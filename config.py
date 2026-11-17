# -*- coding: utf-8 -*-
"""集中配置：路径、环境变量、dev/prod 开关。

所有可调项都在这里，改配置不用翻业务代码。
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # 标准库兜底：没装依赖时也能读 .env
    def load_dotenv(path):
        p = Path(path)
        if not p.exists():
            return False
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
        return True

ROOT = Path(__file__).resolve().parent
RULES_FILE = ROOT / "rules_data.json"
DB_FILE = ROOT / "data" / "studio.db"
LOG_DIR = ROOT / "logs"
STATIC_DIR = ROOT / "static"

# 显式指定路径，避免从别的目录启动时读不到 .env
load_dotenv(ROOT / ".env")

DEEPSEEK_BASE = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 单次上游调用超时（秒）
REQUEST_TIMEOUT = float(os.environ.get("REQUEST_TIMEOUT", "90"))
# 同时最多处理几个改写请求，防止 key 被误刷
MAX_CONCURRENCY = max(1, int(os.environ.get("MAX_CONCURRENCY", "2")))
# 结果缓存有效期（秒），0 = 关闭缓存
CACHE_TTL = float(os.environ.get("CACHE_TTL", "86400"))
# dev：开放规则热重载接口；prod 保持关闭
DEV_MODE = os.environ.get("DEV_MODE", "0") == "1"


def api_key() -> str:
    return os.environ.get("DEEPSEEK_API_KEY", "").strip()


def ensure_dirs() -> None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
