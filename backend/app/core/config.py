import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

os.environ.setdefault("CREWAI_STORAGE_DIR", str(Path(__file__).resolve().parents[3] / ".runtime"))
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["CREWAI_TRACING_ENABLED"] = "false"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env", extra="ignore"
    )
    database_url: str = "postgresql+psycopg://revenueops:local-only@localhost:55433/revenueops"
    app_env: str = "development"
    jwt_secret: str = "local-development-only-replace-this-secret"
    demo_enabled: bool = True
    model_mode: str = "baseline"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    hosted_model: str = ""
    hosted_enabled: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    def validate_runtime(self):
        if self.app_env == "production":
            if (
                self.demo_enabled
                or self.jwt_secret.startswith(("local-", "replace-"))
                or len(self.jwt_secret) < 32
            ):
                raise ValueError("Production requires demo disabled and a strong JWT secret")
            if not self.database_url.startswith("postgresql"):
                raise ValueError("Production requires PostgreSQL")


settings = Settings()
