# -*- coding: utf-8 -*-
"""规则加载器：知识内容放在 rules_data.json，改完不用重启服务。

对外保持旧版接口（MODELS / SCENE_TYPES / build_system ...），
但这些属性通过 __getattr__ 动态读取，热加载后立刻生效。
"""
from __future__ import annotations

import json
import threading

import config

_lock = threading.Lock()
_state: dict = {"mtime": None, "data": None}

_PUBLIC = {
    "SCENE_TYPES": "scene_types",
    "STYLES": "styles",
    "RATIOS": "ratios",
    "DURATIONS": "durations",
    "RATIO_COMPOSITION": "ratio_composition",
    "CAMERA_LANGUAGE": "camera_language",
    "MODELS": "models",
    "MODEL_LABELS": "model_labels",
    "MODEL_HINTS": "model_hints",
    "VIDEO_MODELS": "video_models",
    "VIDEO_OUTPUT_FORMAT": "video_output_format",
    "IMAGE_OUTPUT_FORMAT": "image_output_format",
}


def _load_if_changed(force: bool = False) -> dict:
    """按文件 mtime 热加载；读失败时保留上一份好数据，不让页面挂掉。"""
    with _lock:
        try:
            mtime = config.RULES_FILE.stat().st_mtime
        except FileNotFoundError as exc:
            raise RuntimeError("找不到 rules_data.json") from exc
        if force or _state["data"] is None or _state["mtime"] != mtime:
            raw = config.RULES_FILE.read_text(encoding="utf-8")
            _state["data"] = json.loads(raw)
            _state["mtime"] = mtime
        return _state["data"]


def reload_rules() -> dict:
    return _load_if_changed(force=True)


def data() -> dict:
    return _load_if_changed()


def __getattr__(name: str):
    if name in _PUBLIC:
        value = data()[_PUBLIC[name]]
        return set(value) if name == "VIDEO_MODELS" else value
    if name == "AUTO_SCENE_INSTRUCTION":
        return auto_instruction()
    raise AttributeError(name)


def auto_instruction() -> str:
    d = data()
    return (
        "用户没有指定戏份类型。请先根据用户输入的内容，判断它属于下面六类中的哪一类，"
        "然后只按那一类的节奏、景别、机位、运镜来写：\n\n"
        + "\n\n".join("「{}」\n{}".format(k, v) for k, v in d["scene_types"].items())
    )


def is_video(model: str) -> bool:
    return model in set(data()["video_models"])


def options() -> dict:
    """前端下拉选项的来源，与规则文本保持一致。"""
    d = data()
    videos = set(d["video_models"])
    return {
        "models": [
            {
                "value": key,
                "label": d["model_labels"].get(key, key),
                "hint": d["model_hints"].get(key, ""),
                "video": key in videos,
            }
            for key in d["models"]
        ],
        "scene_types": list(d["scene_types"].keys()),
        "styles": list(d["styles"].keys()),
        "ratios": d["ratios"],
        "durations": d["durations"],
    }


def build_system(model: str, scene_type: str = "", style: str = "", ratio: str = "", duration: str = "自动") -> str:
    d = data()
    if model not in d["models"]:
        raise ValueError("未知模型：{}".format(model))

    parts = [d["models"][model]]
    if scene_type in d["scene_types"]:
        parts.append("本次戏份设定：\n" + d["scene_types"][scene_type])
    else:
        parts.append(auto_instruction())
    if style in d["styles"]:
        parts.append("画风「{}」：{}".format(style, d["styles"][style]))
    if ratio in d["ratio_composition"]:
        parts.append("画面比例「{}」：{}".format(ratio, d["ratio_composition"][ratio]))

    video = model in set(d["video_models"])
    if video and duration and duration != "自动":
        parts.append("目标总时长：{} 秒，按这个时长逐秒拆解分镜。".format(duration))
    if video:
        parts.append(d["camera_language"])
    parts.append(d["video_output_format"] if video else d["image_output_format"])
    return "\n\n".join(parts)
