from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HR Operations Brain API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/hr_brain"
    object_storage_bucket: str = "hr-brain-dev"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    data_dir: str = "data"
    upload_dir: str = "uploads"
    ingestion_store_filename: str = "ingestion_store.json"
    embedding_store_filename: str = "embedding_store.json"
    extraction_store_filename: str = "extraction_store.json"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HR_BRAIN_")

    @property
    def data_dir_path(self) -> Path:
        return Path(self.data_dir).resolve()

    @property
    def upload_dir_path(self) -> Path:
        return self.data_dir_path / self.upload_dir

    @property
    def ingestion_store_path(self) -> Path:
        return self.data_dir_path / self.ingestion_store_filename

    @property
    def embedding_store_path(self) -> Path:
        return self.data_dir_path / self.embedding_store_filename

    @property
    def extraction_store_path(self) -> Path:
        return self.data_dir_path / self.extraction_store_filename


settings = Settings()
