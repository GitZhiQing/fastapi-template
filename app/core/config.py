import os
from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from loguru import logger
from pydantic import ValidationError, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "FastAPI Template"
    APP_ENV: Literal["development", "testing", "production"] = "development"
    # 服务绑定地址, 用于 uvicorn 启动服务
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080
    # 外部访问地址, 用于生成对外可见的资源 URL
    PUBLIC_HOST: str = "127.0.0.1"
    PUBLIC_PORT: int = 8080
    PUBLIC_SCHEME: Literal["http", "https"] = "http"
    API_PREFIX: str = "/api"
    SECRET_KEY: str  # !必须提供

    # 超级管理员信息
    SUPERADMIN_NAME: str
    SUPERADMIN_EMAIL: str
    SUPERADMIN_PASSWORD: str

    # CORS 配置
    FRONTEND_URL: str = "http://localhost:5173"  # 前端访问地址
    EXTERNAL_URLS: list[str] = []  # 其他外部客户端地址

    # 文件路径配置
    APP_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = APP_DIR.parent / "static"

    # JWT 配置
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DELTA_SECONDS: int = 60 * 30  # 30 分钟
    REFRESH_TOKEN_EXPIRE_DELTA_SECONDS: int = 60 * 60 * 24 * 7  # 7 天
    # 数据库配置 - PostgreSQL
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    # 数据库配置 - Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str

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
        """允许的跨域 URL"""
        origins = [self.PUBLIC_URL, self.FRONTEND_URL]
        origins.extend(self.EXTERNAL_URLS)
        return list(set(origins))

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """异步 SQLAlchemy 数据库连接 URL"""
        # 对密码编码，防止密码中包含的特殊字符导致错误
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{encoded_password}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        """Redis 连接 URL"""
        # 对密码编码，防止密码中包含的特殊字符导致错误
        encoded_password = quote_plus(self.REDIS_PASSWORD)
        return f"redis://:{encoded_password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


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
