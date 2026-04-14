from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import mongo_manager
from app.core.eureka import register_with_eureka, stop_eureka_client
from app.routers.temas import router as temas_router

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    mongo_manager.connect()
    await register_with_eureka()
    yield
    await stop_eureka_client()
    mongo_manager.disconnect()


app = FastAPI(
    title="Temas Service",
    description="Microservicio de gestion de temas para El Muro",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(temas_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "service": settings.service_name,
        "status": "healthy",
    }
