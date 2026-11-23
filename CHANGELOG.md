# Changelog · 更新日志

All notable changes to this project are documented here. Format follows Keep a Changelog; versions follow Semantic Versioning.
本项目的所有重要变更都记录于此。格式遵循 Keep a Changelog，版本号遵循语义化版本。

## v0.2.0 — 2026-11-25

- **Script breakdown / 剧本拆解** — New view: paste a script split into `第X集 X-Y` scenes and get character model cards, scene plates and prop plates, each carrying a ready-to-use image prompt. 新增剧本拆解视图：粘贴按「第X集 X-Y」分段的剧本，输出人物模卡、场景图、道具图，每张都附可直接出图的提示词。
- **Character cards / 人物模卡** — Fixed layout (frontal head close-up on the left, full-body three-view on the right) and a fixed prompt order: style anchor → name / gender / age → personality → appearance → costume. One card per character by default; 副状态 cards are added only when the script says the costume or form changes, and 主状态 1 / 2 when the appearance differs between halves. 固定版式（左头部特写、右全身三视图）与固定字段顺序；默认一张主状态，剧本明确写了换装或形态变化才拆副状态，前后半外貌差异大则分为主状态 1 / 2。
- **Concrete style anchors / 风格锚定具体化** — The four styles are now anchored with material and lighting terms instead of bare names (flat fill + single hard shadow for 2D; PBR + subsurface scattering for 3D; calligraphic lines + mineral pigments + negative space for 国漫; film-grade CGI + volumetric haze + 85mm for 次世代CG). The anchor sentence is assembled in code, so every card is identical. 四种画风改用具体材质与光学词锚定，锚定句由代码拼装，保证每张卡完全一致。
- **Guard rails / 输入校验** — Rejects scripts without `第X集 X-Y` markers, under 30 characters or over 30,000 characters. 未分段、过短或超过 3 万字的文本会被拒绝并给出提示。
- **Markdown export / 导出** — One click turns the result into an asset sheet for the art team. 一键导出可直接交给美术的资产清单。
- **Trilingual interface / 三语界面** — The whole UI can be switched between Simplified Chinese, Traditional Chinese and English from the top bar; the choice is remembered. Static copy uses `data-i18n` attributes, dynamic copy goes through a lookup table, and server errors carry codes so the message is rendered in the current language. 顶部可切换简体 / 繁體 / English，选择会被记住；静态文案用 `data-i18n` 标注、动态文案走查表、服务端错误返回 code 由前端按语言渲染。
- **Name chips and editable prompts / 名字按钮与可编辑提示词** — After a breakdown, each card is reachable from a row of name buttons, so you pick the asset instead of scrolling. The image prompt itself is editable in place; edits are marked, can be reset, and are what the copy button and the Markdown export use. 拆解后上方是一排名字按钮，点谁看谁，不用往下翻；出图提示词可直接编辑，会标记「已修改」并可恢复原文，复制与导出用的都是改后的版本。
- **Version bump / 版本更新** — `VERSION` set to `0.2.0`. 版本号升至 `0.2.0`。
- **Tests / 测试** — 70 passing, including the breakdown parser, the anchor uniqueness and an assertion that demo labels stay inside the official vocabulary. 70 项通过，含拆解解析、锚定句互不相同、演示词表属于正式词表等断言。

## v0.1.3 — 2026-11-24

- **Demo uses the official vocabulary / 演示模式改用正式词表** — The offline demo previously invented its own scene labels (情绪戏 / 日常切片 / 产品静物) and style names (真人 / 水墨 / 像素), none of which exist in `rules_data.json`, so demo output contradicted the documented six scene types. Demo inference now picks from `rules.SCENE_TYPES` with 叙事戏 as the default, and style labels follow `rules.STYLES`. 离线演示此前另造了戏份与画风名称，与 `rules_data.json` 中的正式词表不一致；现改为直接使用正式六类戏份与四种画风。
- **Cleaner demo output / 演示输出更干净** — The demo caveat no longer sits inside the copyable prompt (it stays in the changes list and the UI notice), and the storyboard follows the requested duration instead of always showing four seconds. 演示说明不再混入可复制的正文（保留在改动列表与界面提示中）；分镜段数跟随所选时长，不再固定为 4 秒。
- **AI collaboration statement / AI 协作声明** — README now documents the human–AI division of work and the origin of the rewriting rules. README 新增人机分工与规则来源说明。
- **Version bump / 版本更新** — `VERSION` set to `0.1.3`. 版本号升至 `0.1.3`。
- **Tests / 测试** — 57 passing, including a guard that demo labels are a subset of the official vocabulary. 57 项通过，含"演示词表必须是正式词表子集"的回归测试。

## v0.1.2 — 2026-11-23

- **Demo mode (no API key needed) / 演示模式（无需 API key）** — Without a DeepSeek key the app now serves a complete offline sample through the same four-section parser and SSE pipeline, so reviewers can experience streaming, scene inference, storyboard and changes without signing up. Added `DEMO_MODE` config, a bilingual banner, an offline generator (`demo.py`), and 4 tests. 未配置 DeepSeek key 时，应用通过同一套四段解析器与 SSE 链路输出完整离线样例，评委无需注册即可体验流式、戏份判定、分镜与改动说明。新增 `DEMO_MODE` 配置、双语提示条、离线生成器与 4 项测试。
- **Fully bilingual docs / 文档全面双语** — README rewritten English-first, Chinese-second throughout; added this bilingual CHANGELOG. README 全文改为英文在前、中文在后的对照排版；新增本双语更新日志。
- **Version bump / 版本更新** — `VERSION` set to `0.1.2`, reflected in `/api/health` and the UI badge. 版本号升至 `0.1.2`，同步到 `/api/health` 与界面角标。

## v0.1.1 — 2026-11-17

- **Dual-platform launchers / 双平台启动器** — One-click, icon-bearing launchers for macOS (`.app`) and Windows (`run.cmd` + shortcut creator), with environment setup, key guidance, stale-service cleanup and a full-page readiness check before opening the browser. macOS / Windows 一键带图标启动器：自动建环境、引导填 key、清理卡死旧服务、页面真正就绪后才打开浏览器。
- **Engineering hardening / 工程加固** — Fixed streaming marker splits across chunks, white screens, 429 handling, concurrency-slot leaks and launcher mis-kills; added pytest suite and GitHub Actions CI on Python 3.10 / 3.11 / 3.12. 修复流式标记跨 chunk 漏字、白屏、429、并发槽位泄漏与启动脚本误杀；新增 pytest 套件与 Python 3.10 / 3.11 / 3.12 的 GitHub Actions CI。
- **Trilingual copy / 三语文案** — Simplified / Traditional / English taglines; product name kept identical. 简体 / 繁體 / English 标语；产品名三语相同。

## v0.1.0 — 2026-11-17

- **First release / 首发** — Local prompt-rewriting workspace: FastAPI + DeepSeek rewriting + SSE streaming + SQLite history, a four-section output protocol, per-model rules in `rules_data.json`, macOS / Windows one-click launchers, MIT license. 本地提示词改写工作台：FastAPI + DeepSeek 改写 + SSE 流式 + SQLite 历史，四段输出协议，`rules_data.json` 分模型规则，macOS / Windows 一键启动器，MIT 许可。
