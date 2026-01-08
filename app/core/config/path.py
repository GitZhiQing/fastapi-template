from pathlib import Path


class PathConfig:
    """文件路径配置"""

    APP_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = APP_DIR.parent / "static"
