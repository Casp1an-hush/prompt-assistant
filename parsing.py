# -*- coding: utf-8 -*-
"""标记文本解析器：流式状态机与整段解析共用同一套逻辑。

模型按 ===SCENE=== / ===REASON=== / ===PROMPT=== / ===CHANGES=== 分段输出。
流式下标记可能被拆进两个 chunk，所以不能直接 split：留一个可能是标记前缀的尾巴。
"""
from __future__ import annotations

import re

MARKS = {
    "SCENE": "===SCENE===",
    "REASON": "===REASON===",
    "PROMPT": "===PROMPT===",
    "CHANGES": "===CHANGES===",
}
_SECTION_BY_MARK = {mark: name.lower() for name, mark in MARKS.items()}
_MAX_MARK_LEN = max(len(m) for m in MARKS.values())
_BUCKETS = ("preamble", "scene", "reason", "prompt", "changes")
_CHANGE_PREFIX = re.compile(r"^\s*(?:[-•*]|\d+[.、)])\s*")


def _clean(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
    return text


def parse_changes(text: str) -> list[str]:
    """改动说明统一解析成数组，前端不再自己 split。"""
    result = []
    for line in (text or "").splitlines():
        line = _CHANGE_PREFIX.sub("", line).strip()
        if line:
            result.append(line)
    return result


def _hold_suffix(buf: str) -> tuple[str, str]:
    """返回（可安全输出的部分，需要留到下一个 chunk 的标记前缀）。"""
    for n in range(min(len(buf), _MAX_MARK_LEN - 1), 0, -1):
        tail = buf[-n:]
        if any(mark.startswith(tail) for mark in MARKS.values()):
            return buf[:-n], tail
    return buf, ""


class SegmentParser:
    """逐 chunk 喂入，产出 meta / delta / done 事件。"""

    def __init__(self):
        self.section = "preamble"
        self.buffer = ""
        self.parts = {key: [] for key in _BUCKETS}
        self._meta_sent = False
        self.saw_mark = False

    def _append(self, text: str) -> None:
        if text:
            self.parts[self.section].append(text)

    def _meta_event(self):
        scene = _clean("".join(self.parts["scene"]))
        reason = _clean("".join(self.parts["reason"]))
        if not self._meta_sent and scene:
            self._meta_sent = True
            return {"type": "meta", "scene": scene, "reason": reason}
        return None

    def feed(self, chunk: str) -> list[dict]:
        events: list[dict] = []
        if not chunk:
            return events
        self.buffer += chunk

        while True:
            hit = None
            for mark, section in _SECTION_BY_MARK.items():
                idx = self.buffer.find(mark)
                if idx != -1 and (hit is None or idx < hit[0]):
                    hit = (idx, mark, section)
            if hit is None:
                break

            idx, mark, section = hit
            before = self.buffer[:idx]
            leaving = self.section
            self._append(before)
            self.section = section
            self.saw_mark = True
            self.buffer = self.buffer[idx + len(mark):]

            # 标记前的正文也要作为增量发出，否则分块边界会漏字
            if leaving == "prompt" and before:
                events.append({"type": "delta", "text": before})
            # 进入正文段时戏份与依据都已确定，尽早通知前端
            if section == "prompt":
                meta = self._meta_event()
                if meta:
                    events.append(meta)

        emit, hold = _hold_suffix(self.buffer)
        if emit:
            self._append(emit)
            self.buffer = hold
            if self.section == "prompt":
                events.append({"type": "delta", "text": emit})
        return events

    def finish(self) -> list[dict]:
        tail = self.buffer
        self._append(tail)
        self.buffer = ""

        scene = _clean("".join(self.parts["scene"]))
        reason = _clean("".join(self.parts["reason"]))
        prompt = _clean("".join(self.parts["prompt"]))
        changes = _clean("".join(self.parts["changes"]))
        preamble = _clean("".join(self.parts["preamble"]))

        if not self.saw_mark:
            # 模型完全没按格式输出：整段当提示词，至少不丢内容
            prompt = _clean("\n".join(x for x in (preamble, prompt, changes) if x))
        elif not prompt and preamble:
            prompt = preamble

        result = {
            "scene": scene,
            "reason": reason,
            "prompt": prompt,
            "changes": parse_changes(changes),
        }
        events = []
        if self.section == "prompt" and tail:
            events.append({"type": "delta", "text": tail})
        meta = self._meta_event()
        if meta:
            events.append(meta)
        events.append({"type": "done", "result": result})
        return events


def parse_full(content: str) -> dict:
    """非流式接口用：一次性解析完整文本。"""
    parser = SegmentParser()
    parser.feed(content)
    return parser.finish()[-1]["result"]
