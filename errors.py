# -*- coding: utf-8 -*-
"""把上游异常转换成可展示给用户的中文提示。

界面上不出现上游原始报文与 key；完整错误只写本地日志。
"""
from __future__ import annotations

import requests


class StudioError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False, http_status: int = 500):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable
        self.http_status = http_status

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }


class ConfigError(StudioError):
    def __init__(self, message: str | None = None):
        super().__init__(
            "config",
            message or "还没配置 DeepSeek key。请在项目目录的 .env 里填入 DEEPSEEK_API_KEY，然后重启服务。",
            False,
            500,
        )


class BusyError(StudioError):
    def __init__(self, limit: int):
        super().__init__(
            "busy",
            "同时最多处理 {} 个改写请求，等前一个完成再试。".format(limit),
            True,
            429,
        )


def from_response(status: int, body: str) -> StudioError:
    """按 DeepSeek 的状态码分类，401/402 不重试，429/5xx 可重试。"""
    raw = body or ""
    lowered = raw.lower()
    if status == 401:
        return StudioError("auth", "API key 无效或已失效，请重新填一次 key 再试。", False, 401)
    if status == 402 or "insufficient_balance" in lowered or "余额不足" in raw:
        return StudioError(
            "balance",
            "DeepSeek 账户余额不足，去 platform.deepseek.com 充值后再试。",
            False,
            402,
        )
    if status == 429:
        return StudioError("rate_limit", "请求有点频繁，稍等几秒再试一次。", True, 429)
    if status >= 500:
        return StudioError("upstream", "DeepSeek 服务暂时不可用，稍后再试。", True, 502)
    return StudioError(
        "upstream", "DeepSeek 返回了未预期的响应（{}），稍后再试。".format(status), True, 502
    )


def from_exception(exc: Exception) -> StudioError:
    """兜底：界面只给异常类型，完整堆栈写日志。"""
    if isinstance(exc, StudioError):
        return exc
    if isinstance(exc, requests.Timeout):
        return StudioError("timeout", "请求超时了，检查网络后再试一次。", True, 504)
    if isinstance(exc, requests.ConnectionError):
        return StudioError("network", "连不上 DeepSeek，检查网络或代理设置。", True, 502)
    return StudioError("unknown", "改写没能完成（{}），再试一次。".format(type(exc).__name__), True, 500)
