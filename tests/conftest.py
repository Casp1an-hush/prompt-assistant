# -*- coding: utf-8 -*-
"""测试全局夹具。

关键原则：把数据库 / 日志 / 规则缓存全部隔离到 pytest 的临时目录，
任何测试都不会读改写用户真实的 data/studio.db 与 logs/。
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# app.py 在模块导入时就会 basicConfig 挂一个指向 LOG_DIR 的日志 handler，
# 而 test_api.py 在收集阶段就 import app —— 早于任何 fixture。
# 因此必须在 conftest 加载时（收集前）就把日志目录改到临时位置，
# 否则测试会往用户真实的 logs/studio.log 写内容。
import config as _config

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="prompt-assistant-tests-"))
_config.LOG_DIR = _TEST_ROOT / "logs"
_config.DB_FILE = _TEST_ROOT / "boot" / "studio.db"
_config.ensure_dirs()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """每个用例前重置数据层与规则缓存，指向临时文件。"""
    import config

    monkeypatch.setattr(config, "DB_FILE", tmp_path / "studio.db")
    monkeypatch.setattr(config, "LOG_DIR", tmp_path / "logs")
    monkeypatch.setattr(config, "CACHE_TTL", 86400.0)
    monkeypatch.setattr(config, "DEV_MODE", False)
    config.ensure_dirs()

    import store

    store.init_db()

    import rules

    monkeypatch.setattr(rules, "_state", {"mtime": None, "data": None})
    yield
