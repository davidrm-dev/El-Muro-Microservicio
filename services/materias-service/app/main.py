from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import materias

settings = get_settings()


# Crear tablas al iniciar
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de ciclo de vida de la aplicación"""
    # Startup
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada")
    yield
    # Shutdown
    print("🛑 Aplicación cerrada")


# Crear aplicación FastAPI
app = FastAPI(
    title="Materias Service",
    description="Microservicio de gestión de materias y temas para El Muro",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(materias.router)


@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "service": "materias-service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "service": "materias-service",
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.service_port
    )
