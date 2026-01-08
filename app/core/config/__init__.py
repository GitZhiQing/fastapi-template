import os
from functools import lru_cache
from typing import Literal

from loguru import logger
from pydantic import ValidationError, computed_field
from pydantic_settings import BaseSettings

from .database import DatabaseConfig
from .path import PathConfig


class Settings(BaseSettings, DatabaseConfig, PathConfig):
    # 应用配置
    APP_NAME: str = "FastAPI Template"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    # 超级管理员信息
    SUPERADMIN_NAME: str
    SUPERADMIN_EMAIL: str
    SUPERADMIN_PASSWORD: str
    # JWT 配置
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DELTA_SECONDS: int = 60 * 30  # 30 分钟
    REFRESH_TOKEN_EXPIRE_DELTA_SECONDS: int = 60 * 60 * 24 * 7  # 7 天
    # 后端服务绑定地址，用于 uvicorn 启动服务
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080
    # 后端 API 访问地址，用于生成外部可访问的资源 URL
    PUBLIC_HOST: str = "127.0.0.1"
    PUBLIC_PORT: int = 8080
    PUBLIC_SCHEME: Literal["http", "https"] = "http"
    API_PREFIX: str = "/api"
    SECRET_KEY: str  # !必须提供
    # 客户端 URL 列表，用于 CORS 配置
    CLIENT_URLS: list[str] = ["http://localhost:5173"]

    @computed_field
    @property
    def PUBLIC_URL(self) -> str:
        """完整的公共 URL"""
        if self.PUBLIC_PORT in (80, 443):
            return f"{self.PUBLIC_SCHEME}://{self.PUBLIC_HOST}"
        return f"{self.PUBLIC_SCHEME}://{self.PUBLIC_HOST}:{self.PUBLIC_PORT}"

    @computed_field
    @property
    def ALLOW_ORIGINS(self) -> list[str]:
        """允许的跨域 URL 列表（前端+后端访问地址），用于 CORS 配置"""
        origins = self.CLIENT_URLS + [self.PUBLIC_URL]
        return list(set(origins))

    @property
    def DEBUG(self) -> bool:
        """调试模式: 优先使用环境变量 DEBUG, 否则根据 APP_ENV 判断"""
        debug_env = os.getenv("DEBUG")
        if debug_env is not None:
            # 支持多种布尔值表示: true/false, 1/0, yes/no, on/off
            return debug_env.lower() in ("true", "1", "yes", "on")
        return self.APP_ENV == "development"

    @computed_field
    @property
    def WORKERS(self) -> int:
        """工作进程数：生产环境多进程，其他环境单进程"""
        workers_env = os.getenv("WORKERS")
        if workers_env is not None:
            return int(workers_env)
        return 4 if self.APP_ENV == "production" else 1


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        logger.error(f"配置导入错误: {e}")
        # 分析具体的错误原因
        missing_vars = []  # 缺失变量
        invalid_vars = []  # 无效变量
        for error in e.errors():
            field_name = error.get("loc", [""])[0] if error.get("loc") else ""
            error_type = error.get("type", "")
            if error_type == "missing":
                missing_vars.append(field_name)
            else:
                invalid_vars.append(f"{field_name}: {error.get('msg', '验证失败')}")
        if missing_vars:
            logger.error(f"[!] 缺失环境变量: {', '.join(missing_vars)}")
        if invalid_vars:
            logger.error(f"[!] 无效环境变量: {', '.join(invalid_vars)}")
        exit(1)
