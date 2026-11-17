# -*- coding: utf-8 -*-
"""Prompt Assistant 应用装配入口。

只做三件事：初始化（目录/日志/数据库）、挂路由、提供页面。
业务逻辑都在 routes.py / llm.py / rules.py，以后加模块不用动这里的结构。
"""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import config
import store
from routes import router

config.ensure_dirs()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s [%(name)s]  %(message)s",
    handlers=[
        RotatingFileHandler(
            config.LOG_DIR / "studio.log", maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)
logging.getLogger("studio").setLevel(logging.INFO)

store.init_db()

app = FastAPI(title="Prompt Assistant", version=config.VERSION)
app.include_router(router)
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(config.STATIC_DIR / "index.html")
