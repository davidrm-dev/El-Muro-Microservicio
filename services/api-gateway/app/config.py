from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración del API Gateway"""
    
    # Service
    service_name: str = "api-gateway"
    service_port: int = 8000
    environment: str = "development"
    
    # Eureka
    eureka_server: str = "http://eureka-server:8761/eureka/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
