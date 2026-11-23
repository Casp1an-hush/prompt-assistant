# Changelog · 更新日志

All notable changes to this project are documented here. Format follows Keep a Changelog; versions follow Semantic Versioning.
本项目的所有重要变更都记录于此。格式遵循 Keep a Changelog，版本号遵循语义化版本。

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
