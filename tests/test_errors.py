# -*- coding: utf-8 -*-
"""错误映射测试：确保上游异常永远被翻译成可展示的中文提示，不泄露原文与 key。"""
from __future__ import annotations

import requests

import errors


def test_response_401_is_auth_error():
    err = errors.from_response(401, '{"error":{"message":"invalid api key sk-abc"}}')
    assert err.code == "auth"
    assert err.http_status == 401
    assert err.retryable is False
    assert "sk-abc" not in err.message


def test_response_402_variants_are_balance():
    for status, body in [(402, ""), (400, "insufficient_balance"), (400, "余额不足")]:
        err = errors.from_response(status, body)
        assert err.code == "balance", (status, body)
        assert err.http_status == 402


def test_response_429_is_retryable():
    err = errors.from_response(429, "rate limit")
    assert err.code == "rate_limit"
    assert err.retryable is True
    assert err.http_status == 429


def test_response_5xx_maps_to_upstream_502():
    err = errors.from_response(503, "DeepSeek 内部错误堆栈 secret")
    assert err.code == "upstream"
    assert err.http_status == 502
    assert "secret" not in err.message


def test_exception_mapping():
    assert errors.from_exception(requests.Timeout()).code == "timeout"
    assert errors.from_exception(requests.ConnectionError()).code == "network"
    assert errors.from_exception(ValueError("x")).code == "unknown"

    original = errors.BusyError(2)
    assert errors.from_exception(original) is original  # 已是 StudioError 原样返回


def test_busy_and_config_errors():
    busy = errors.BusyError(3)
    assert busy.code == "busy" and busy.http_status == 429 and busy.retryable
    assert "3" in busy.message

    cfg = errors.ConfigError()
    assert cfg.code == "config" and cfg.retryable is False
    assert "DEEPSEEK_API_KEY" in cfg.message


def test_as_dict_has_no_internal_fields():
    payload = errors.from_response(401, "sk-secret").as_dict()
    assert set(payload) == {"code", "message", "retryable"}
    assert "sk-secret" not in str(payload)
