from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .config import get_settings
from .database import async_engine, redis_client

settings = get_settings()


class AppLifespanManager:
    async def startup(self):
        """应用启动时执行"""
        logger.info("启动应用...")
        logger.info(f"当前环境: {settings.APP_ENV}")
        logger.info(f"调试模式: {settings.DEBUG}")
        logger.info(f"服务绑定: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
        logger.info(f"访问地址: {settings.PUBLIC_URL}")

    async def shutdown(self):
        """应用关闭时执行"""
        logger.info("关闭应用...")
        logger.info("释放数据库连接...")
        await async_engine.dispose()
        logger.info("释放 Redis 连接...")
        await redis_client.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    app_lifespan_manager = AppLifespanManager()
    try:
        await app_lifespan_manager.startup()
        yield
    finally:
        await app_lifespan_manager.shutdown()
