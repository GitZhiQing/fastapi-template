from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .config import get_settings

settings = get_settings()


class AppLifespanManager:
    async def startup(self):
        """应用启动时执行"""
        logger.info("启动应用...")
        logger.info(f"当前环境: {settings.APP_ENV}")
        logger.info(f"访问地址: {settings.PUBLIC_URL}")

    async def shutdown(self):
        """应用关闭时执行"""
        logger.info("关闭应用...")


app_lifespan_manager = AppLifespanManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        await app_lifespan_manager.startup()
        yield
    finally:
        await app_lifespan_manager.shutdown()
