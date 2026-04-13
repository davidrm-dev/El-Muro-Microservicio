import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import py_eureka_client.eureka_client as eureka_client
import httpx
import traceback
import logging

from app.config import get_settings

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de ciclo de vida de la aplicación"""
    # Startup
    eureka_client.init(
        eureka_server=settings.eureka_server,
        app_name="api-gateway",
        instance_port=settings.service_port
    )
    print("✅ API Gateway registrado en Eureka")
    yield
    # Shutdown
    eureka_client.stop()
    print("🛑 API Gateway detenido")

app = FastAPI(
    title="API Gateway",
    description="Punto de entrada único para los microservicios de El Muro.",
    version="1.0.0",
    lifespan=lifespan
)

def get_service_url(service_name: str) -> str:
    """Obtiene la URL de un servicio desde Eureka."""
    try:
        service_info = eureka_client.get_application(
            app_name=service_name,
            eureka_server=settings.eureka_server
        )
        if not service_info or not service_info.instances:
            raise HTTPException(status_code=503, detail=f"Servicio '{service_name}' no disponible.")
        
        # Idealmente, aquí habría lógica de balanceo de carga.
        # Por simplicidad, tomamos la primera instancia.
        instance = service_info.instances[0]
        # El puerto está en instance.port que es un PortWrapper
        # Accedemos al valor interno correctamente
        if hasattr(instance.port, '__dict__'):
            port_dict = instance.port.__dict__
            port = port_dict.get('$', port_dict.get('port', 8000))
        else:
            port = str(instance.port)
            if port.startswith('<'):
                port = 8000  # Default si no podemos extraer
            else:
                port = int(port)
        
        logger.info(f"Servicio {service_name}: IP={instance.ipAddr}, Puerto={port}")
        
        # Usamos la IP que Eureka devuelve, que funciona dentro de la red Docker
        ip_addr = instance.ipAddr
        return f"http://{ip_addr}:{port}"
    except Exception as e:
        logger.error(f"Error en get_service_url: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=503, detail=f"Error al contactar Eureka para el servicio '{service_name}': {e}")

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def reverse_proxy(request: Request, service_name: str, path: str):
    """Redirige las peticiones al microservicio correspondiente."""
    
    # Mapeo de nombres de ruta a nombres de servicio en Eureka
    service_map = {
        "carreras": "CARRERAS-SERVICE",
        "materias": "MATERIAS-SERVICE",
        "auth": "AUTH-SERVICE",
        "posts": "POSTS-SERVICE",
        "temas": "TEMAS-SERVICE"
    }
    
    eureka_app_name = service_map.get(service_name.lower())
    
    if not eureka_app_name:
        raise HTTPException(status_code=404, detail=f"Ruta de servicio '{service_name}' no encontrada.")

    base_url = get_service_url(eureka_app_name)
    # Las rutas de los microservicios están bajo /api/{service_name}/
    url = f"{base_url}/api/{service_name}/{path}"
    
    logger.info(f"Redirigiendo petición a: {url}")
    
    headers = dict(request.headers)
    # Remover headers que no deben ser forwarded
    headers.pop("host", None)

    try:
        body = await request.body()
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=60.0,
            )
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
    except Exception as e:
        logger.error(f"Error en reverse proxy: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error al contactar el servicio '{eureka_app_name}': {str(e)}")

@app.get("/")
def root():
    return {"message": "API Gateway está funcionando"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.service_port)
