from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import get_settings

settings = get_settings()


def register_middlewares(app: FastAPI):
    """注册中间件"""
    # GZIP：对大于 1024 字节(1KB)的响应进行压缩，提升传输效率
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1024,
    )
    # CORS：允许指定的外部源列表访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,  # 允许的前端地址列表
        allow_credentials=True,  # 允许携带 Cookie 等凭证
        allow_methods=["*"],  # 允许所有 HTTP 方法
        allow_headers=["*"],  # 允许所有请求头
    )
