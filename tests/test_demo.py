# -*- coding: utf-8 -*-
"""Offline demo tests / 离线演示测试.

Guards the no-key experience so a reviewer can always run the product.
守护免 key 体验，保证评委任何时候都能跑起来。
"""
from __future__ import annotations

import demo
import parsing


def test_build_text_has_four_sections():
    """Demo text must carry all four markers / 演示文本必须包含四个标记."""
    text = demo.build_text({"prompt": "一个女孩在雨夜哭泣，镜头慢慢推近", "model": "seedance", "ratio": "9:16"})
    for mark in ("===SCENE===", "===REASON===", "===PROMPT===", "===CHANGES==="):
        assert mark in text


def test_parse_roundtrip():
    """Demo text parses into the same structure as real output / 演示文本解析结果与真实输出同构."""
    params = {"prompt": "一只橘猫趴在窗台上看雪", "model": "gpt-image", "style": "3D", "ratio": "9:16"}
    text = "".join(demo.stream_text(params, delay=0))
    result = parsing.parse_full(text)
    assert result["scene"]
    assert result["reason"]
    assert "橘猫" in result["prompt"]
    assert result["changes"]


def test_scene_inference():
    """Keyword inference picks a sensible scene / 关键词判定选出合理戏份."""
    assert demo.infer_scene("雨夜追逐，快速奔跑") == "动作戏"
    assert demo.infer_scene("她独自哭泣，很孤独") == "情绪戏"
    assert demo.infer_scene("随便画点什么") == "氛围片段"
    assert demo.infer_scene("随便画点什么", "自定义戏份") == "自定义戏份"


def test_stream_matches_full_parse():
    """Chunked streaming must equal full parse / 分块流式必须与整段解析一致."""
    params = {"prompt": "香水静物，柔和自然光", "model": "seedream", "ratio": "1:1"}
    parser = parsing.SegmentParser()
    events = []
    for chunk in demo.stream_text(params, delay=0):
        events.extend(parser.feed(chunk))
    events.extend(parser.finish())
    done = [e for e in events if e["type"] == "done"][-1]
    assert done["result"] == parsing.parse_full("".join(demo.stream_text(params, delay=0)))
