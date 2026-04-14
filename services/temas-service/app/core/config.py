from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for temas-service."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "temas-service"
    service_port: int = 8003
    environment: str = "development"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_database: str = "temas_db"
    temas_collection: str = "temas"

    secret_key: str = "change-this-shared-jwt-secret"
    algorithm: str = "HS256"

    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])

    materias_service_name: str = "materias-service"
    posts_service_name: str = "posts-service"

    eureka_enabled: bool = True
    eureka_server_url: str = "http://localhost:8761/eureka/"
    eureka_instance_host: str = "localhost"
    eureka_instance_ip: str = "127.0.0.1"

    request_timeout_seconds: float = 5.0


@lru_cache()
def get_settings() -> Settings:
    return Settings()
