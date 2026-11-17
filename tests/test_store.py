# -*- coding: utf-8 -*-
"""数据层测试：缓存命中 / 过期 / 关闭，以及历史增删查。全部走临时 DB。"""
from __future__ import annotations

import time

import store


def _record(rid: str, prompt: str = "一只橘猫看雪") -> dict:
    return {
        "id": rid,
        "created_at": time.time(),
        "model": "gpt-image",
        "input": prompt,
        "result_prompt": "窗台上的橘猫",
        "changes_json": '["加了雪"]',
        "status": "ok",
        "cached": 0,
    }


def test_cache_roundtrip():
    key = store.cache_key({"prompt": "橘猫", "model": "gpt-image"})
    assert store.cache_get(key) is None
    store.cache_put(key, {"scene": "近景", "prompt": "一只猫"})
    assert store.cache_get(key) == {"scene": "近景", "prompt": "一只猫"}


def test_cache_key_only_depends_on_business_fields():
    base = {"prompt": "橘猫", "model": "gpt-image", "ratio": "9:16"}
    # ignored_field 不在白名单里，加它不应改变 key
    same = dict(base, ignored_field="随便")
    different = dict(base, prompt="黑猫")
    assert store.cache_key(base) == store.cache_key(same)
    assert store.cache_key(base) != store.cache_key(different)

    # duration 是白名单里的业务字段，改变它必须得到不同 key
    with_duration = dict(base, duration="5")
    assert store.cache_key(base) != store.cache_key(with_duration)


def test_cache_disabled_when_ttl_zero(monkeypatch):
    import config

    monkeypatch.setattr(config, "CACHE_TTL", 0)
    key = store.cache_key({"prompt": "橘猫"})
    store.cache_put(key, {"prompt": "不该被写入"})
    assert store.cache_get(key) is None


def test_cache_expires_after_ttl(monkeypatch):
    import config

    monkeypatch.setattr(config, "CACHE_TTL", 0.01)
    key = store.cache_key({"prompt": "橘猫"})
    store.cache_put(key, {"prompt": "会过期"})
    assert store.cache_get(key) is not None
    time.sleep(0.02)
    assert store.cache_get(key) is None


def test_cache_corrupt_payload_returns_none(monkeypatch):
    """坏数据不能让整个服务崩，当缓存未命中处理。"""
    import config
    import sqlite3

    key = store.cache_key({"prompt": "坏数据"})
    store.cache_put(key, {"prompt": "先写好的"})
    conn = sqlite3.connect(str(config.DB_FILE))
    try:
        conn.execute("UPDATE cache SET payload = ? WHERE key = ?", ("{not json", key))
        conn.commit()
    finally:
        conn.close()
    assert store.cache_get(key) is None


def test_history_crud():
    store.log_request(_record("id-001", "橘猫"))
    store.log_request(_record("id-002", "黑猫"))

    items = store.history(limit=10)
    assert len(items) == 2
    assert items[0]["id"] in {"id-001", "id-002"}
    assert len(items[0]["input"]) <= 120  # 列表只给摘要

    detail = store.history_get("id-001")
    assert detail["input"] == "橘猫"
    assert detail["changes"] == ["加了雪"]

    assert store.history_delete("id-001") is True
    assert store.history_delete("id-001") is False  # 幂等
    assert store.history_get("id-001") is None

    assert store.history_clear() == 1
    assert store.history() == []


def test_new_id_is_unique():
    ids = {store.new_id() for _ in range(1000)}
    assert len(ids) == 1000
