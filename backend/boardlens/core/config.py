from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOARDLENS_", env_file=".env")

    env: str = "development"
    database_url: str = "sqlite:///./boardlens.db"
    artifact_root: Path = Path("artifacts")
    max_upload_bytes: int = 15 * 1024 * 1024
    allowed_origins: str = "http://localhost:5173"
    model_config_path: Path = Path("configs/models.yaml")
    product_config: Path = Path("configs/products.yaml")


@lru_cache
def get_settings() -> Settings:
    return Settings()
