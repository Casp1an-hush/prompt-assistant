# Prompt Assistant

[![tests](https://github.com/zjy053231-crypto/prompt-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/zjy053231-crypto/prompt-assistant/actions/workflows/ci.yml) [![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![macOS](https://img.shields.io/badge/macOS-supported-1f6feb)](#macos) [![Windows](https://img.shields.io/badge/Windows-supported-0078D4)](#windows)

> Before the image — 画面之前 — 畫面之前

Write what you mean — the rest is composed.
写下所想，其余由它铺陈。

---

## English

A local workspace that turns one rough line into a model-ready prompt: shot sizes, camera movement, lighting and sound cues, plus a persistent style lock. The scene type is inferred from what you write — never asked. Tweak it only when you want, via "Change scene" in the result panel.
一个本地提示词工作台：把一句模糊的描述整理成模型可用的分镜、镜头运动、光线与声音提示，并带一个持久的风格锁定。戏份由你写的内容自动推断，不向用户提问；想微调时才用结果区的「换个戏份」。

Built with FastAPI, SSE streaming and a local SQLite store — no cloud service, no account, no data leaving your machine. Works on both macOS and Windows, each with a one-click launcher that sets up the environment and opens the browser only when the page is truly ready.
基于 FastAPI、SSE 流式输出与本地 SQLite 历史，无云服务、无账号、数据不出本机。同时支持 macOS 与 Windows，两边都有开箱即用的启动入口：自动建环境、引导填 key、清理卡死的旧服务，并在页面真正就绪后才打开浏览器。

**No API key? No problem.** Without a DeepSeek key the app automatically enters **Demo mode** and generates a complete offline sample, so reviewers can experience the full pipeline — streaming, scene inference, storyboard, changes — without signing up. Add `DEEPSEEK_API_KEY` any time to switch to live rewriting.
**没有 API key 也能用。** 未配置 DeepSeek key 时应用自动进入**演示模式**，生成完整的离线样例，评委无需注册即可体验流式、戏份判定、分镜、改动说明的完整链路。随时填入 `DEEPSEEK_API_KEY` 即切换为模型实时改写。

Targets Seedance 2.5 and MiniMax H3 (video), Doubao / Seedream and GPT Image (image). Rewriting is done by DeepSeek; the per-model rules live in `rules_data.json` and can be edited without touching code.
面向 Seedance 2.5、MiniMax H3（视频）与豆包 Seedream、GPT Image（图片）。改写由 DeepSeek 完成，各模型规则写在 `rules_data.json`，改规则无需动代码。

## 中文

基于 DeepSeek 的本地提示词工作台：把一句模糊的描述整理成模型可用的分镜、镜头运动、光线与声音提示。戏份由模型推断，不向用户提问；想微调时才用结果区的「换个戏份」。FastAPI + SSE 流式输出 + SQLite 本地历史，一键启动。

## Quick start · 快速开始

Requires Python 3.10+. Both platforms provide one-click launchers that create the virtual environment, optionally guide you through entering a key (skip to stay in Demo mode), clean up stuck services, and open the browser only when the full page is ready.
要求 Python 3.10+。两个平台都提供一键入口：自动建虚拟环境、引导填 key（可跳过以留在演示模式）、清理卡死的旧服务，并在页面真正能返回完整内容后才打开浏览器。

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # Optional: set DEEPSEEK_API_KEY for live mode · 可选：填入 key 以启用实时模式
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### macOS

Double-click **`Prompt Assistant.app`** (recommended — custom icon, forwards to `run.command`), or `run.command` directly.
双击 **`Prompt Assistant.app`**（推荐，带自定义图标，转发到 `run.command`）或直接双击 `run.command`。

> A `.app` downloaded from GitHub may trigger "unknown developer": right-click → Open → Open again, or run `xattr -d com.apple.quarantine "Prompt Assistant.app"`. Normal for unsigned apps.
> 从 GitHub 下载的 `.app` 可能提示「来自未知开发者」：右键 → 打开 → 再点「打开」，或执行 `xattr -d com.apple.quarantine "Prompt Assistant.app"`。这是未签名应用的正常现象。

### Windows

1. Double-click **`create-shortcut.cmd`** once to create a desktop shortcut with the icon. 双击 **`create-shortcut.cmd`**（只需一次）在桌面生成带图标的快捷方式。
2. Afterwards use the desktop icon, or double-click `run.cmd` directly. 以后双击桌面图标，或直接双击 `run.cmd`。

### Manual setup (any platform) / 手动安装（任意平台）

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip.exe
cp .env.example .env                           # Windows: copy .env.example .env
# Optional: set DEEPSEEK_API_KEY for live rewriting · 可选：填入 key 以启用实时改写
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Then open <http://localhost:8000>. 然后打开 <http://localhost:8000>。

## Example output · 效果示例

Input / 输入：

> 一个少年在雨夜的天台上追一个黑衣人，镜头越来越快

Selected `Seedance 2.5` / `2D` / `9:16` / `8s`, giving (excerpt; full output ~770 chars):
选择 `Seedance 2.5` / `2D` / `9:16` / `8 秒`，得到（节选，完整输出约 770 字）：

```
【Style Lock】
2D cel animation: flat color blocks, few shadow layers, low visual density;
cool blue night tones and neon purple, rain as thin white lines, a rim light on subjects.

【Reference images】
@img1 = youth character sheet, lock face / hair / wet coat
@img2 = pursuer sheet, lock build / trench coat / hood
@img3 = rainy rooftop, lock reflections / neon signs / railing layout

【Characters】
Youth: mid-teens, wet short hair, dark hooded coat, large movements.
Pursuer: all-black trench coat, hood low over face, lean, coat flaring while running.

【Storyboard】
[0-1s]: medium, side angle, accelerating tracking — youth enters from left, splashes a puddle;
        <urgent rain, footsteps in water>
[1-2s]: close, 45-degree, fast push — youth lunges to grab the pursuer's coat;
        <cloth rustle, heavy breathing>
...
```

And the inference / 同时给出判定与依据：

- **Scene / 戏份判定** — Action: a rainy rooftop chase, built around speed and escalating conflict. 动作戏 —— 雨夜天台追逐，核心是速度与冲突升级。
- "Faster camera" is expanded into a per-second storyboard, from tracking to whip pans. 把「镜头越来越快」拆成逐秒分镜，从跟拍推进到甩镜快推。
- Two character sheets are filled in to keep the cast consistent across 8 seconds. 补全两份人物设定，保证 8 秒内角色一致。
- Rain, footsteps and breathing cues are added for impact. 加入雨声、脚步、心跳等音效标记，强化动作戏的冲击感。
- Reframed for 9:16 portrait, favoring close-ups over horizontal blocking. 按 9:16 竖屏改为以近景、特写为主。

| | Tagline / 短句 | Subtitle / 小字 |
|---|---|---|
| 简中 | 写下所想，其余由它铺陈 | 画面之前 |
| 繁中 | 寫下所想，其餘由它鋪陳 | 畫面之前 |
| EN | Write what you mean — the rest is composed. | Before the image |

The product name "Prompt Assistant" is identical in all three languages. Full copy: [docs/brand-copy.md](docs/brand-copy.md).
产品名 Prompt Assistant 三语相同，不翻译。完整文案见 [docs/brand-copy.md](docs/brand-copy.md)。

## Features · 功能亮点

- **Scene inference / 戏份判定** — The model decides the scene from your text; "Change scene" is there only for fine-tuning. 模型根据你的文字判定戏份，「换个戏份」只用于微调。
- **Script breakdown / 剧本拆解** — Paste a script split into `第X集 X-Y` scenes and get character model cards, scene plates and prop plates, each with a ready-to-use image prompt. 粘贴按「第X集 X-Y」分段的剧本，自动列出人物模卡、场景图、道具图，每张都附可直接出图的提示词。
- **Structured output / 结构化输出** — A four-section protocol (scene / reason / prompt / changes) parsed by a streaming state machine. 四段协议（戏份 / 依据 / 提示词 / 改动），由流式状态机解析。
- **Live SSE streaming / SSE 流式输出** — `start → meta → delta×N → done`, with incremental scene detection. `start → meta → delta×N → done`，戏份一旦判定立即推送。
- **Local cache & history / 本地缓存与历史** — SQLite-backed cache and history; nothing uploaded. SQLite 缓存与历史，不上传任何内容。
- **Demo mode / 演示模式** — Full offline experience with no key, no network and no signup. 无需 key、无需联网、无需注册即可完整体验。
- **Trilingual interface / 三语界面** — Switch the whole interface between Simplified Chinese, Traditional Chinese and English from the top bar; the choice is remembered, and server errors are rendered in the selected language. 顶部可切换简体 / 繁體 / English，选择会被记住，服务端报错也按当前语言显示。

## Script breakdown · 剧本拆解

Turn a segmented script into production-ready asset cards: character model cards, scene plates and prop plates.
把分好段的剧本拆成可直接开工的资产：人物模卡、场景图、道具图。

**输入格式 / Input format** — the script must be split by hand into an episode line, a scene-number line and the body; the app checks for it and refuses to guess.
剧本需要先手动按集、场分段，程序会检查，不会替你猜：

```
第一集
1-1
雨夜，老城区天台，积水映着霓虹。
林晚推门冲上天台，雨水顺着湿透的短发往下淌……

1-2
陈默回过头，露出左眉一道旧疤……
```

格式要求：**集名单独一行，每个场次号也单独一行**。每集分几场不限，长的可以十几场。
Format: the episode line and each scene number (`1-1`, `1-2` …) sit on their own lines. An episode can have any number of scenes.

Up to 30,000 characters per run. 单次上限 3 万字。

**人物模卡 / Character card** — every card is laid out as *frontal head close-up on the left, full-body three-view on the right*; the prompt follows a fixed order: style anchor → name / gender / age → personality → appearance (build, face, bone structure) → costume (hair, cut, colour, layering).
每张卡的画面结构固定为「左侧正面头部特写 + 右侧全身三视图」，提示词按固定顺序组织：风格锚定 → 姓名性别年龄 → 性格 → 外貌（体型、五官、骨相）→ 服饰（发色发长、款式、颜色、剪裁、叠穿）。

**状态拆分 / States** — one card per character by default, labelled 主状态. A new card is added only when the script says so:

- 副状态 N — 换装、更衣、换造型；身份转变、战伤、成长升级带来的形态变化
- 主状态 1 / 主状态 2 — 外貌在剧本前半与后半有显著差异

**风格锚定 / Style anchors** — the four styles are anchored with concrete material terms, not just names, and the anchor sentence is written by code so every card stays identical:
四种画风都用具体的材质词锚定，锚定句由程序统一拼装，保证每张卡完全一致：

| 画风 | 锚定的关键质感 |
|---|---|
| 2D | 平涂色块、单档硬边阴影、清晰黑色描线；禁止渐变与体积光 |
| 3D | PBR 材质、皮肤次表面散射、织物经纬、金属各向异性高光 |
| 国漫 | 书法性线条、矿物色、五至六成留白、宣纸绢本质感 |
| 次世代CG | 院线级 CG、物理全局光照、体积雾与空气透视、85mm 浅景深 |

**导出 / Export** — one click produces a Markdown asset sheet that can be handed straight to an artist.
一键导出 Markdown 资产清单，可直接交给美术。

## Tech · 技术实现

A clean FastAPI service with deliberately simple, auditable components.
一个结构清晰的 FastAPI 服务，各组件刻意保持简单、可审计。

- `parsing.py` — Four-section streaming state machine. Markers split across chunks are held as a prefix tail, so no character is lost. 四段流式状态机；标记被拆进两个 chunk 时保留前缀尾巴，逐字不丢。
- `llm.py` — DeepSeek client with a heartbeated concurrency gate: stuck slots self-heal by idle / absolute timeout (a `Semaphore` + `finally` leaks slots when a client cancels a synchronous generator). DeepSeek 客户端，并发闸门带心跳：僵尸槽位按 idle / 绝对超时自愈（用 `Semaphore` + `finally` 时客户端取消同步生成器会永久泄漏名额）。
- `demo.py` — Offline generator producing the same four-section text, so the entire pipeline runs unchanged without a key. 离线生成器，产出同样的四段文本，无 key 时整条链路原样运行。
- `breakdown.py` — Script → assets. The model returns structured fields only; the image prompts are assembled in code so the style anchor is byte-identical across every card. 剧本转资产：模型只返回结构化字段，出图提示词由代码拼装，保证风格锚定句在每张卡上完全一致。
- `store.py` — SQLite cache and history with cache keys depending only on business fields. SQLite 缓存与历史，缓存 key 只依赖业务字段。
- `errors.py` — Upstream status codes become actionable Chinese hints; keys and raw upstream responses never reach the UI. 上游状态码转成可操作的中文提示，key 与原始报文不会透出到界面。
- `static/` — Single-page front end (vanilla JS/CSS), pluggable views, GPU-friendly motion layer that respects `prefers-reduced-motion`. 单页前端（原生 JS/CSS），可插拔视图，动效层走 GPU 并尊重系统「减少动效」。

## API

| Method | Path | Description / 说明 |
|---|---|---|
| GET | `/api/health` | Health + config status, including `demo_mode` · 健康与配置状态，含 `demo_mode` |
| GET | `/api/options` | Dropdown options, feature flags, backgrounds · 下拉选项、功能开关、背景 |
| POST | `/api/stream` | Main SSE endpoint: `start → meta → delta×N → done` · 主 SSE 接口 |
| POST | `/api/rewrite` | Synchronous rewrite · 同步改写 |
| POST | `/api/breakdown` | Script → asset cards with image prompts and Markdown · 剧本拆解：返回人物模卡 / 场景图 / 道具图 |
| GET | `/api/history?limit=20` | History list · 历史列表 |
| GET / DELETE | `/api/history/{id}` | Detail / delete · 详情 / 删除 |
| DELETE | `/api/history` | Clear history · 清空历史 |
| POST | `/api/admin/reload` | Hot-reload rules (`DEV_MODE=1` only) · 热重载规则（仅开发模式） |

## Configuration · 配置

All in `.env` or environment variables; no code changes needed. 全部在 `.env` 或环境变量中，改配置不用动代码。

| Variable | Default | Description / 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | — | Optional. Without it, Demo mode runs · 可选，不填则进入演示模式 |
| `DEMO_MODE` | `0` | `1` forces Demo mode even with a key · 设为 `1` 时即使有 key 也强制演示 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | Rewriting model · 改写用模型 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | Compatible endpoint · 兼容接口地址 |
| `REQUEST_TIMEOUT` | `90` | Upstream timeout (s) · 上游超时（秒） |
| `MAX_CONCURRENCY` | `2` | Max simultaneous rewrites · 同时最多几个改写请求 |
| `CACHE_TTL` | `86400` | Cache TTL (s), `0` disables · 缓存有效期（秒），`0` 关闭 |
| `DEV_MODE` | `0` | Enables rule hot-reload · 开启规则热重载 |

Editing `rules_data.json` takes effect immediately via mtime-based reload. 改 `rules_data.json` 无需重启，按 mtime 自动生效。

## Testing · 测试

Automated tests cover the core logic, fully isolated in temp directories — no real `data/studio.db`, no `.env`, no network calls to DeepSeek.
自动化测试覆盖核心逻辑，全部隔离在临时目录，不碰真实 `data/studio.db`、不需要 `.env`、不联网调 DeepSeek。

| File | Coverage / 覆盖 |
|---|---|
| `test_parsing.py` | Four-section state machine: markers split into 1/2/3/5/7-char chunks produce output identical to whole-text parsing; meta sent once; non-format output degrades without losing content · 四段状态机，标记按 1/2/3/5/7 字符切块喂入与整段解析一致；meta 只发一次；非格式输出降级不丢内容 |
| `test_rules.py` | mtime hot-reload; video/image models use different formats; unknown model errors · 按 mtime 热加载；视频/图片模型不同输出；未知模型报错 |
| `test_store.py` | Cache hit / expiry / off / bad-data fallback; history CRUD; cache key depends only on business fields · 缓存命中/过期/关闭/坏数据降级；历史增删查；缓存 key 只依赖业务字段 |
| `test_llm.py` | Concurrency cap, idempotent release, zombie slot self-heal · 并发上限、幂等释放、僵尸槽位自愈 |
| `test_errors.py` | Status code → Chinese hint; key and raw response never leak · 状态码 → 中文提示；key 与原始报文不泄漏 |
| `test_api.py` | Endpoint smoke tests · 接口冒烟 |
| `test_demo.py` | Offline demo: four sections, parse round-trip, scene inference, chunked stream equals full parse · 离线演示：四段、解析往返、戏份判定、分块流式与整段一致 |

```bash
pip install -r requirements-dev.txt
pytest -q
```

GitHub Actions runs the same suite on Python 3.10 / 3.12 / 3.14 for every push and PR; the `tests` badge above is that workflow's status.
每次 push / PR 时 GitHub Actions 在 Python 3.10 / 3.12 / 3.14 三个版本上跑同一套测试，顶部 `tests` 徽章即该工作流状态。

## Known limits · 已知局限

- Rewriting quality depends on `rules_data.json` and DeepSeek itself. 改写质量取决于规则与 DeepSeek 本身。
- Demo mode uses fixed offline samples, not model generation — labelled clearly in the UI. 演示模式使用固定的离线样例而非模型生成，界面已明确标注。
- If the model ignores the four-section format entirely, the parser treats everything as the prompt (content preserved, but no scene / changes). 若模型完全不按四段格式输出，解析器会把整段当提示词（内容不丢，但缺戏份与改动说明）。
- Database and logs live in the project directory; no multi-user or backup support yet. 数据库与日志在项目目录，暂不支持多用户与备份。

## Changelog · 更新日志

See [CHANGELOG.md](CHANGELOG.md). 见 [CHANGELOG.md](CHANGELOG.md)。

## AI collaboration · AI 协作说明

Development and implementation were done in a human–AI collaboration: requirement definition, experience design, rule curation and result acceptance were led by the author, while implementation was assisted by AI tooling.
开发与实现采用人机协作方式完成：以需求定义、体验设计、规则整理和结果验收为主导，实现环节借助 AI 工具链完成。

The per-model rewriting rules in `rules_data.json` are based on the four models' published prompt guides and will be extended with the author's own production experience.
`rules_data.json` 中各模型的改写规则基于四个模型公开的提示词指南整理，后续将继续补充作者本人的生产实践经验。

## License · 许可

MIT — see [LICENSE](LICENSE). MIT — 见 [LICENSE](LICENSE)。
