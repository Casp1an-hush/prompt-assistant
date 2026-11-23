# -*- coding: utf-8 -*-
"""Script breakdown: turn a segmented script into production asset cards.

把按「集-场」分好段的剧本拆成美术资产：人物模卡、场景图、道具图。

设计要点：
- 模型只负责抽取结构化字段；最终出图提示词由代码拼装，
  保证风格锚定句在所有卡片里完全一致，不会被模型改写走样。
- 人物默认一张「主状态」卡，只有剧本明确写了换装 / 形态变化才拆副状态。
"""
from __future__ import annotations

import json
import re

import rules

MAX_CHARS = 30000

# 剧本格式：
#   第一集          ← 集名必须单独一行
#   1-1             ← 场次号必须单独一行，格式为「集-场」
#   （正文）
#   1-2             ← 每集有多少场不固定
#   （正文）
# 硬性要求：集名单独一行、每个场次号单独一行。
_EPISODE_RE = re.compile(r"^\s*第\s*[0-9一二三四五六七八九十百]+\s*集\s*$", re.M)
_SCENE_RE = re.compile(r"^\s*(\d+)\s*[-－—]\s*(\d+)\s*$", re.M)

SYSTEM = """你是影视与漫剧的美术资产拆解师。用户会给你分好段的剧本：集名「第一集」单独一行，场次号「1-1」也单独一行，后面跟正文，你要从中抽取所有需要制作的美术资产，输出 JSON。

抽取规则：
1. 人物：剧本通常不会大篇幅描写外貌。你要根据身份、年龄、性格与剧情合理补全，但不得与剧情冲突。
2. 每个角色默认只出一张卡，label 固定为「主状态」。
   只有在剧本明确出现以下情况时，才新增卡片：
   - 明确写了换装、更衣、换造型
   - 身份转变、受伤战损、成长升级导致外貌或形态变化
   新增卡片依次标为「副状态1」「副状态2」。
   若同一角色的外貌在剧本前半与后半有显著差异，改用「主状态1」「主状态2」。
3. 每张卡必须写 note，注明这个状态出现在哪些场次，沿用剧本里的编号，例如「第一集 1-1、1-3」。
4. appearance 要具体到能画出来：身高体型、脸型、五官与骨相特征、肤色。
5. costume 要具体到：发色发长发型、服装款式、颜色、剪裁、层次叠穿、鞋。
6. anchors 放 1 到 3 条必须在所有镜头中保持不变的特征。
7. 场景：name、time（时间）、era（时代/地点类型）、architecture（建筑与材质）、lighting（光线氛围）、note。
8. 道具：name、material、size、color、detail（关键细节）、note。
9. 不要遗漏重要角色、场景与道具；只出现一次且不影响剧情的龙套可合并为一条概括条目。
10. 只输出 JSON，不要任何解释文字。

输出结构：
{
  "characters": [{"name","label","gender","age","personality","appearance","costume","anchors":[],"note"}],
  "scenes": [{"name","time","era","architecture","lighting","note"}],
  "props": [{"name","material","size","color","detail","note"}]
}"""


class BreakdownError(Exception):
    """面向用户的错误，可直接展示。"""


def validate_script(text: str) -> list:
    """返回问题列表（含 code 与参数），空列表表示可以提交。

    只给 code，具体文案由前端按当前语言渲染。
    """
    problems = []
    text = text or ""
    if len(text.strip()) < 30:
        problems.append({"code": "too_short"})
    if len(text) > MAX_CHARS:
        problems.append({"code": "too_long", "chars": len(text), "limit": MAX_CHARS})
    # 硬性要求：集名单独一行，场次号各自单独一行。
    if not _has_episode(text):
        problems.append({"code": "no_episode"})
    if not _has_scene(text):
        problems.append({"code": "no_scenes"})
    return problems


def problem_message(problem: dict) -> str:
    """服务端的中文兜底文案（前端会按 code 本地化）。"""
    code = problem.get("code")
    if code == "too_short":
        return "内容太短，至少要有一段完整的剧情。"
    if code == "too_long":
        return "文本 {} 字，超过 {} 字上限，请先分成几批再提交。".format(
            problem.get("chars"), problem.get("limit"))
    if code == "no_episode":
        return ("没有检测到集名。集名需要单独占一行，例如「第一集」。\n"
                "第一集\n1-1\n（正文）\n1-2\n（正文）")
    if code == "no_scenes":
        return ("没有检测到场次号。每个场次需要单独占一行，写成「1-1」「1-2」这样的编号。例如：\n"
                "第一集\n1-1\n（正文）\n1-2\n（正文）")
    return "剧本格式不正确。"


def segments(text: str) -> list:
    """按出现顺序返回场次标签，例如 ["第一集 1-1", "1-2", "第二集 2-1"]。

    有集名时带上集名，没有就只返回场次号——不强制要求写集名。
    """
    labels = []
    episode = ""
    for line in (text or "").splitlines():
        stripped = line.strip()
        if _EPISODE_RE.match(stripped):
            episode = re.sub(r"\s+", "", stripped)
            continue
        scene = _SCENE_RE.match(stripped)
        if scene:
            number = "{}-{}".format(scene.group(1), scene.group(2))
            labels.append("{} {}".format(episode, number).strip())
    return labels


def _has_episode(text: str) -> bool:
    return bool(_EPISODE_RE.search(text or ""))


def _has_scene(text: str) -> bool:
    return bool(_SCENE_RE.search(text or ""))


def build_payload(script: str, style: str) -> dict:
    """构造发给模型的请求体（供 llm 层调用）。"""
    anchor = rules.STYLE_ANCHORS.get(style, "")
    style_note = ""
    if anchor:
        style_note = (
            "\n\n本片统一画风（描述资产时请与之协调）：{}\n"
            "不要把这个风格描述写进 JSON 字段，出图提示词会由程序统一拼装。".format(anchor)
        )
    return {
        "model": None,  # 由调用方填充
        "messages": [
            {"role": "system", "content": SYSTEM + style_note},
            {"role": "user", "content": script},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }


def parse(raw: str) -> dict:
    """解析模型返回的 JSON，并补齐缺失字段。"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # 模型偶尔会在 JSON 外包一层 ```，这里容错一次
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise BreakdownError("模型返回的内容不是有效 JSON，请重试一次。") from exc

    if not isinstance(data, dict):
        raise BreakdownError("模型返回的结构不正确，请重试一次。")

    return {
        "characters": _clean_list(data.get("characters"), (
            "name", "label", "gender", "age", "personality",
            "appearance", "costume", "note",
        ), "anchors"),
        "scenes": _clean_list(data.get("scenes"), (
            "name", "time", "era", "architecture", "lighting", "note",
        )),
        "props": _clean_list(data.get("props"), (
            "name", "material", "size", "color", "detail", "note",
        )),
    }


def _clean_list(items, fields: tuple, list_field: str = "") -> list:
    out = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        row = {key: str(item.get(key, "") or "").strip() for key in fields}
        if list_field:
            values = item.get(list_field) or []
            if isinstance(values, str):
                values = [values]
            row[list_field] = [str(v).strip() for v in values if str(v).strip()]
        if row.get("name"):
            out.append(row)
    return out


# ---------------------------------------------------------------- 提示词拼装
# 风格锚定句由代码统一加在最前，确保所有卡片风格一致。

def character_prompt(card: dict, style: str) -> str:
    anchor = rules.STYLE_ANCHORS.get(style, "")
    parts = [
        anchor,
        "角色设定图：左侧为正面头部特写，右侧为全身三视图（正面、侧面、背面）。",
        "{}。".format("，".join(x for x in (
            card.get("name", ""), card.get("gender", ""), _age_text(card.get("age", ""))
        ) if x)),
    ]
    if card.get("personality"):
        parts.append("性格{}。".format(card["personality"]))
    if card.get("appearance"):
        parts.append("外貌：{}".format(card["appearance"]))
    if card.get("costume"):
        parts.append("服饰：{}".format(card["costume"]))
    anchors = card.get("anchors") or []
    if anchors:
        parts.append("必须在所有画面中保持不变的特征：{}。".format("；".join(anchors)))
    parts.append("同一角色，白底，均匀布光，头部特写与三视图的五官、发型、服饰完全一致。")
    return _join(parts)


def _age_text(age: str) -> str:
    """模型可能返回「24」「24 岁」「20-25岁」，统一成带「岁」且不重复。"""
    age = (age or "").strip()
    if not age:
        return ""
    if not re.search(r"\d", age):
        return age
    return age if age.endswith("岁") else age + " 岁"


def scene_prompt(card: dict, style: str) -> str:
    anchor = rules.STYLE_ANCHORS.get(style, "")
    parts = [
        anchor,
        "场景设定图：{}。".format(card.get("name", "")),
        "{}，{}。".format(card.get("time", ""), card.get("era", "")),
        card.get("architecture", ""),
        "光线：{}".format(card.get("lighting", "")),
        "空场景，无人物。",
    ]
    return _join(parts)


def prop_prompt(card: dict, style: str) -> str:
    anchor = rules.STYLE_ANCHORS.get(style, "")
    parts = [
        anchor,
        "道具设定图：{}。".format(card.get("name", "")),
        "材质{}，尺寸{}，颜色{}。".format(
            card.get("material", ""), card.get("size", ""), card.get("color", "")),
        card.get("detail", ""),
        "白底，产品图布光，提供正面与侧面两个角度。",
    ]
    return _join(parts)


def _join(parts) -> str:
    return re.sub(r"\s{2,}", " ", " ".join(p.strip() for p in parts if p and p.strip())).strip()


def attach_prompts(result: dict, style: str) -> dict:
    """给每张卡补上可直接使用的出图提示词。"""
    for card in result.get("characters", []):
        card["prompt"] = character_prompt(card, style)
    for card in result.get("scenes", []):
        card["prompt"] = scene_prompt(card, style)
    for card in result.get("props", []):
        card["prompt"] = prop_prompt(card, style)
    return result


def to_markdown(result: dict, style: str) -> str:
    """导出成可直接交给美术的 Markdown。"""
    lines = ["# 剧本拆解 · 美术资产清单", "", "统一画风：{}".format(style or "未指定"), ""]

    def section(title, cards, render):
        if not cards:
            return
        lines.append("## {}".format(title))
        lines.append("")
        for card in cards:
            lines.extend(render(card))
            lines.append("")

    def render_character(card):
        out = ["### {} · {}".format(card["name"], card.get("label", "")), ""]
        for key, label in (
            ("gender", "性别"), ("age", "年龄"), ("personality", "性格"),
            ("appearance", "外貌"), ("costume", "服饰"),
        ):
            if card.get(key):
                out.append("- {}：{}".format(label, card[key]))
        if card.get("anchors"):
            out.append("- 一致性锚点：{}".format("；".join(card["anchors"])))
        if card.get("note"):
            out.append("- 出现场次：{}".format(card["note"]))
        out.extend(["", "```", card.get("prompt", ""), "```"])
        return out

    def render_scene(card):
        out = ["### {}".format(card["name"]), ""]
        for key, label in (
            ("time", "时间"), ("era", "时代与地点"), ("architecture", "建筑与材质"),
            ("lighting", "光线氛围"), ("note", "出现场次"),
        ):
            if card.get(key):
                out.append("- {}：{}".format(label, card[key]))
        out.extend(["", "```", card.get("prompt", ""), "```"])
        return out

    def render_prop(card):
        out = ["### {}".format(card["name"]), ""]
        for key, label in (
            ("material", "材质"), ("size", "尺寸"), ("color", "颜色"),
            ("detail", "关键细节"), ("note", "出现场次"),
        ):
            if card.get(key):
                out.append("- {}：{}".format(label, card[key]))
        out.extend(["", "```", card.get("prompt", ""), "```"])
        return out

    section("人物模卡", result.get("characters", []), render_character)
    section("场景图", result.get("scenes", []), render_scene)
    section("道具图", result.get("props", []), render_prop)
    return "\n".join(lines).strip() + "\n"


# ---------------------------------------------------------------- 演示模式

def demo_result(script: str, style: str) -> dict:
    """离线演示：按脚本给出一个明显标注为演示的样例，走完整的拼装与导出链路。

    名字不做猜测——猜错会让人误以为是真实抽取结果，这里用中性占位。
    """
    found = segments(script) or ["（未识别到分场）"]
    result = {
        "characters": [{
            "name": "角色 A（演示）",
            "label": "主状态",
            "gender": "（演示）",
            "age": "（演示）",
            "personality": "（演示）根据剧情补全",
            "appearance": "（演示）身高体型、脸型、五官与骨相、肤色",
            "costume": "（演示）发色发长发型、服装款式、颜色、剪裁、叠穿",
            "anchors": ["（演示）全部镜头中必须保持不变的特征"],
            "note": "、".join(found[:3]),
        }],
        "scenes": [{
            "name": "主要场景",
            "time": "（演示）",
            "era": "（演示）",
            "architecture": "（演示）建筑结构与材质",
            "lighting": "（演示）光源方向与氛围",
            "note": "、".join(found[:2]),
        }],
        "props": [{
            "name": "关键道具",
            "material": "（演示）",
            "size": "（演示）",
            "color": "（演示）",
            "detail": "（演示）决定辨识度的细节",
            "note": found[0],
        }],
    }
    return attach_prompts(result, style)
