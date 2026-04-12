from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://usuario:password@localhost:5432/materias_db"
    )
    
    # Service
    service_name: str = "materias-service"
    service_port: int = 8002
    environment: str = "development"
    
    # JWT (para integración futura)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list = ["*"]
    
    # Otros servicios
    carreras_service_url: str = "http://carreras-service:8001"
    usuarios_service_url: str = "http://usuarios-service:8003"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
