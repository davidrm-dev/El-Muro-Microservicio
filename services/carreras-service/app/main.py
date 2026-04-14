import py_eureka_client.eureka_client as eureka_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import carreras

settings = get_settings()


# Crear tablas al iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de ciclo de vida de la aplicación"""
    # Startup
    eureka_client.init(
        eureka_server=settings.eureka_server,
        app_name=settings.service_name,
        instance_port=settings.service_port
    )
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")
    yield
    # Shutdown
    eureka_client.stop()
    print("🛑 Aplicación cerrada")


# Crear aplicación FastAPI
app = FastAPI(
    title="Carreras Service",
    description="Microservicio de gestión de carreras para El Muro",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(carreras.router)


@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "service": "carreras-service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "service": "carreras-service",
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.service_port
    )
