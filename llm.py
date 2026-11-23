# -*- coding: utf-8 -*-
"""DeepSeek 客户端：同步调用 + 流式生成器，共用同一份请求构造。

界面拿到的永远是结构化事件（meta / delta / done），不再自己切标记。
"""
from __future__ import annotations

import json
import logging
import threading
import time
import uuid

import requests

import config
import demo
import errors
import parsing
import rules

log = logging.getLogger("studio.llm")

# 并发闸门：非阻塞，超限时立刻给可读提示，避免 key 被连点刷爆。
#
# 不能用 threading.Semaphore + 生成器 finally：客户端中途取消/关页面时，
# Starlette 在 threadpool 里迭代同步生成器，不保证调用 gen.close()，
# finally 不跑就会永久泄漏名额（表现为之后所有请求都 busy）。
# 这里改成带心跳的槽位表：正常请求持续续租，僵尸槽位超时自动回收。
_gate_lock = threading.Lock()
_slots: dict[str, tuple[float, float]] = {}  # token -> (创建时间, 最后活跃时间)
SLOT_IDLE_TTL = 30.0                          # 30 秒没有任何上游输出，视为断连残留
SLOT_MAX_TTL = config.REQUEST_TIMEOUT + 30.0  # 单次请求的绝对上限


def _reap(now: float) -> None:
    for token, (born, last) in list(_slots.items()):
        if now - last > SLOT_IDLE_TTL or now - born > SLOT_MAX_TTL:
            del _slots[token]


def acquire_slot() -> str:
    """占用一个改写名额，返回用于释放的 token；超限时抛 BusyError。"""
    now = time.time()
    with _gate_lock:
        _reap(now)
        if len(_slots) >= config.MAX_CONCURRENCY:
            raise errors.BusyError(config.MAX_CONCURRENCY)
        token = uuid.uuid4().hex
        _slots[token] = (now, now)
        return token


def touch_slot(token: str) -> None:
    """收到上游内容时刷新槽位的活跃时间。"""
    with _gate_lock:
        slot = _slots.get(token)
        if slot:
            _slots[token] = (slot[0], time.time())


def release_slot(token: str) -> None:
    with _gate_lock:
        _slots.pop(token, None)


def active_slots() -> int:
    with _gate_lock:
        _reap(time.time())
        return len(_slots)


def _headers() -> dict:
    key = config.api_key()
    if not key:
        raise errors.ConfigError()
    return {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }


def _payload(system: str, prompt: str, stream: bool) -> dict:
    return {
        "model": config.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": "请改写下面这段提示词：\n\n{}".format(prompt)},
        ],
        "temperature": 0.3,
        "stream": stream,
    }


def _iter_sse(resp):
    """逐行解析上游 SSE，只吐增量文本。"""
    for line in resp.iter_lines(decode_unicode=True):
        if isinstance(line, bytes):
            line = line.decode("utf-8", "replace")
        if not line or not line.startswith("data:"):
            continue
        chunk = line[5:].strip()
        if chunk == "[DONE]":
            break
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue
        choices = obj.get("choices") or []
        if not choices:
            continue
        text = (choices[0].get("delta") or {}).get("content")
        if text:
            yield text


def _system(params: dict) -> str:
    return rules.build_system(
        params["model"],
        params.get("scene_type", ""),
        params.get("style", ""),
        params.get("ratio", ""),
        params.get("duration", "自动"),
    )


def rewrite_stream_events(params: dict, token: str | None = None):
    """流式：产出 parsing.SegmentParser 的事件，异常向上抛给路由统一翻译。

    token 由路由层提前申请并挂到响应的 background 上；这里再 release 一次
    是幂等的，正常结束时可以立刻归还名额，不必等 background。
    """
    token = token or acquire_slot()
    try:
        parser = parsing.SegmentParser()
        if config.demo_mode():
            # 离线演示：复用同一套解析器，保证流式事件与真实模式逐字一致。
            # Offline demo: reuse the same parser so streaming events are byte-for-byte
            # identical to the real path.
            for text in demo.stream_text(params):
                for event in parser.feed(text):
                    yield event
        else:
            with requests.post(
                config.DEEPSEEK_BASE + "/chat/completions",
                headers=_headers(),
                json=_payload(_system(params), params["prompt"], True),
                stream=True,
                timeout=(10, config.REQUEST_TIMEOUT),
            ) as resp:
                if resp.status_code != 200:
                    raise errors.from_response(resp.status_code, resp.text[:300])
                for text in _iter_sse(resp):
                    touch_slot(token)
                    for event in parser.feed(text):
                        yield event
        for event in parser.finish():
            yield event
    finally:
        release_slot(token)


def rewrite_sync(params: dict):
    """同步：兼容旧调用方，返回 (结构化结果, usage)。"""
    token = acquire_slot()
    try:
        if config.demo_mode():
            # 离线演示：整段构造后走同一解析器；usage 留空表示未消耗真实 token。
            # Offline demo: build the full text through the same parser; empty usage
            # signals that no real tokens were consumed.
            return parsing.parse_full("".join(demo.stream_text(params))), {}
        resp = requests.post(
            config.DEEPSEEK_BASE + "/chat/completions",
            headers=_headers(),
            json=_payload(_system(params), params["prompt"], False),
            timeout=(10, config.REQUEST_TIMEOUT),
        )
        if resp.status_code != 200:
            raise errors.from_response(resp.status_code, resp.text[:300])
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
        return parsing.parse_full(content), body.get("usage", {})
    finally:
        release_slot(token)
