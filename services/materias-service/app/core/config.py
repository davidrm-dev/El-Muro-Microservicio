from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Database
    database_url: str = "postgresql://usuario:password@localhost:5432/materias_db"
    
    # Service
    service_name: str = "materias-service"
    service_port: int = 8002
    environment: str = "development"
    
    # JWT (para integración futura)
    jwt_secret: str = "your-secret-key-change-in-production"
    secret_key: Optional[str] = None  # Para compatibilidad
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: list = ["*"]
    
    # Otros servicios
    carreras_service_url: str = "http://carreras-service:8001"
    usuarios_service_url: str = "http://usuarios-service:8003"
    
    def __init__(self, **data):
        super().__init__(**data)
        # Si secret_key no se proporciona, usar jwt_secret
        if not self.secret_key:
            self.secret_key = self.jwt_secret
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
