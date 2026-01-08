from urllib.parse import quote_plus

from pydantic import computed_field


class DatabaseConfig:
    """数据库配置"""

    # PostgreSQL
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str
    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """异步 SQLAlchemy 数据库连接 URL"""
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        uri = (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{encoded_password}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        return uri

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        """Redis 连接 URL"""
        encoded_password = quote_plus(self.REDIS_PASSWORD)
        uri = f"redis://:{encoded_password}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return uri
