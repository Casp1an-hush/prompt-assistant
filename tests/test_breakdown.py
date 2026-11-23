# -*- coding: utf-8 -*-
"""剧本拆解测试。"""

import json

import pytest

import breakdown
import rules

SCRIPT = """第一集
1-1
林晚推门冲上天台，雨水顺着头发往下淌，栏杆边站着一个人。

1-2
陈默回过头，说了句话。"""

MODEL_JSON = {
    "characters": [{
        "name": "林晚", "label": "主状态", "gender": "女", "age": "24",
        "personality": "表面温和", "appearance": "身高 165cm，鹅蛋脸",
        "costume": "深栗色长发及腰，米白高领针织衫", "anchors": ["左眼下有小痣"],
        "note": "第1集 1-1、1-2",
    }],
    "scenes": [{
        "name": "天台", "time": "雨夜", "era": "当代城市",
        "architecture": "水泥地面，锈蚀栏杆", "lighting": "霓虹自下而上", "note": "第1集 1-1",
    }],
    "props": [{
        "name": "怀表", "material": "黄铜", "size": "掌心大小",
        "color": "暗金", "detail": "表盖有划痕", "note": "第1集 1-2",
    }],
}


def test_validate_rejects_short_text():
    codes = [p["code"] for p in breakdown.validate_script("太短了")]
    assert "too_short" in codes


def test_validate_rejects_text_without_scene_numbers():
    text = "这是一个很长但没有分场的段落。" * 5
    codes = [p["code"] for p in breakdown.validate_script(text)]
    assert "no_episode" in codes and "no_scenes" in codes


def test_validate_rejects_oversized_text():
    text = "第一集\n1-1\n" + "台词。" * 12000
    codes = [p["code"] for p in breakdown.validate_script(text)]
    assert "too_long" in codes


def test_validate_accepts_segmented_script():
    assert breakdown.validate_script(SCRIPT) == []


def test_segments_finds_markers():
    assert breakdown.segments(SCRIPT) == ["第一集 1-1", "第一集 1-2"]


def test_segments_follow_episode_changes():
    text = "第一集\n1-1\n正文正文正文\n1-2\n正文\n\n第二集\n2-1\n正文正文"
    assert breakdown.segments(text) == ["第一集 1-1", "第一集 1-2", "第二集 2-1"]


def test_segments_label_scenes_without_episode():
    """缺集名时仍能解析出场次，只是没有集名前缀。"""
    assert breakdown.segments("1-1\n正文\n1-2\n正文") == ["1-1", "1-2"]


def test_validate_rejects_scene_without_episode_line():
    """集名必须单独一行。"""
    text = "1-1\n" + "正文。" * 20
    codes = [p["code"] for p in breakdown.validate_script(text)]
    assert "no_episode" in codes and "no_scenes" not in codes


def test_validate_requires_scene_number_on_its_own_line():
    """场次号混在正文行里不算分段。"""
    text = "第一集 1-1 林晚冲上天台。" + "正文。" * 20
    codes = [p["code"] for p in breakdown.validate_script(text)]
    assert "no_scenes" in codes


def test_parse_accepts_plain_json():
    result = breakdown.parse(json.dumps(MODEL_JSON, ensure_ascii=False))
    assert result["characters"][0]["name"] == "林晚"
    assert result["characters"][0]["anchors"] == ["左眼下有小痣"]


def test_parse_accepts_fenced_json():
    text = "```json\n" + json.dumps(MODEL_JSON, ensure_ascii=False) + "\n```"
    assert breakdown.parse(text)["scenes"][0]["name"] == "天台"


def test_parse_raises_on_garbage():
    with pytest.raises(breakdown.BreakdownError):
        breakdown.parse("这不是 JSON")


def test_character_prompt_has_layout_and_anchor():
    result = breakdown.parse(json.dumps(MODEL_JSON, ensure_ascii=False))
    breakdown.attach_prompts(result, "2D")
    prompt = result["characters"][0]["prompt"]
    assert rules.STYLE_ANCHORS["2D"] in prompt
    assert "左侧为正面头部特写" in prompt
    assert "全身三视图" in prompt
    assert "林晚" in prompt


def test_every_style_anchor_is_distinct():
    anchors = list(rules.STYLE_ANCHORS.values())
    assert len(anchors) == len(set(anchors))
    for anchor in anchors:
        assert len(anchor) > 30


def test_prompts_differ_between_styles():
    card = breakdown.parse(json.dumps(MODEL_JSON, ensure_ascii=False))["characters"][0]
    a = breakdown.character_prompt(card, "2D")
    b = breakdown.character_prompt(card, "次世代CG")
    assert a != b


def test_markdown_contains_sections():
    result = breakdown.parse(json.dumps(MODEL_JSON, ensure_ascii=False))
    breakdown.attach_prompts(result, "3D")
    text = breakdown.to_markdown(result, "3D")
    assert "## 人物模卡" in text
    assert "## 场景图" in text
    assert "## 道具图" in text
    assert "林晚" in text


def test_demo_result_is_labelled():
    result = breakdown.demo_result(SCRIPT, "国漫")
    assert "演示" in result["characters"][0]["name"]
    assert "演示" in result["characters"][0]["prompt"] or "演示" in result["characters"][0]["appearance"]
