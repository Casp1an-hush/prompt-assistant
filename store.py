# -*- coding: utf-8 -*-
"""sqlite 数据层：请求日志、结果缓存、历史记录。不引入任何新依赖。

这一层是以后加「模板库 / 收藏 / 批量对比」的地基。
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import uuid
from contextlib import closing

import config

_lock = threading.Lock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
    id            TEXT PRIMARY KEY,
    created_at    REAL NOT NULL,
    model         TEXT,
    scene_type    TEXT,
    style         TEXT,
    ratio         TEXT,
    duration      TEXT,
    input         TEXT,
    scene         TEXT,
    reason        TEXT,
    result_prompt TEXT,
    changes_json  TEXT,
    latency_ms    INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    status        TEXT,
    error         TEXT,
    cached        INTEGER DEFAULT 0,
    kind          TEXT DEFAULT 'rewrite'
);
CREATE INDEX IF NOT EXISTS idx_requests_created ON requests(created_at DESC);
CREATE TABLE IF NOT EXISTS cache (
    key         TEXT PRIMARY KEY,
    payload     TEXT NOT NULL,
    created_at  REAL NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    config.ensure_dirs()
    conn = sqlite3.connect(str(config.DB_FILE), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock, closing(_connect()) as conn:
        conn.executescript(_SCHEMA)
        # 老库补列：kind 用来区分改写记录与拆解记录
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(requests)")}
        if "kind" not in columns:
            conn.execute("ALTER TABLE requests ADD COLUMN kind TEXT DEFAULT 'rewrite'")
        conn.commit()


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def cache_key(params: dict) -> str:
    fields = ("prompt", "model", "scene_type", "style", "ratio", "duration")
    raw = json.dumps({k: params.get(k, "") for k in fields}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cache_get(key: str):
    if config.CACHE_TTL <= 0:
        return None
    with _lock, closing(_connect()) as conn:
        row = conn.execute("SELECT payload, created_at FROM cache WHERE key = ?", (key,)).fetchone()
    if not row or time.time() - row["created_at"] > config.CACHE_TTL:
        return None
    try:
        return json.loads(row["payload"])
    except json.JSONDecodeError:
        return None


def cache_put(key: str, payload: dict) -> None:
    if config.CACHE_TTL <= 0:
        return
    with _lock, closing(_connect()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache (key, payload, created_at) VALUES (?, ?, ?)",
            (key, json.dumps(payload, ensure_ascii=False), time.time()),
        )
        conn.commit()


def log_request(record: dict) -> None:
    columns = (
        "id", "created_at", "model", "scene_type", "style", "ratio", "duration",
        "input", "scene", "reason", "result_prompt", "changes_json",
        "latency_ms", "prompt_tokens", "completion_tokens", "status", "error", "cached", "kind",
    )
    values = [record.get(c) for c in columns]
    with _lock, closing(_connect()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO requests ({}) VALUES ({})".format(
                ", ".join(columns), ", ".join("?" for _ in columns)
            ),
            values,
        )
        conn.commit()


def _brief(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "model": row["model"],
        "scene": row["scene"],
        "input": (row["input"] or "")[:120],
        "preview": (row["result_prompt"] or "")[:120],
        "status": row["status"],
        "cached": bool(row["cached"]),
        "latency_ms": row["latency_ms"],
        "kind": row["kind"] or "rewrite",
    }


def history(limit: int = 20, kind: str = "") -> list[dict]:
    limit = max(1, min(limit, 100))
    with _lock, closing(_connect()) as conn:
        if kind:
            rows = conn.execute(
                "SELECT * FROM requests WHERE COALESCE(kind, 'rewrite') = ? "
                "ORDER BY created_at DESC LIMIT ?", (kind, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM requests ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [_brief(r) for r in rows]


def history_get(item_id: str):
    with _lock, closing(_connect()) as conn:
        row = conn.execute("SELECT * FROM requests WHERE id = ?", (item_id,)).fetchone()
    if not row:
        return None
    data = dict(row)
    try:
        data["changes"] = json.loads(data.pop("changes_json") or "[]")
    except json.JSONDecodeError:
        data["changes"] = []
    return data


def history_delete(item_id: str) -> bool:
    with _lock, closing(_connect()) as conn:
        cur = conn.execute("DELETE FROM requests WHERE id = ?", (item_id,))
        conn.commit()
    return cur.rowcount > 0


def history_clear(kind: str = "") -> int:
    with _lock, closing(_connect()) as conn:
        if kind:
            cur = conn.execute("DELETE FROM requests WHERE COALESCE(kind, 'rewrite') = ?", (kind,))
        else:
            cur = conn.execute("DELETE FROM requests")
        conn.commit()
    return cur.rowcount
