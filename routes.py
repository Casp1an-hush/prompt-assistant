# -*- coding: utf-8 -*-
"""全部 HTTP 接口。按职责分组，以后加模块直接新增 router 即可。"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

import config
import breakdown
import errors
import llm
import rules
import store

log = logging.getLogger("studio.api")
router = APIRouter(prefix="/api")


class RewriteRequest(BaseModel):
    prompt: str
    model: str
    scene_type: str = ""
    style: str = ""
    ratio: str = ""
    duration: str = "自动"


def _validate(req: RewriteRequest):
    if not req.prompt.strip():
        return None, JSONResponse({"error": "请先写点什么，再交给它改写。", "code": "empty"}, status_code=400)
    if req.model not in rules.MODELS:
        return None, JSONResponse(
            {"error": "未知模型：{}".format(req.model), "code": "unknown_model"}, status_code=400
        )
    return req.model_dump(), None


def _sse(event: str, data: dict) -> str:
    return "event: {}\ndata: {}\n\n".format(event, json.dumps(data, ensure_ascii=False))


def _record(rid: str, params: dict, result: dict | None, started: float, status: str,
            error: str = "", cached: bool = False, usage: dict | None = None) -> dict:
    usage = usage or {}
    payload = {
        "id": rid,
        "created_at": started,
        "model": params.get("model"),
        "scene_type": params.get("scene_type", ""),
        "style": params.get("style", ""),
        "ratio": params.get("ratio", ""),
        "duration": params.get("duration", "自动"),
        "input": params.get("prompt", ""),
        "scene": (result or {}).get("scene", ""),
        "reason": (result or {}).get("reason", ""),
        "result_prompt": (result or {}).get("prompt", ""),
        "changes_json": json.dumps((result or {}).get("changes", []), ensure_ascii=False),
        "latency_ms": int((time.time() - started) * 1000),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "status": status,
        "error": error,
        "cached": int(cached),
    }
    try:
        store.log_request(payload)
    except Exception:
        log.exception("写请求日志失败（不影响本次改写）")
    return payload


# ---------------------------------------------------------------- 元信息

@router.get("/options")
def options():
    return {
        **rules.options(),
        "features": {
            "history": True,
            "templates": False,
            "favorites": False,
            "compare": False,
        },
        "backgrounds": sorted(p.name for p in (config.STATIC_DIR / "backgrounds").glob("*.jpeg"))
        if (config.STATIC_DIR / "backgrounds").exists() else [],
    }


@router.get("/health")
def health():
    return {
        "status": "ok",
        "version": config.VERSION,
        "dev_mode": config.DEV_MODE,
        "rules_loaded": len(rules.MODELS),
        "key_configured": bool(config.api_key()),
        "demo_mode": config.demo_mode(),          # 无 key 时为离线演示模式 / offline demo when no key
        "active_requests": llm.active_slots(),   # 当前占用的并发名额
    }


@router.post("/admin/reload")
def reload_rules():
    if not config.DEV_MODE:
        return JSONResponse({"error": "仅开发模式可热重载规则"}, status_code=403)
    data = rules.reload_rules()
    return {"reloaded": True, "models": len(data["models"]), "scene_types": len(data["scene_types"])}


# ---------------------------------------------------------------- 改写

@router.post("/stream")
def stream(req: RewriteRequest):
    """SSE 流式改写：meta → delta×N → done / error。"""
    params, error = _validate(req)
    if error:
        return error
    key = store.cache_key(params)
    cached = store.cache_get(key)

    # 名额在进入流式响应之前申请。客户端断连时生成器 finally 未必执行，
    # 所以释放同时挂在响应 background 上，再由 llm 的槽位超时兜底。
    token = None
    if not cached:
        try:
            token = llm.acquire_slot()
        except errors.BusyError as exc:
            err = errors.from_exception(exc)
            return JSONResponse({"error": err.message, **err.as_dict()}, status_code=err.http_status)

    def generate():
        rid = store.new_id()
        started = time.time()
        yield _sse("start", {"request_id": rid, "cached": bool(cached)})

        if cached:
            log.info("rid=%s 命中缓存 model=%s", rid, params["model"])
            yield _sse("meta", {"scene": cached.get("scene", ""), "reason": cached.get("reason", "")})
            yield _sse("done", {
                **cached,
                "request_id": rid,
                "cached": True,
                "latency_ms": 0,
            })
            return

        try:
            final = None
            for event in llm.rewrite_stream_events(params, token):
                kind = event["type"]
                if kind == "delta":
                    yield _sse("delta", {"text": event["text"]})
                elif kind == "meta":
                    yield _sse("meta", {"scene": event["scene"], "reason": event["reason"]})
                elif kind == "done":
                    final = event["result"]
                    store.cache_put(key, final)
                    latency = int((time.time() - started) * 1000)
                    _record(rid, params, final, started, "ok", cached=False)
                    log.info(
                        "rid=%s model=%s scene=%s latency=%dms chars=%d",
                        rid, params["model"], final.get("scene", ""), latency, len(final.get("prompt", "")),
                    )
                    yield _sse("done", {**final, "request_id": rid, "cached": False, "latency_ms": latency})
            if final is None:
                raise errors.StudioError("empty_result", "这次没拿到改写结果，再试一次。", True, 502)
        except Exception as exc:  # noqa: BLE001
            err = errors.from_exception(exc)
            log.exception("rid=%s 改写失败 code=%s", rid, err.code)
            _record(rid, params, None, started, "error", error=err.message)
            yield _sse("error", err.as_dict())

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
        background=BackgroundTask(llm.release_slot, token) if token else None,
    )


@router.post("/rewrite")
def rewrite(req: RewriteRequest):
    """同步改写：保留给脚本调用与降级使用，返回结构化的四个字段。"""
    params, error = _validate(req)
    if error:
        return error
    rid = store.new_id()
    started = time.time()
    key = store.cache_key(params)
    cached = store.cache_get(key)
    if cached:
        return {**cached, "request_id": rid, "cached": True, "latency_ms": 0}

    try:
        result, usage = llm.rewrite_sync(params)
    except Exception as exc:  # noqa: BLE001
        err = errors.from_exception(exc)
        log.exception("rid=%s 同步改写失败 code=%s", rid, err.code)
        _record(rid, params, None, started, "error", error=err.message)
        return JSONResponse({"error": err.message, **err.as_dict()}, status_code=err.http_status)

    store.cache_put(key, result)
    _record(rid, params, result, started, "ok", usage=usage)
    latency = int((time.time() - started) * 1000)
    log.info("rid=%s model=%s scene=%s latency=%dms", rid, params["model"], result.get("scene", ""), latency)
    return {**result, "request_id": rid, "cached": False, "latency_ms": latency, "usage": usage}


# ---------------------------------------------------------------- 剧本拆解

class BreakdownRequest(BaseModel):
    text: str
    style: str = ""


@router.post("/breakdown")
def breakdown_script(req: BreakdownRequest):
    """按集-场分段的长文本 → 人物模卡 / 场景图 / 道具图。"""
    problems = breakdown.validate_script(req.text)
    if problems:
        return JSONResponse(
            {
                "error": breakdown.problem_message(problems[0]),
                "problems": problems,
                "code": problems[0]["code"],
            },
            status_code=400,
        )

    started = time.time()
    try:
        result, usage = llm.breakdown_sync(req.text, req.style)
    except Exception as exc:  # noqa: BLE001
        err = errors.from_exception(exc)
        log.exception("剧本拆解失败 code=%s", err.code)
        return JSONResponse({"error": err.message, **err.as_dict()}, status_code=err.http_status)

    result = breakdown.attach_prompts(result, req.style)
    latency = int((time.time() - started) * 1000)
    log.info(
        "breakdown chars=%d style=%s chars_cards=%d scenes=%d props=%d latency=%dms",
        len(req.text), req.style,
        len(result["characters"]), len(result["scenes"]), len(result["props"]), latency,
    )
    return {
        **result,
        "style": req.style,
        "demo": config.demo_mode(),
        "markdown": breakdown.to_markdown(result, req.style),
        "segments": breakdown.segments(req.text),
        "latency_ms": latency,
        "usage": usage,
    }


class MarkdownRequest(BaseModel):
    characters: list = []
    scenes: list = []
    props: list = []
    style: str = ""


@router.post("/breakdown/markdown")
def breakdown_markdown(req: MarkdownRequest):
    """把（可能已被用户修改过的）卡片重新拼成 Markdown。"""
    result = {
        "characters": req.characters,
        "scenes": req.scenes,
        "props": req.props,
    }
    return {"markdown": breakdown.to_markdown(result, req.style)}


# ---------------------------------------------------------------- 历史

@router.get("/history")
def history(limit: int = 20):
    return {"items": store.history(limit)}


@router.get("/history/{item_id}")
def history_detail(item_id: str):
    item = store.history_get(item_id)
    if not item:
        return JSONResponse({"error": "找不到这条记录"}, status_code=404)
    return item


@router.delete("/history/{item_id}")
def history_delete(item_id: str):
    if not store.history_delete(item_id):
        return JSONResponse({"error": "找不到这条记录"}, status_code=404)
    return {"deleted": True}


@router.delete("/history")
def history_clear():
    return {"deleted": store.history_clear()}
