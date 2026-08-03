"""
Application configuration.

All settings are read from environment variables (with sane local-dev
defaults) so the same codebase runs unchanged across dev / staging / prod.
Copy `.env.example` to `.env` and adjust values for your environment.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    # --- App ---
    APP_NAME: str = os.getenv("APP_NAME", "DigitalHub API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = _bool(os.getenv("DEBUG"), default=True)

    # --- CORS ---
    CORS_ORIGINS: list = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]

    # --- Database ---
    # Defaults to a local SQLite file so the project runs without a
    # PostgreSQL server. Set DATABASE_URL (or the POSTGRES_* vars below via
    # DB_ENGINE=postgres) to point at real PostgreSQL when available.
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "shopsense")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "shopsense")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "shopsense")

    SQLITE_DB_PATH: Path = BASE_DIR / "shopsense.db"

    @property
    def DATABASE_URL(self) -> str:
        # Allow a full override (e.g. for managed Postgres providers).
        override = os.getenv("DATABASE_URL")
        if override:
            return override
        if self.DB_ENGINE == "postgres":
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return f"sqlite:///{self.SQLITE_DB_PATH}"

    # --- JWT Auth ---
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # --- Storage paths ---
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    CLEANED_DATA_DIR: Path = BASE_DIR / "cleaned_data"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    MLRUNS_DIR: Path = BASE_DIR / "mlruns"
    MODELS_DIR: Path = BASE_DIR / "mlruns" / "registry"

    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    ALLOWED_UPLOAD_EXTENSIONS: tuple = (".csv", ".xlsx", ".xls")

    # --- MLflow ---
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", f"file:///{MLRUNS_DIR}")
    MLFLOW_EXPERIMENT_NAME: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "shopsense")

    def ensure_directories(self) -> None:
        for path in (self.UPLOAD_DIR, self.CLEANED_DATA_DIR, self.REPORTS_DIR, self.MLRUNS_DIR, self.MODELS_DIR):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
