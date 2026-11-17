# -*- coding: utf-8 -*-
"""解析器测试：这是整个项目最容易出错的部分，重点验证跨 chunk 的标记边界。"""
from __future__ import annotations

import pytest

import parsing


SAMPLE = """===SCENE===
城市天台的日落
===REASON===
用暖色调铺垫离别的安静
===PROMPT===
一位女孩背对镜头望向远处的城市，晚风掀起她的长发，
金色光线勾出轮廓，镜头缓慢后拉。
===CHANGES===
- 加了慢镜头
- 调整成金色光线
2. 补了环境音
"""


def _feed(parser: parsing.SegmentParser, chunks: list[str]) -> list[dict]:
    events: list[dict] = []
    for chunk in chunks:
        events.extend(parser.feed(chunk))
    events.extend(parser.finish())
    return events


def _done(events: list[dict]) -> dict:
    done = [e for e in events if e["type"] == "done"]
    assert len(done) == 1, "finish 应恰好产出一条 done"
    return done[0]["result"]


def test_parse_full_happy_path():
    """一次性解析：四段都归位，改动说明去掉列表符号。"""
    result = parsing.parse_full(SAMPLE)
    assert result["scene"] == "城市天台的日落"
    assert result["reason"] == "用暖色调铺垫离别的安静"
    assert "女孩背对镜头" in result["prompt"]
    assert result["changes"] == ["加了慢镜头", "调整成金色光线", "补了环境音"]


@pytest.mark.parametrize("size", [1, 2, 3, 5, 7, 13, 64])
def test_streaming_matches_full_at_every_chunk_size(size):
    """核心回归：无论标记被拆成多碎，流式结果必须与整段解析一致。

    这是之前漏字 / 丢字段 bug 的防护网—— size=1 时 '===PROMPT===' 会被
    逐字符喂入，正好覆盖标记横跨两个 chunk 的最坏情况。
    """
    chunks = [SAMPLE[i:i + size] for i in range(0, len(SAMPLE), size)]
    streamed = _done(_feed(parsing.SegmentParser(), chunks))
    assert streamed == parsing.parse_full(SAMPLE)


def test_meta_fires_once_when_prompt_enters():
    """meta 在进入正文段时发出，且只发一次，不能重复。"""
    events = _feed(parsing.SegmentParser(), [SAMPLE[:40], SAMPLE[40:120], SAMPLE[120:]])
    metas = [e for e in events if e["type"] == "meta"]
    assert len(metas) == 1
    assert metas[0]["scene"] == "城市天台的日落"
    assert metas[0]["reason"] == "用暖色调铺垫离别的安静"


def test_delta_only_in_prompt_section():
    """delta 只来自正文段，且逐字拼接后与最终 prompt 完全一致（不漏字）。"""
    chunks = [SAMPLE[i:i + 2] for i in range(0, len(SAMPLE), 2)]
    events = _feed(parsing.SegmentParser(), chunks)
    delta_text = "".join(e["text"] for e in events if e["type"] == "delta")
    result = _done(events)
    assert delta_text.strip() == result["prompt"].strip()
    assert "日落" not in delta_text  # 戏份内容不能混进正文增量


def test_no_marks_falls_back_to_whole_text():
    """模型完全不按格式输出时，整段当提示词，一点内容都不丢。"""
    raw = "这是一段没有四段标记的自由文本，应该原样成为提示词。"
    events = _feed(parsing.SegmentParser(), [raw[i:i + 3] for i in range(0, len(raw), 3)])
    result = _done(events)
    assert result["prompt"] == raw
    assert result["scene"] == ""
    assert result["changes"] == []


def test_mark_prefix_held_until_resolved():
    """结尾是标记前缀时先扣住，不提前吐给正文，等下一个 chunk 判定。"""
    parser = parsing.SegmentParser()
    first = parser.feed("===SCENE===\n近景\n===PRO")
    # "===PRO" 是 ===PROMPT=== 的前缀，必须被扣在 buffer 里
    assert parser.buffer == "===PRO"
    assert all(e["type"] != "meta" for e in first)

    second = parser.feed("MPT===\n正文")
    events = second + parser.finish()
    result = _done(events)
    assert result["scene"] == "近景"
    assert result["prompt"] == "正文"


def test_code_fence_is_stripped():
    """模型爱用 ``` 包住正文，解析器要去掉围栏。"""
    text = "===PROMPT===\n```\n一段被围栏包住的文字\n```\n"
    assert parsing.parse_full(text)["prompt"] == "一段被围栏包住的文字"


def test_parse_changes_handles_common_bullets():
    lines = "- 第一项\n• 第二项\n* 第三项\n1. 第四项\n2、第五项\n3) 第六项\n\n  第七项  \n"
    assert parsing.parse_changes(lines) == [
        "第一项", "第二项", "第三项", "第四项", "第五项", "第六项", "第七项",
    ]


def test_empty_changes():
    assert parsing.parse_changes("") == []
    assert parsing.parse_changes(None) == []
