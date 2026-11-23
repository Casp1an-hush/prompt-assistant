# -*- coding: utf-8 -*-
"""Offline demo generator (no API key required) / 离线演示生成器（无需 API key）.

Emits the same four-section text as the real model so the entire pipeline —
streaming, SegmentParser, scene inference display, history — runs unchanged.
A reviewer with no DeepSeek key can still experience the full product.
输出与真实模型相同的四段文本，让流式、解析器、戏份展示、历史等整条链路
原样运行。没有 DeepSeek key 的评委也能完整体验产品。

Everything is deterministic and local: no network, no secrets, no user data
leaving the machine. The sample is clearly labelled as a demo in the UI.
全部内容确定且本地生成：不联网、不需要密钥、不上传任何用户数据。
界面会明确标注这是演示内容。
"""
from __future__ import annotations

import re
import time

# Scene vocabulary reused for lightweight, offline inference / 轻量离线判定所用的戏份词表
_SCENE_HINTS = [
    ("动作戏", ("追", "逃", "打", "跑", "跳", "战斗", "追逐", "chase", "fight")),
    ("情绪戏", ("哭", "笑", "孤独", "思念", "拥抱", "眼泪", "cry", "lonely")),
    ("日常切片", ("窗台", "咖啡", "清晨", "午后", "餐桌", "morning", "coffee")),
    ("产品静物", ("香水", "产品", "静物", "台面", "展示", "product", "bottle")),
]

_STYLE_LABEL = {
    "2D": "2D 赛璐璐动画风",
    "3D": "3D 写实渲染风",
    "真人": "真人电影质感",
    "水墨": "东方水墨写意风",
    "像素": "像素游戏风",
}


def infer_scene(prompt: str, override: str = "") -> str:
    """Pick a scene label from keywords (offline stand-in for model inference).
    根据关键词挑选戏份标签，是模型判定在离线模式下的替身。
    """
    if override:
        return override
    text = prompt.lower()
    for label, words in _SCENE_HINTS:
        if any(w in text for w in words):
            return label
    return "氛围片段"


def build_text(params: dict) -> str:
    """Build the four-section raw text fed to SegmentParser / 构造喂给解析器的四段原文."""
    prompt = (params.get("prompt") or "").strip()
    scene = infer_scene(prompt, params.get("scene_type", ""))
    style = _STYLE_LABEL.get(params.get("style", ""), params.get("style", "") or "柔和的写实风格")
    ratio = params.get("ratio", "16:9") or "16:9"
    duration = params.get("duration", "自动")
    model = params.get("model", "seedance")

    # Keep the user's own words visible so the demo feels connected to the input.
    # 保留用户自己写的词，让演示看起来与输入确实相关。
    subject = re.split(r"[，。！？,\.!?]", prompt)[0][:24] or "画面中的主体"

    video = "video" in model or model in ("seedance", "minimax", "h3")
    frames = _video_storyboard(subject, scene, video, duration) if video else _image_plan(subject, scene)

    return (
        "===SCENE===\n" + scene + "\n"
        + "===REASON===\n" + _reason(scene, ratio, video) + "\n"
        + "===PROMPT===\n" + style + "。\n\n"
        + "【参考图占位】\n" + _refs(subject) + "\n\n"
        + "【主体与场景】\n" + _subject_block(subject, scene) + "\n\n"
        + (frames + "\n\n" if frames else "")
        + "【全局约束】\n" + _constraints(ratio, video) + "\n"
        + "===CHANGES===\n" + _changes(scene, ratio) + "\n"
    )


def _video_storyboard(subject: str, scene: str, video: bool, duration: str) -> str:
    beats = [
        ("0-1s", "中景", "建立场景，主体进入画面", "环境底噪、轻微空气声"),
        ("1-2s", "近景", "主体开始动作，镜头缓慢推进", "动作细节声"),
        ("2-3s", "特写", "抓住关键细节，情绪或冲突升级", "主体声、节奏加强"),
        ("3-4s", "中景", "动作延续，光线随镜头变化", "环境声回环"),
    ]
    lines = ["【分镜】"]
    for t, shot, action, sound in beats:
        lines.append("[{}]：{}，{} — {}；<{}>".format(t, shot, "侧机位" if scene == "动作戏" else "平视", action, sound))
    lines.append("（演示样例：真实模式会按 {} 时长扩展为逐秒分镜）".format(duration))
    return "\n".join(lines)


def _image_plan(subject: str, scene: str) -> str:
    return "\n".join([
        "【构图】",
        "主体居中偏左，留出呼吸感；前景轻虚化，背景层次分明。",
        "（演示样例：真实模式会针对目标模型输出专属构图与光线方案）",
    ])


def _reason(scene: str, ratio: str, video: bool) -> str:
    kind = "视频" if video else "图片"
    return "离线演示判定：{}。按 {} 的 {} 需求组织镜头、光线与声音线索。".format(scene, ratio, kind)


def _refs(subject: str) -> str:
    return "@图片1 = {} 的主体参考，锁定外形与色彩\n@图片2 = 场景与光线参考，锁定氛围".format(subject)


def _subject_block(subject: str, scene: str) -> str:
    return "{}：细节清晰，动作自然；整体服务于「{}」的叙事基调。".format(subject, scene)


def _constraints(ratio: str, video: bool) -> str:
    extra = "动作连贯、镜头过渡自然；" if video else ""
    return "{}严格遵循 {} 画幅；主体特征在全部镜头中保持一致；不出现水印、字幕或多余文字。".format(extra, ratio)


def _changes(scene: str, ratio: str) -> str:
    return "\n".join([
        "- 判定为「{}」，并据此组织镜头节奏".format(scene),
        "- 补全主体设定与参考图占位，保证一致性",
        "- 加入光线、声音与全局约束，便于直接使用",
        "- 按 {} 画幅调整构图重心".format(ratio),
        "- 这是离线演示结果：配置 DeepSeek key 后即可获得模型实时改写",
    ])


def stream_text(params: dict, delay: float = 0.012):
    """Yield the demo text in small chunks to exercise the real streaming path.
    把演示文本切成小块吐出，走真实的流式链路。
    """
    text = build_text(params)
    size = 6
    for i in range(0, len(text), size):
        time.sleep(delay)
        yield text[i:i + size]
