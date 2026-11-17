# -*- coding: utf-8 -*-
"""HTTP 接口冒烟测试：不调用任何真实上游，只验证校验分支与元信息。"""
from __future__ import annotations

import pytest

import config

pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from app import app  # noqa: E402

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == config.VERSION
    assert body["rules_loaded"] > 0
    assert body["active_requests"] == 0


def test_index_page():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Prompt Assistant" in resp.text


def test_options_exposes_four_models():
    body = client.get("/api/options").json()
    assert len(body["models"]) == 4
    assert all("video" in m for m in body["models"])
    assert "history" in body["features"]


def test_rewrite_rejects_empty_prompt():
    resp = client.post("/api/rewrite", json={"prompt": "   ", "model": "gpt-image"})
    assert resp.status_code == 400
    assert resp.json()["code"] == "empty"


def test_rewrite_rejects_unknown_model():
    resp = client.post("/api/rewrite", json={"prompt": "一只猫", "model": "not-a-model"})
    assert resp.status_code == 400
    assert resp.json()["code"] == "unknown_model"


def test_stream_rejects_empty_prompt():
    resp = client.post("/api/stream", json={"prompt": "", "model": "gpt-image"})
    assert resp.status_code == 400


def test_reload_forbidden_in_prod():
    resp = client.post("/api/admin/reload")
    assert resp.status_code == 403


def test_history_endpoints_on_empty_db():
    assert client.get("/api/history").json() == {"items": []}
    assert client.delete("/api/history").json() == {"deleted": 0}
    assert client.get("/api/history/no-such-id").status_code == 404
