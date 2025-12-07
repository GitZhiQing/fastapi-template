import os
from datetime import timedelta
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
    APP_VERSION: str = "0.1.0"
    # 服务绑定配置 (容器内部), 用于 uvicorn 启动服务
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080
    # 公共 URL 配置 (外部访问), 用于生成对外可见的资源 URL
    PUBLIC_HOST: str = "127.0.0.1"
    PUBLIC_PORT: int = 8080
    PUBLIC_SCHEME: Literal["http", "https"] = "http"
    API_PREFIX: str = "/api"
    SECRET_KEY: str  # !必须提供

    @computed_field
    @property
    def PUBLIC_URL(self) -> str:
        return f"{self.PUBLIC_SCHEME}://{self.PUBLIC_HOST}:{self.PUBLIC_PORT}"

    @computed_field
    @property
    def DEBUG(self) -> bool:
        """调试模式：仅在开发环境启用"""
        return True if self.APP_ENV == "development" else False

    @computed_field
    @property
    def WORKERS(self) -> int:
        """工作进程数：生产环境多进程，其他环境单进程"""
        return 4 if self.APP_ENV == "production" else 1

    # 超级管理员信息
    SUPERADMIN_NAME: str
    SUPERADMIN_EMAIL: str
    SUPERADMIN_PASSWORD: str

    # CORS 配置
    FRONTEND_URL: str = "http://localhost:5173"  # 前端 URL
    ALLOWED_CORS_URLS: list[str] = []  # 允许跨域的 URL 列表

    # 文件路径配置
    APP_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = APP_DIR.parent / "static"

    @computed_field
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        public_url = f"{self.PUBLIC_SCHEME}://{self.PUBLIC_HOST}"
        if self.PUBLIC_PORT not in (80, 443):
            public_url += f":{self.PUBLIC_PORT}"
        origins = [self.FRONTEND_URL, public_url]
        origins.extend(self.ALLOWED_CORS_URLS)
        return list(set(origins))

    # JWT 配置
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DELTA: timedelta = timedelta(hours=1)
    REFRESH_TOKEN_EXPIRE_DELTA: timedelta = timedelta(days=1)

    # 数据库配置 - PostgreSQL
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    # 数据库配置 - Redis
    REDIS_DB: int = 0
    REDIS_PASSWORD: str
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def IS_DOCKER_ENV(self) -> bool:
        """检测是否运行在 Docker 环境中"""
        return os.path.exists("/.dockerenv")

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
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
