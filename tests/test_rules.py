# -*- coding: utf-8 -*-
"""规则加载器测试：热加载与未知输入的处理。"""
from __future__ import annotations

import json
import time


def _write_rules(path, models: list[str], scene: str) -> None:
    """写一份最小但结构完整的规则文件。"""
    # 真实的 rules_data.json 里 models 是 {模型ID: 该模型的系统提示词} 字典
    payload = {
        "models": {m: "系统提示词-" + m for m in models},
        "model_labels": {m: m.upper() for m in models},
        "model_hints": {m: "hint-" + m for m in models},
        "video_models": [m for m in models if "video" in m],
        "scene_types": {"剧情": scene},
        "styles": {"写实": "写实风格描述"},
        "ratios": ["16:9", "9:16"],
        "ratio_composition": {"16:9": "横向构图", "9:16": "竖向构图"},
        "durations": ["5", "10"],
        "camera_language": "运镜要求",
        "video_output_format": "视频输出格式",
        "image_output_format": "图片输出格式",
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_rules_load_from_file(tmp_path, monkeypatch):
    import config
    import rules

    target = tmp_path / "rules_data.json"
    _write_rules(target, ["video-a", "image-b"], "初始戏份规则")
    monkeypatch.setattr(config, "RULES_FILE", target)
    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})

    assert list(rules.MODELS) == ["video-a", "image-b"]
    assert rules.VIDEO_MODELS == {"video-a"}
    assert "初始戏份规则" in rules.auto_instruction()


def test_hot_reload_on_mtime_change(tmp_path, monkeypatch):
    """改了 rules_data.json 后不用重启，下次读取自动生效。"""
    import config
    import rules

    target = tmp_path / "rules_data.json"
    _write_rules(target, ["old-model"], "旧规则")
    monkeypatch.setattr(config, "RULES_FILE", target)
    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})
    assert list(rules.MODELS) == ["old-model"]

    _write_rules(target, ["new-model"], "新规则")
    # 确保 mtime 一定变化（文件系统分辨率可能是整秒）
    future = time.time() + 10
    import os
    os.utime(target, (future, future))

    assert list(rules.MODELS) == ["new-model"]
    assert "新规则" in rules.auto_instruction()


def test_build_system_for_video_includes_duration_and_camera(tmp_path, monkeypatch):
    import config
    import rules

    target = tmp_path / "rules_data.json"
    _write_rules(target, ["video-a"], "戏份规则")
    monkeypatch.setattr(config, "RULES_FILE", target)
    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})

    system = rules.build_system("video-a", scene_type="剧情", style="写实", ratio="9:16", duration="8")
    assert "目标总时长：8 秒" in system
    assert "运镜要求" in system
    assert "视频输出格式" in system
    assert "图片输出格式" not in system


def test_build_system_for_image_uses_image_format(tmp_path, monkeypatch):
    import config
    import rules

    target = tmp_path / "rules_data.json"
    _write_rules(target, ["image-b", "video-a"], "戏份规则")
    monkeypatch.setattr(config, "RULES_FILE", target)
    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})

    system = rules.build_system("image-b", scene_type="剧情")
    assert "图片输出格式" in system
    assert "视频输出格式" not in system


def test_unknown_model_raises(tmp_path, monkeypatch):
    import config
    import rules

    target = tmp_path / "rules_data.json"
    _write_rules(target, ["only-model"], "戏份规则")
    monkeypatch.setattr(config, "RULES_FILE", target)
    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})

    try:
        rules.build_system("不存在的模型")
    except ValueError as exc:
        assert "未知模型" in str(exc)
    else:
        raise AssertionError("未知模型应该抛 ValueError")


def test_options_shape(tmp_path, monkeypatch):
    import config
    import rules

    target = tmp_path / "rules_data.json"
    _write_rules(target, ["video-a", "image-b"], "戏份规则")
    monkeypatch.setattr(config, "RULES_FILE", target)
    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})

    options = rules.options()
    assert [m["value"] for m in options["models"]] == ["video-a", "image-b"]
    assert options["models"][0]["video"] is True
    assert options["models"][1]["video"] is False
    assert options["scene_types"] == ["剧情"]
