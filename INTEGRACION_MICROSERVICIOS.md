# 🔗 Guía de Integración entre Microservicios

## 📌 Relación Carreras ↔ Materias

### Escenario Actual (Arquitectura Actual)

```
╔═══════════════════════════════════════════════════════════════╗
║              EL MURO - MICROSERVICIOS PLATFORM                ║
╚═══════════════════════════════════════════════════════════════╝

 SEPARACIÓN COMPLETA DE DATOS (Database-per-Service Pattern)

┌─────────────────────────────────────────────────────────────┐
│  CARRERAS SERVICE (Puerto 8001)                             │
├─────────────────────────────────────────────────────────────┤
│  DATABASE: carreras_db (PostgreSQL 15 - Puerto 5432)        │
│  HOST: carreras-db                                          │
│  ├── Tabla: carreras                                        │
│  │   ├── id (PK)
│  │   ├── nombre (UNIQUE)
│  │   ├── descripción
│  │   └── timestamps                                         │
│  └── Tabla: materias                                        │
│      ├── id (PK)                                            │
│      ├── nombre                                             │
│      ├── semestre                                           │
│      ├── carrera_id (FK → carreras.id)                     │
│      └── timestamps                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  MATERIAS SERVICE (Puerto 8002)                             │
├─────────────────────────────────────────────────────────────┤
│  DATABASE: materias_db (PostgreSQL 15 - Puerto 5433)        │
│  HOST: materias-db                                          │
│  ├── Tabla: materias                                        │
│  │   ├── id (PK)                                            │
│  │   ├── nombre                                             │
│  │   ├── descripción                                        │
│  │   ├── semestre                                           │
│  │   ├── carrera_id (referencia, NO FK)                    │
│  │   └── timestamps                                         │
│  └── Tabla: temas                                           │
│      ├── id (PK)                                            │
│      ├── nombre                                             │
│      ├── descripción                                        │
│      ├── materia_id (FK → materias.id)                     │
│      └── timestamps                                         │
└─────────────────────────────────────────────────────────────┘

⚠️ IMPORTANTE:
   • DOS bases de datos COMPLETAMENTE INDEPENDIENTES
   • DOS espacios de almacenamiento SEPARADOS
   • TWO PostgreSQL instances ejecutándose en paralelo
   • CERO compartición de datos a nivel de BD
   • Los servicios comunican SOLO vía HTTP REST API
```

---

## 🔀 Dos Formas de Integración

### Opción 1: Por Foreign Key (Actual) ⭐ RECOMENDADO

**Implementado en:**
- `carreras-service`: Tabla `materias` con FK a `carreras.id`
- `materias-service`: Campo `carrera_id` (referencia, no FK)

**Ventajas:**
- ✅ Simple de implementar
- ✅ Integridad referencial automática
- ✅ Sin latencia de red
- ✅ Sin dependencias de servicios externos
- ✅ Escalable horizontalmente

**Desventajas:**
- ❌ Datos duplicados entre servicios
- ❌ Debe mantenerse consistencia manual

**Diagrama:**

```
carreras_db.materias
    carrera_id (FK) ──→ carreras_db.carreras.id
    
materias_db.materias
    carrera_id (referencia, sin FK) ─ sin validación BD
```

**Implementación en Python:**

```python
# En materias-service:
# La validación se hace a nivel de aplicación, no BD

db_materia = Materia(
    nombre=materia_data.nombre,
    semestre=materia_data.semestre,
    carrera_id=materia_data.carrera_id  # Sin FK, solo referencia
)
```

### Opción 2: Por API REST (Preparada)

**Cliente HTTP implementado en:**
- `materias-service/app/core/external_services.py`

**Ventajas:**
- ✅ Desacoplamiento total
- ✅ Cada servicio es independiente
- ✅ Patrón microservicios "puro"
- ✅ Escalable en orden de depedencias

**Desventajas:**
- ❌ Latencia de red
- ❌ Dependencia del servicio externo
- ❌ Posibles fallos de conectividad
- ❌ Necesita timeout handling

**Código (Comentado):**

```python
# En materias_service.py - create_materia()

# Descomenta esta sección:
if not CarrerasServiceClient.carrera_exists(materia_data.carrera_id):
    raise HTTPException(status_code=404, detail="Carrera no encontrada")

db_materia = Materia(...)
```

**Cliente HTTP:**

```python
class CarrerasServiceClient:
    BASE_URL = "http://carreras-service:8001"  # URL Docker
    
    @staticmethod
    def carrera_exists(carrera_id: int) -> bool:
        try:
            url = f"{CarrerasServiceClient.BASE_URL}/api/carreras/{carrera_id}"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False  # Default: asumir que existe (failure-open)
```

---

## 📊 Comparación de Integraciones

| Característica | Foreign Key | API REST |
|---|---|---|
| **Complejidad** | Simple | Media |
| **Latencia** | 0ms | 50-200ms |
| **Acoplamiento** | Medio | Bajo |
| **Escalabilidad** | Alta | Alta |
| **Tolerancia a Fallos** | Alta | Baja |
| **Consistencia** | Fuerte (BD) | Eventual |
| **Recomendado para** | Datos críticos | Consultas |

---

## 🚀 Cómo Activar API REST

### Paso 1: Editar materias_service.py

Archivo: `materias-service/app/services/materia_service.py`

```python
from app.core.external_services import CarrerasServiceClient

@staticmethod
def create_materia(db: Session, materia_data: MateriaCreate) -> Materia:
    """Crear una nueva materia"""
    
    # 🔓 DESCOMENTAR ESTAS LÍNEAS:
    if not CarrerasServiceClient.carrera_exists(materia_data.carrera_id):
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    
    # ... resto del código
```

### Paso 2: Reiniciar Servicio

```bash
docker-compose restart materias-service

# O si está en desarrollo:
uvicorn app.main:app --port 8002 --reload
```

### Paso 3: Probar

```bash
# Crear materia con carrera válida
curl -X POST http://localhost:8002/api/materias/crear \
  -H "x-role: ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","semestre":1,"carrera_id":1}'

# Crear materia con carrera inválida (debe fallar)
curl -X POST http://localhost:8002/api/materias/crear \
  -H "x-role: ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","semestre":1,"carrera_id":9999}'
```

---

## 🔄 Sincronización de Datos

### Escenario: Eliminar Carrera

**Problema:**
```
Elimino carrera ID=1
  ├─ Se elimina de carreras_db.carreras
  ├─ Se eliminan materias asociadas en carreras_db.materias
  └─ materias_db.materias seguirá teniendo carrera_id=1 (huérfano)
```

**Soluciones:**

#### Opción A: Cascade Delete (Recomendado)

```python
# En carreras-service/app/models/carrera.py

class Carrera(Base):
    materias = relationship(
        "Materia", 
        cascade="all, delete-orphan"  # Elimina materias automáticamente
    )
```

#### Opción B: Sincronización Manual

```python
# webhook que llama a materias-service cuando se elimina carrera

@router.delete("/{carrera_id}")
def eliminar_carrera(carrera_id: int, db: Session):
    # Eliminar localmente
    carrera = db.query(Carrera).get(carrera_id)
    db.delete(carrera)
    db.commit()
    
    # Notificar a otros servicios
    try:
        requests.delete(
            f"{settings.materias_service_url}/api/materias/carrera/{carrera_id}",
            timeout=5
        )
    except Exception:
        pass  # Log error, pero no fallar
```

#### Opción C: Event Sourcing

```python
# Crear evento que se procesa asincronamente
# (Para futura implementación con RabbitMQ/Kafka)

class CarreraDeletedEvent:
    carrera_id: int
    timestamp: datetime
```

---

## 🏗️ Preparación para Futuros Servicios

### Usuarios Service (Próximo)

```
POST /api/usuarios/crear
{
  "email": "estudiante@uptc.edu.co",
  "nombre": "Juan",
  "rol": "ESTUDIANTE|ADMIN|PROFESOR"
}

GET /api/usuarios/{id}
GET /api/usuarios/by-email/{email}
```

**Integración con Materias:**

```python
# En materias-service cuando alguien publica una pregunta

class Pregunta(Base):
    usuario_id: int  # Referencia a usuarios-service
    materia_id: int  # FK local
    
# Al crear pregunta:
# 1. Validar usuario existe (API call)
# 2. Validar materia existe (local FK o API)
# 3. Insertar pregunta
```

### Posts Service

```
GET /api/posts/search?materia_id=1
POST /api/posts/crear
{
  "usuario_id": 1,
  "materia_id": 1,
  "tema_id": 1,
  "titulo": "¿Cómo funcionan los arrays?",
  "contenido": "..."
}
```

---

## 🔐 Service-to-Service Communication

### Con JWT (Recomendado)

```python
# Cuando un servicio llama a otro:

headers = {
    "Authorization": f"Bearer {service_token}",
    "X-Service-ID": "materias-service"
}

response = requests.get(
    f"{carreras_service_url}/api/carreras/{id}",
    headers=headers,
    timeout=5
)
```

### Con API Keys

```python
# Alternativa más simple:

headers = {
    "X-API-Key": "materias-service-key-xyz123",
}
```

### Implementación de Validación en Carreras-service

```python
# En carreras-service/app/core/security.py

VALID_SERVICES = {
    "materias-service": "materias-service-key-xyz123",
    "posts-service": "posts-service-key-xyz123",
    "usuarios-service": "usuarios-service-key-xyz123",
}

async def verify_service_token(
    x_api_key: str = Header(None)
) -> str:
    if x_api_key not in VALID_SERVICES.values():
        raise HTTPException(status_code=401, detail="Invalid service token")
    
    # Retornar nombre del servicio
    return [k for k, v in VALID_SERVICES.items() if v == x_api_key][0]

# En endpoints internos:
@router.get("/internal/carreras/{carrera_id}")
async def get_carrera_internal(
    carrera_id: int,
    service: str = Depends(verify_service_token)
):
    # Solo servicios autenticados pueden acceder
    ...
```

---

## 📈 Escalabilidad Horizontal

### Con Docker Compose (Múltiples instancias)

```yaml
# En docker-compose.yml

services:
  carreras-service:
    # ... config
    deploy:
      replicas: 3
  
  materias-service:
    # ... config
    deploy:
      replicas: 2
```

### Con Load Balancer (Nginx)

```nginx
# nginx.conf

upstream carreras {
    server carreras-service:8001;
    server carreras-service:8001;  # Replica
}

upstream materias {
    server materias-service:8002;
    server materias-service:8002;  # Replica
}

server {
    listen 80;
    
    location /carreras {
        proxy_pass http://carreras;
    }
    
    location /materias {
        proxy_pass http://materias;
    }
}
```

---

## 🔍 Monitoring y Logging

### Health Checks Actuales

```bash
# Ejecutar regularmente para diagnosticar

curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Agradar Logs Centralizados (ELK Stack)

```python
# Usando estructuración de logs

import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": record.created,
            "service": "carreras-service",
            "level": record.levelname,
            "message": record.getMessage(),
            "user_id": getattr(record, 'user_id', None),
        })

logging.basicConfig(format=JSONFormatter())
```

---

## 🚨 Manejo de Errores

### Circuit Breaker Pattern

```python
from pybreaker import CircuitBreaker

carreras_breaker = CircuitBreaker(
    fail_max=5,
    reset_timeout=60
)

@carreras_breaker
def get_carrera(carrera_id):
    return requests.get(
        f"{CARRERAS_URL}/api/carreras/{carrera_id}",
        timeout=5
    )

# Si el servicio falla 5 veces,
# el circuit breaker se abre automáticamente
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_carreras_service(url):
    return requests.get(url, timeout=5)

# Reintentar hasta 3 veces con espera exponencial
```

---

## 📝 Checklist de Integración

- [ ] Ambos servicios pueden comunicarse (docker network)
- [ ] Health checks responden correctamente
- [ ] FK validadas automáticamente (opción 1)
- [ ] Cliente HTTP funciona (opción 2, si está activada)
- [ ] Eliminaciones en cascada funcionan
- [ ] Logs centralizados configurados
- [ ] Timeouts establecidos
- [ ] Errores de red manejados
- [ ] Load balancer configurado (si necesario)
- [ ] Tests de integración ejecutados

---

## 🎓 Próximos Pasos

1. **Implementar Usuarios Service**
   - Autenticación real
   - Gestión de roles
   - Tokens JWT

2. **Implementar Posts Service**
   - Preguntas por materia
   - Respuestas por tema
   - Votación de contenido

3. **API Gateway**
   - Enrutamiento centralizado
   - Rate limiting
   - Autenticación centralizada

4. **Message Broker** (RabbitMQ/Kafka)
   - Eventos entre servicios
   - Notificaciones
   - Sincronización de datos

5. **Observabilidad**
   - Prometheus (métricas)
   - Jaeger (tracing distribuido)
   - Grafana (dashboards)

---

**Fecha**: Enero 2024
**Versión**: 1.0.0
**Mantenido por**: Equipo de Desarrollo UPTC
