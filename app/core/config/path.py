from pathlib import Path

from loguru import logger
from pydantic import model_validator


class PathConfig:
    """文件路径配置"""

    APP_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = APP_DIR.parent / "static"

    @model_validator(mode="after")
    def ensure_directories_exist(self):
        """确保所有配置的目录都存在"""
        directories = [self.STATIC_DIR]

        for directory in directories:
            if directory.exists():
                logger.debug(f"目录已存在: {directory}")
            else:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建目录: {directory}")

        return self
