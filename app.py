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


@app.middleware("http")
async def no_cache_static(request, call_next):
    """本地静态资源不缓存：改完代码刷新即生效，不会被浏览器旧副本盖住。

    A local tool is edited constantly; serving JS/CSS from cache after an
    update is more confusing than the few milliseconds it saves.
    """
    response = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


app.include_router(router)
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(config.STATIC_DIR / "index.html")
