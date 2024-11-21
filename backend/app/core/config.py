from pydantic import BaseSettings
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AutoML Web Platform"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./storage/automl.db"

    # 文件存储路径
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    MODEL_DIR: Path = BASE_DIR / "storage" / "models"
    RESULT_DIR: Path = BASE_DIR / "storage" / "results"

    # 训练配置
    DEFAULT_TIME_LIMIT: int = 3600
    MAX_TIME_LIMIT: int = 7200

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# 确保存储目录存在
for path in [settings.UPLOAD_DIR, settings.MODEL_DIR, settings.RESULT_DIR]:
    path.mkdir(parents=True, exist_ok=True) 