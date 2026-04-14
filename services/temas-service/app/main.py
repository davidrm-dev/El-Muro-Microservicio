import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import mongo_manager
from app.core.eureka import register_with_eureka, stop_eureka_client
from app.routers.temas import router as temas_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.get("/test-jwt")
def test_jwt(authorization: str | None = Header(default=None)):
    """Debug endpoint to test JWT token."""
    import jwt
    from app.core.config import get_settings
    
    settings = get_settings()
    logger.info(f"TEST JWT: Secret key = {settings.secret_key}")
    logger.info(f"TEST JWT: Authorization header = {authorization}")
    
    if not authorization:
        return {"error": "No authorization header"}
    
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return {"error": "Invalid scheme"}
        
        logger.info(f"TEST JWT: Token = {token}")
        decoded = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        logger.info(f"TEST JWT: Successfully decoded: {decoded}")
        return {"success": True, "decoded": decoded}
    except Exception as e:
        logger.error(f"TEST JWT: Error: {type(e).__name__}: {e}")
        return {"error": str(e), "type": type(e).__name__}


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "service": "temas-service",
        "status": "healthy",
    }
