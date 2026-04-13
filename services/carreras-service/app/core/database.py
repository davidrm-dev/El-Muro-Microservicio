from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from typing import Generator
from app.core.config import get_settings

settings = get_settings()

# Crear engine
engine = create_engine(
    settings.database_url,
    echo=settings.environment == "development",
    poolclass=NullPool if "sqlite" in settings.database_url else None,
)

# Session local
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base para los modelos
Base = declarative_base()


def get_db() -> Generator:
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Event listener para ejecutar migraciones automáticamente
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Ejecutar migraciones al conectar"""
    pass
