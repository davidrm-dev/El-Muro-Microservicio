# 🎓 El Muro - Arquitectura de Microservicios

**Plataforma académica tipo Brainly para la UPTC sede central**, basada en arquitectura de microservicios con **DOS BASES DE DATOS COMPLETAMENTE INDEPENDIENTES**.

---

## ⚠️ ARQUITECTURA: DATOS SEPARADOS POR SERVICIO

```
┌─────────────────────────────────────────────────────────────────┐
│         TWO POSTGRES INSTANCES - ZERO DATA SHARING              │
│         (Database-per-Service Pattern)                           │
└─────────────────────────────────────────────────────────────────┘

CARRERAS SERVICE (8001)
└─► carreras_db (PostgreSQL 15)
    │ Puerto: 5432
    │ Host: carreras-db
    │ Usuario: usuario
    │ Password: password
    └─ Volumen: carreras-db-data
       ├── Tabla: carreras (gestión de carreras)
       └── Tabla: materias (materias del servicio carreras)

─────────────────────────────────────────────────────────────────

MATERIAS SERVICE (8002)
└─► materias_db (PostgreSQL 15)
    │ Puerto: 5433
    │ Host: materias-db
    │ Usuario: usuario
    │ Password: password
    └─ Volumen: materias-db-data
       ├── Tabla: materias (materias del servicio materias)
       └── Tabla: temas (temas de materias)

─────────────────────────────────────────────────────────────────

✅ RESULTADO:
   • DOS espacios de almacenamiento COMPLETAMENTE SEPARADOS
   • CERO compartición de datos a nivel de base de datos
   • Servicios comunican SOLO por HTTP/REST API
   • Cada servicio es autónomo e independiente
```

---

## Estructura del Repositorio

```text
El-Muro-Microservicio/
├── infrastructure/
│   └── docker-compose.yml              ✅ Orquestación completa (BD + servicios)
├── services/
│   ├── auth-service/                   📝 TS + MongoDB (Puerto 3000)
│   ├── carreras-service/               ✅ Python FastAPI + PostgreSQL (Puerto 8001)
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   ├── services/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── core/
│   │   ├── scripts/seed.py
│   │   └── Dockerfile
│   ├── materias-service/               ✅ Python FastAPI + PostgreSQL (Puerto 8002)
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   ├── services/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── core/
│   │   ├── scripts/seed.py
│   │   └── Dockerfile
│   ├── posts-service/                  📝 Java + MongoDB (Puerto 8002)
│   ├── temas-service/                  📝 Python + MongoDB (Puerto 8003)
│   └── eureka-server/                  📝 Registro y Descubrimiento
├── frontend/                           📝 React
├── GUIA_RAPIDA.md                      ⚡ Inicio rápido (5 min)
├── MICROSERVICIOS_DOCUMENTACION.md     📚 Documentación completa
├── INTEGRACION_MICROSERVICIOS.md       🔗 Guía de integración
├── El-Muro-Microservicios.postman_collection.json  📤 Colección Postman
└── README.md
```
**Leyenda**: ✅ Completado | 📝 Próximo | ⚡ Utilidad

## 🚀 Inicio Rápido

### 1️⃣ Con Docker Compose (RECOMENDADO)

```bash
cd infrastructure
docker-compose up -d --build

# Esperar 1-2 minutos...
# ✅ Servicios listos en:
# - Carreras: http://localhost:8001
# - Materias: http://localhost:8002
```

### 2️⃣ Verificar Funcionamiento

```bash
curl -H "x-role: ADMIN" http://localhost:8001/health
curl -H "x-role: ADMIN" http://localhost:8002/health
```

### 2b️⃣ VALIDAR QUE ESTÁN SEPARADAS LAS DOS BASES DE DATOS

```bash
# ===== CARRERAS_DB (PUERTO 5432) =====
docker exec carreras-db psql -U usuario -d carreras_db -c "SELECT datname FROM pg_database WHERE datname='carreras_db';"
docker exec carreras-db psql -U usuario -d carreras_db -c "\dt"

# ===== MATERIAS_DB (PUERTO 5433) =====
docker exec materias-db psql -U usuario -d materias_db -c "SELECT datname FROM pg_database WHERE datname='materias_db';"
docker exec materias-db psql -U usuario -d materias_db -c "\dt"

# ✅ RESULTADO ESPERADO:
#    - Dos instancias de PostgreSQL en diferentes puertos (5432 y 5433)
#    - Dos bases de datos con nombres diferentes (carreras_db vs materias_db)
#    - Cada una con sus propias tablas
#    - CERO compartición de datos
```

### 3️⃣ Importar Colección en Postman

1. Descargar: `El-Muro-Microservicios.postman_collection.json`
2. Importar en Postman (Ctrl+O)
3. Ejecutar requests de ejemplo

**→ Ver [GUIA_RAPIDA.md](GUIA_RAPIDA.md) para detalles**

## 📚 Microservicios Implementados

### ✅ Carreras Service (Puerto 8001)

**Tecnología**: Python 3.11 + FastAPI + PostgreSQL

**Funcionalidades**:
- ✅ CRUD de Carreras
- ✅ Relación con Materias
- ✅ Control de acceso por Roles (ADMIN/ESTUDIANTE)
- ✅ Validaciones con Pydantic
- ✅ Migraciones con Alembic
- ✅ Health checks
- ✅ Swagger integrado

**Endpoints**:
```
GET    /api/carreras                # Listar carreras
POST   /api/carreras/crear          # Crear carrera (ADMIN)
GET    /api/carreras/{id}           # Obtener carrera
PUT    /api/carreras/{id}           # Actualizar (ADMIN)
DELETE /api/carreras/{id}           # Eliminar (ADMIN)
POST   /api/carreras/{id}/materias  # Crear materia en carrera (ADMIN)
GET    /api/carreras/{id}/materias  # Listar materias de carrera
```

### ✅ Materias Service (Puerto 8002)

**Tecnología**: Python 3.11 + FastAPI + PostgreSQL

**Funcionalidades**:
- ✅ CRUD de Materias
- ✅ CRUD de Temas
- ✅ Filtrado por Carrera
- ✅ Relaciones anidadas
- ✅ Control de acceso (ADMIN/ESTUDIANTE)
- ✅ Cliente HTTP para validar carreras (preparado)
- ✅ Health checks
- ✅ Swagger integrado

**Endpoints**:
```
GET    /api/materias                # Listar materias (con filtro opcional)
POST   /api/materias/crear          # Crear materia (ADMIN)
GET    /api/materias/{id}           # Obtener materia + temas
PUT    /api/materias/{id}           # Actualizar (ADMIN)
DELETE /api/materias/{id}           # Eliminar (ADMIN)

POST   /api/materias/{id}/temas     # Crear tema (ADMIN)
GET    /api/materias/{id}/temas     # Listar temas
DELETE /api/materias/temas/{id}     # Eliminar tema (ADMIN)
```

---

## 🔐 Autenticación y Autorización

### Sistema Actual (Simulado con Headers)

Valida roles mediante header `x-role`:

```http
x-role: ADMIN          # Acceso total (CRUD)
x-role: ESTUDIANTE     # Solo lectura (GET)
```

**Ejemplo**:
```bash
curl -H "x-role: ADMIN" http://localhost:8001/api/carreras/crear \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Nueva Carrera", "descripcion": "Descripción"}'
  ```

  ### Futura Integración JWT

  Ver → [MICROSERVICIOS_DOCUMENTACION.md#Futura-Integración-JWT](MICROSERVICIOS_DOCUMENTACION.md)

---

## 🐳 Características Docker

**docker-compose.yml incluye**:
- ✅ PostgreSQL 15 para Carreras
- ✅ PostgreSQL 15 para Materias
- ✅ Volúmenes persistentes
- ✅ Health checks automáticos
- ✅ Red interna (`el-muro-network`)
- ✅ Seed automático de datos
- ✅ Hot reload para desarrollo

**Puertos**:
```
8001 → Carreras Service
8002 → Materias Service
5432 → Carreras DB
5433 → Materias DB
```

---

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [GUIA_RAPIDA.md](GUIA_RAPIDA.md) | ⚡ Inicio en 5 minutos |
| [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md) | 📚 Documentación completa (60+ páginas) |
| [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md) | 🔗 Integración entre servicios |
| [El-Muro-Microservicios.postman_collection.json](El-Muro-Microservicios.postman_collection.json) | 📤 Colección Postman |

---

## 📋 Stack Tecnológico

### Backend
- **Python 3.11**: Lenguaje
- **FastAPI**: Framework web asincrónico
- **SQLAlchemy**: ORM
- **Pydantic**: Validaciones
- **Alembic**: Migraciones de BD

### Base de Datos
- **PostgreSQL 15**: BD relacional
- Índices optimizados
- Relaciones referenciadas

### DevOps
- **Docker**: Contenedorización
- **Docker Compose**: Orquestación
- **Scripts de Seed**: Población automática

### Testing & QA
- **pytest**: Tests unitarios
- **Postman**: Tests manuales
- **SQLite**: BD de prueba

---

## 🔀 Integración entre Microservicios

### Opción 1: Foreign Key (Actual) ⭐

```
carreras_db.carrera (id) ← materias_db.materia (carrera_id)
```

**Ventajas**: Simple, rápida, sin latencia
**Uso**: Datos críticos, integridad referencial

### Opción 2: API REST (Preparada)

```
materias-service → GET /api/carreras/{id} → carreras-service
```

**Ventajas**: Desacoplamiento total
**Uso**: Consultas, validaciones opcionales

**Ver** → [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)

---

## 📊 Datos Iniciales (Seed)

Se cargan automáticamente:

**Carreras**:
- Ingeniería de Sistemas
- Ingeniería Electrónica
- Ingeniería Industrial

**Materias**: 8 materias distribuidas en diferentes semestres

**Temas**: 5 temas preparados como ejemplo

*Editar: `services/*/scripts/seed.py`*

---

## ✅ Requisitos

- Docker Desktop 20.10+
- Docker Compose 1.29+
- Postman (opcional, para pruebas)
- Git

---

## 🚨 Troubleshooting

### Error: "Connection refused"
```bash
docker ps  # Verificar que los contenedores están corriendo
docker logs carreras-service  # Ver logs
```

### Error: "Database does not exist"
```bash
docker-compose down
docker volume prune
docker-compose up -d --build
```

### Error: "ModuleNotFoundError"
```bash
docker-compose exec carreras-service pip install -r requirements.txt
```

**Ver más** → [MICROSERVICIOS_DOCUMENTACION.md#Troubleshooting](MICROSERVICIOS_DOCUMENTACION.md)

---

## 🔮 Próximos Pasos

1. **Usuarios Service** (JWT real, roles, autenticación)
2. **Posts Service** (preguntas y respuestas)
3. **API Gateway** (enrutamiento centralizado)
4. **Message Broker** (eventos entre servicios)
5. **Observabilidad** (Prometheus, Grafana, Jaeger)

---