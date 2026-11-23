# -*- coding: utf-8 -*-
"""Offline demo generator (no API key required) / 离线演示生成器（无需 API key）.

Emits the same four-section text as the real model so the entire pipeline —
streaming, SegmentParser, scene inference display, history — runs unchanged.
输出与真实模型相同的四段文本，让流式、解析器、戏份展示、历史等整条链路
原样运行。

Everything is deterministic and local: no network, no secrets, no user data
leaving the machine. The UI labels the result as a demo.
全部内容确定且本地生成：不联网、不需要密钥、不上传任何用户数据。
界面会标注这是演示内容。

戏份与画风沿用 rules_data.json 的正式词表，避免演示输出和文档对不上。
"""
from __future__ import annotations

import re
import time

import rules

# 关键词 → 官方六类戏份。顺序从最具体到最宽泛，先命中先返回。
_SCENE_HINTS = [
    ("动作戏", ("追", "逃", "打斗", "奔跑", "跳", "战斗", "追逐", "冲突", "搏斗",
                "chase", "fight", "battle", "run")),
    ("恐怖戏", ("恐怖", "惊悚", "鬼", "阴森", "尖叫", "血腥", "horror", "scary")),
    ("悬疑戏", ("悬疑", "秘密", "线索", "调查", "真相", "监控", "嫌疑",
                "mystery", "suspect", "clue")),
    ("对话戏", ("对话", "交谈", "争吵", "争论", "conversation", "dialogue", "talk")),
    ("环境戏", ("空镜", "风景", "城市", "街道", "雪山", "海边", "窗台", "咖啡",
                "餐桌", "清晨", "午后", "landscape", "street", "window")),
]

# 未命中任何关键词时的默认戏份
DEFAULT_SCENE = "叙事戏"

# 画风说明，键与 rules_data.json 的 styles 保持一致
_STYLE_LABEL = {
    "2D": "2D 赛璐璐动画风",
    "3D": "3D 写实渲染风",
    "国漫": "国漫线描风",
    "次世代CG": "次世代 CG 渲染风",
}

# 分镜模板：景别、画面动作、环境音
_BEATS = [
    ("中景", "建立场景，主体进入画面", "环境底噪、轻微空气声"),
    ("近景", "主体开始动作，镜头缓慢推进", "动作细节声"),
    ("特写", "抓住关键细节，情绪或冲突升级", "主体声、节奏加强"),
    ("中景", "动作延续，光线随镜头变化", "环境声回环"),
]


def scene_types() -> list:
    """正式戏份词表，供测试与调用方核对。"""
    return list(rules.SCENE_TYPES)


def infer_scene(prompt: str, override: str = "") -> str:
    """Pick a scene from the official vocabulary by keywords.
    按关键词在正式词表里挑一个戏份，是模型判定在离线模式下的替身。
    """
    if override:
        return override
    text = (prompt or "").lower()
    for label, words in _SCENE_HINTS:
        if any(word in text for word in words):
            return label
    return DEFAULT_SCENE


def build_text(params: dict) -> str:
    """Build the four-section raw text fed to SegmentParser / 构造喂给解析器的四段原文."""
    prompt = (params.get("prompt") or "").strip()
    scene = infer_scene(prompt, params.get("scene_type", ""))
    style_key = params.get("style", "")
    style = _STYLE_LABEL.get(style_key, style_key or "柔和的写实风格")
    ratio = params.get("ratio", "16:9") or "16:9"
    duration = params.get("duration", "自动")
    model = params.get("model", "seedance")

    # Keep the user's own words visible so the demo feels connected to the input.
    # 保留用户自己写的词，让演示看起来与输入确实相关。
    subject = re.split(r"[，。！？,\.!?]", prompt)[0][:24] or "画面中的主体"

    video = model in rules.VIDEO_MODELS
    frames = _video_storyboard(scene, video, duration) if video else _image_plan()

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


def _seconds(duration):
    """把时长参数解析成整数秒；无法解析时返回 None。"""
    try:
        value = int(str(duration).strip())
    except (TypeError, ValueError):
        return None
    return value if 2 <= value <= 30 else None


def _fmt_second(value) -> str:
    return str(int(value)) if float(value).is_integer() else "{:.1f}".format(value)


def _video_storyboard(scene: str, video: bool, duration: str) -> str:
    total = _seconds(duration) or 4
    count = min(total, 8)
    step = total / count
    camera = "侧机位" if scene == "动作戏" else "平视"

    lines = ["【分镜】"]
    for index in range(count):
        start = index * step
        end = min(total, (index + 1) * step)
        shot, action, sound = _BEATS[index % len(_BEATS)]
        lines.append("[{}-{}s]：{}，{} — {}；<{}>".format(
            _fmt_second(start), _fmt_second(end), shot, camera, action, sound))
    return "\n".join(lines)


def _image_plan() -> str:
    return "\n".join([
        "【构图】",
        "主体居中偏左，留出呼吸感；前景轻虚化，背景层次分明。",
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
