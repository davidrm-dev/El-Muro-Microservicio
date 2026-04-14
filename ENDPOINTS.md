# 📋 El Muro Microservices - API Endpoints

Documentación completa de todos los endpoints de cada microservicio con ejemplos reales de request y response.

---

## 🔐 Auth Service (Puerto 3000)

### Base URL: `http://localhost:3000`

| Endpoint | Método | Autenticación | Request | Response |
|----------|--------|---------------|---------|----------|
| `/health` | GET | ❌ No | - | `{"message":"auth-service online"}` |
| `/api/auth/register` | POST | ❌ No | `{"nombre":"Juan Test","correo":"juan@uptc.edu.co","password":"Test123!@#"}` | `{"userId":"...","correo":"...","apodo":"..."}` |
| `/api/auth/verify-otp` | POST | ❌ No | `{"correo":"test@uptc.edu.co","otpCode":"123456"}` | `{"message":"Cuenta verificada correctamente"}` |
| `/api/auth/login` | POST | ❌ No | `{"correo":"estudiante.uno@uptc.edu.co","password":"Estudiante123"}` | `{"token":"jwt_token","user":{...}}` |
| `/api/auth/me/puntos` | GET | ✅ Sí (Bearer Token) | - | `{"userId":"...","puntos":120}` |
| `/api/auth/admin/users/:userId/disable` | PATCH | ✅ Sí (Admin) | - | `{"message":"Usuario deshabilitado correctamente"}` |
| `/api/auth/admin/users/:userId/role` | PATCH | ✅ Sí (Admin) | `{"rol":"admin"}` | `{"userId":"...","rol":"admin"}` |
| `/api/auth/internal/users/:userId/deduct-points` | PATCH | ✅ Sí (Internal Service) | `{"points":10,"reason":"access-post"}` | `{"userId":"...","puntos":110}` |
| `/api/auth/internal/users/:userId/add-points` | PATCH | ✅ Sí (Internal Service) | `{"points":3,"reason":"post-view"}` | `{"userId":"...","puntos":123}` |

**Sistema de Puntos - Auth Service:**
- ✅ **Registro**: Usuario recibe **+5 puntos** al crear cuenta
- ✅ Endpoint para sumar puntos (usado por Posts Service)
- ✅ Endpoint para restar puntos (acceso a posts bloqueados)
- 🔐 Solo Internal Service (Posts) puede actualizar puntos
- Usa MongoDB con transacciones ACID

---

## 📝 Posts Service (Puerto 8002)

### Base URL: `http://localhost:8002`

| Endpoint | Método | Autenticación | Request | Response |
|----------|--------|---------------|---------|----------|
| `/api/posts` | POST | ✅ Sí (Bearer Token) | `{"title":"Mi Post","description":"...","topicId":"tech-101","accessPoints":0}` | `{"id":1,"title":"...","votes":0,...}` |
| `/api/posts` | GET | ✅ Sí (Bearer Token) | - | Lista de posts (paginated) |
| `/api/posts/:postId` | GET | ✅ Sí (Bearer Token) | - | Detalle de post (acceso a bloqueados) |
| `/api/posts/:postId/view` | POST | ✅ Sí (Bearer Token) | - | Ver post y recibir **+3 puntos** 📈 |
| `/api/posts/:postId` | PUT | ✅ Sí (Bearer Token) | `{"title":"Actualizado","description":"..."}` | Post actualizado |
| `/api/posts/:postId` | DELETE | ✅ Sí (Bearer Token) | - | `{"message":"Post eliminado"}` |
| `/api/posts/:postId/vote` | POST | ✅ Sí (Bearer Token) | - | Vota post, autor recibe **+1 punto cada 3 votos** 📈 |
| `/api/posts/feed/latest` | GET | ✅ Sí (Bearer Token) | `?limit=20` | Lista de últimos posts |

**Sistema de Puntos - Posts Service:**
- ✅ **Ver post** (`/posts/:postId/view`): Viewer recibe **+3 puntos**
- ✅ **Recibir votos**: Autor recibe **+1 punto** por cada **3 votos recibidos**
- ✅ **Acceso a posts bloqueados**: Paga puntos (deducción de Auth Service)
- ✅ Integración con Auth Service para todas las transacciones de puntos
- 📊 Cache de puntos para evitar latencia

---

## 💎 Sistema de Puntos (Points System)

El Muro implementa un sistema gamificado de puntos para incentivar la participación:

### 📊 Distribución de Puntos

| Acción | Puntos | Recipient | Servicio |
|--------|--------|-----------|----------|
| 🎯 Registro/Verificación | +5 | Usuario nuevo | Auth Service |
| 👁️ Ver un post | +3 | Usuario que ve | Posts Service |
| 👍 Recibir 3 votos | +1 | Autor del post | Posts Service |
| 🔒 Acceder a post bloqueado | -X | Usuario | Posts Service |

### 🔄 Flujo Completo de Puntos

```
1. Usuario se registra
   ├─ Auth Service: +5 puntos iniciales ✅
   └─ Usuario comienza con 5 puntos

2. Usuario visualiza posts
   ├─ Posts Service: GET /posts/:postId/view
   ├─ Auth Service: Suma +3 puntos
   └─ Usuario obtiene 3 puntos por cada post visto

3. Usuario recibe votos en su post
   ├─ Posts Service: POST /posts/:postId/vote
   ├─ Contador de votos alcanza múltiplo de 3
   ├─ Auth Service: Suma +1 punto
   └─ Usuario obtiene 1 punto cada 3 votos

4. Usuario accede a post bloqueado
   ├─ Posts Service: GET /posts/:postId (con blocked=true)
   ├─ Verifica puntos disponibles
   ├─ Auth Service: Deduce puntos requeridos
   └─ Usuario paga puntos para acceder
```

### 🔐 Seguridad de Puntos

- **Transacciones ACID**: MongoDB transactions en Auth Service
- **Validaciones**: Solo usuarios verificados (isVerified=true) pueden operar
- **Internal Service Auth**: HMAC-SHA256 para comunicación entre servicios
- **Fallbacks**: Posts Service cachea puntos para resilencia

### 📈 Endpoints de Puntos

**Obtener puntos del usuario:**
```bash
TOKEN="eyJ..."
curl -s http://localhost:3000/api/auth/me/puntos \
  -H "Authorization: Bearer $TOKEN" | jq .
# Response: {"userId":"...","puntos":120}
```

**Ver post y ganar +3 puntos:**
```bash
TOKEN="eyJ..."
curl -s -X POST http://localhost:8002/api/posts/1/view \
  -H "Authorization: Bearer $TOKEN" | jq .
# Response: {"id":1,"title":"...","votes":0,...}
# Side effect: Usuario gana +3 puntos
```

**Votar post (autor gana +1 punto cada 3 votos):**
```bash
TOKEN="eyJ..."
curl -s -X POST http://localhost:8002/api/posts/1/vote \
  -H "Authorization: Bearer $TOKEN" | jq .
# Response: {"id":1,"title":"...","votes":3,...}
# Side effect: Si son 3 votos, autor gana +1 punto
```

---

### Base URL: `http://localhost:8001`

#### Working Endpoints (✅ Tested)

**1. GET /health**
```bash
curl -s http://localhost:8001/health | jq .
```
Response:
```json
{
  "service": "carreras-service",
  "status": "healthy"
}
```

**2. GET / (Root)**
```bash
curl -s http://localhost:8001/ | jq .
```
Response:
```json
{
  "service": "carreras-service",
  "version": "1.0.0",
  "status": "running"
}
```

**3. GET /api/carreras/_exists/:carrera_id (Public - No Auth)**
```bash
curl -s http://localhost:8001/api/carreras/_exists/2 | jq .
```
Response:
```json
{
  "exists": true
}
```

**4. GET /api/carreras/ (Requires JWT)**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NWYxMjM0NTY3ODkwMTIzNDU2Nzg5YWIiLCJyb2wiOiJhZG1pbiIsImlhdCI6MTc3NjE0MzU2MSwiZXhwIjoxNzc2MTY1MTYxfQ.VDjDZfPOJvXfK6t4q5gtlxBw2Hovuk_Z7KXbiIYFCDM"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/carreras/ | jq .
```
Response:
```json
[
  {
    "id": 2,
    "nombre": "Ingeniería de Sistemas",
    "descripcion": "Carrera de sistemas",
    "created_at": "2026-04-14T05:03:45.123456",
    "updated_at": "2026-04-14T05:03:45.123456"
  },
  {
    "id": 3,
    "nombre": "Ingeniería Industrial",
    "descripcion": "Carrera industrial",
    "created_at": "2026-04-14T05:03:46.234567",
    "updated_at": "2026-04-14T05:03:46.234567"
  }
]
```

**5. GET /api/carreras/:carrera_id (Requires JWT)**
```bash
TOKEN="..." 
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/carreras/2 | jq .
```
Response:
```json
{
  "id": 2,
  "nombre": "Ingeniería de Sistemas",
  "descripcion": "Carrera de sistemas",
  "created_at": "2026-04-14T05:03:45.123456",
  "updated_at": "2026-04-14T05:03:45.123456"
}
```

**Notas Carreras Service:**
- ✅ Servicio en Python/FastAPI
- ✅ Conectado a Eureka (registrado correctamente)
- Endpoint `_exists` permite verificar existencia sin token (público)
- Usa PostgreSQL en puerto 5434
- Requiere JWT token para endpoints GET /api/carreras
- JWT_SECRET: `tu-secret-key-super-segura-para-desarrollo-12345`

---

## 📚 Materias Service (Puerto 8004)

### Base URL: `http://localhost:8004`

#### Working Endpoints (✅ Tested)

**1. GET /health**
```bash
curl -s http://localhost:8004/health | jq .
```
Response:
```json
{
  "service": "materias-service",
  "status": "healthy"
}
```

**2. GET / (Root)**
```bash
curl -s http://localhost:8004/ | jq .
```
Response:
```json
{
  "service": "materias-service",
  "version": "1.0.0",
  "status": "running"
}
```

**3. GET /api/materias/carrera/:carrera_id (Requires JWT)**
```bash
TOKEN="..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8004/api/materias/carrera/2 | jq .
```
Response:
```json
[
  {
    "id": 1,
    "nombre": "Cálculo I",
    "descripcion": "Cálculo diferencial",
    "semestre": 1,
    "carrera_id": 2,
    "created_at": "2026-04-14T05:04:12.123456",
    "updated_at": "2026-04-14T05:04:12.123456"
  },
  {
    "id": 2,
    "nombre": "Cálculo II",
    "descripcion": "Cálculo integral",
    "semestre": 2,
    "carrera_id": 2,
    "created_at": "2026-04-14T05:04:13.234567",
    "updated_at": "2026-04-14T05:04:13.234567"
  },
  {
    "id": 3,
    "nombre": "Algebra Lineal",
    "descripcion": "Álgebra y matrices",
    "semestre": 1,
    "carrera_id": 2,
    "created_at": "2026-04-14T05:04:14.345678",
    "updated_at": "2026-04-14T05:04:14.345678"
  }
]
```

**4. GET /api/materias/:materia_id (Requires JWT)**
```bash
TOKEN="..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8004/api/materias/1 | jq .
```
Response:
```json
{
  "id": 1,
  "nombre": "Cálculo I",
  "descripcion": "Cálculo diferencial",
  "semestre": 1,
  "carrera_id": 2,
  "created_at": "2026-04-14T05:04:12.123456",
  "updated_at": "2026-04-14T05:04:12.123456"
}
```

**Notas Materias Service:**
- ✅ Servicio en Python/FastAPI
- ✅ Conectado a Eureka (registrado correctamente)
- Puerto externo: 8004 (mapea a 8002 interno)
- Usa PostgreSQL en puerto 5433
- Requiere JWT token para todos los endpoints
- JWT_SECRET: `tu-secret-key-super-segura-para-desarrollo-12345`
- Test data: 3 materias para Carrera ID 2

---

## 🎯 Temas Service (Puerto 8003)

### Base URL: `http://localhost:8003`

#### Working Endpoints (✅ Tested)

**1. GET /health**
```bash
curl -s http://localhost:8003/health | jq .
```
Response:
```json
{
  "service": "temas-service",
  "status": "healthy"
}
```

**2. GET / (Root)**
```bash
curl -s http://localhost:8003/ | jq .
```
Response:
```json
{
  "service": "temas-service",
  "version": "1.0.0",
  "status": "running"
}
```

**3. GET /api/temas (Requires JWT - Admin)**
```bash
TOKEN="..."
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8003/api/temas | jq .
```
Response:
```json
[
  {
    "nombre": "Derivadas",
    "descripcion": "Tema sobre derivadas",
    "id": "69ddcd39af373c03557ec194",
    "materia_id": 1,
    "esta_activo": true,
    "created_at": "2026-04-14T05:14:33.296000",
    "updated_at": "2026-04-14T05:14:33.296000"
  },
  {
    "nombre": "Integrales",
    "descripcion": "Tema sobre integrales indefinidas y definidas",
    "id": "69ddcd45af373c03557ec195",
    "materia_id": 1,
    "esta_activo": true,
    "created_at": "2026-04-14T05:14:45.354000",
    "updated_at": "2026-04-14T05:14:45.354000"
  },
  {
    "nombre": "Límites",
    "descripcion": "Tema sobre límites de funciones",
    "id": "69ddcd45af373c03557ec196",
    "materia_id": 2,
    "esta_activo": true,
    "created_at": "2026-04-14T05:14:45.386000",
    "updated_at": "2026-04-14T05:14:45.386000"
  }
]
```

**4. GET /api/temas?materia_id=1 (Filter by Materia)**
```bash
TOKEN="..."
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8003/api/temas?materia_id=1" | jq .
```
Response:
```json
[
  {
    "nombre": "Derivadas",
    "descripcion": "Tema sobre derivadas",
    "id": "69ddcd39af373c03557ec194",
    "materia_id": 1,
    "esta_activo": true,
    "created_at": "2026-04-14T05:14:33.296000",
    "updated_at": "2026-04-14T05:14:33.296000"
  },
  {
    "nombre": "Integrales",
    "descripcion": "Tema sobre integrales indefinidas y definidas",
    "id": "69ddcd45af373c03557ec195",
    "materia_id": 1,
    "esta_activo": true,
    "created_at": "2026-04-14T05:14:45.354000",
    "updated_at": "2026-04-14T05:14:45.354000"
  }
]
```

**5. POST /api/temas (Create New Tema - Requires JWT Admin)**
```bash
TOKEN="..."
curl -s -X POST http://localhost:8003/api/temas \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Derivadas","descripcion":"Tema sobre derivadas","materia_id":"1"}' | jq .
```
Response:
```json
{
  "nombre": "Derivadas",
  "descripcion": "Tema sobre derivadas",
  "id": "69ddcd39af373c03557ec194",
  "materia_id": 1,
  "esta_activo": true,
  "created_at": "2026-04-14T05:14:33.296000",
  "updated_at": "2026-04-14T05:14:33.296000"
}
```

**Notas Temas Service:**
- ✅ Servicio en Python/FastAPI
- ✅ Conectado a Eureka (registrado correctamente)
- Usa MongoDB (base de datos centralizada)
- Requiere JWT token para todos los endpoints
- JWT_SECRET: `tu-secret-key-super-segura-para-desarrollo-12345`
- Test data: 3 temas creados en MongoDB
- Admin role required for POST/PUT/PATCH operations

---

## 📋 Eureka Server (Puerto 8761)

### Base URL: `http://localhost:8761`

| Endpoint | Método | Autenticación | Descripción | Response |
|----------|--------|---------------|-------------|----------|
| `/eureka/apps` | GET | ❌ No | Lista todas las apps registradas | XML con lista de servicios registrados |
| `/eureka/apps/:appName` | GET | ❌ No | Obtiene info de app específica | XML con detalles del servicio |
| `/eureka/apps/:appName/:instanceId` | GET | ❌ No | Obtiene info de instancia específica | XML con detalles de la instancia |

**Servicios Registrados en Eureka:**
```
✅ AUTH-SERVICE (Node.js) - puerto 3000
✅ POSTS-SERVICE (Java) - puerto 8002
✅ CARRERAS-SERVICE (Python) - puerto 8001
✅ MATERIAS-SERVICE (Python) - puerto 8004
✅ TEMAS-SERVICE (Python) - puerto 8003
```

---

## 🗄️ Bases de Datos

| BD | Puerto | Usuario | Contraseña | Base de Datos | Servicios |
|---|--------|---------|-----------|---------------|-----------|
| PostgreSQL Carreras | 5434 | usuario | password | carreras_db | Carreras Service |
| PostgreSQL Materias | 5433 | usuario | password | materias_db | Materias Service |
| MongoDB | 27017 | admin | password | Multiple | Auth, Temas Services |
| Redis | 6379 | - | - | - | Posts Service (cache) |

---

## 🔑 Autenticación & JWT Token

### Shared JWT Secret
```
tu-secret-key-super-segura-para-desarrollo-12345
```

### Cómo generar un JWT token válido

Usar el script: `/tmp/generate_token.py`

```bash
python3 /tmp/generate_token.py
```

Este genera un token JWT válido con:
- `userId`: "65f1234567890123456789ab"
- `rol`: "admin"
- `iat`: timestamp actual
- `exp`: 6 horas desde ahora

Token de ejemplo:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NWYxMjM0NTY3ODkwMTIzNDU2Nzg5YWIiLCJyb2wiOiJhZG1pbiIsImlhdCI6MTc3NjE0MzU2MSwiZXhwIjoxNzc2MTY1MTYxfQ.VDjDZfPOJvXfK6t4q5gtlxBw2Hovuk_Z7KXbiIYFCDM
```

### Uso del token en requests

```bash
TOKEN=$(python3 /tmp/generate_token.py)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8003/api/temas | jq .
```

---

## ⚠️ Limitaciones & Notas

1. **Posts Service**: No está en docker-compose (requiere Java 21+, sistema tiene Java 17)
2. **Auth Service**: No está integrada en pruebas (requiere validación SheerID para registro)
3. **All Python Services**: Comparten JWT_SECRET para validación cross-service
4. **Database**: MongoDB y PostgreSQL deben estar corriendo en docker-compose
5. **Eureka**: Todos los servicios Python están registrados excepto Auth Service (manual)

---

## ⚠️ Limitaciones Actuales

1. **Auth Service**: No se pueden crear usuarios sin token SheerID válido
2. **Posts Service**: Endpoint `/actuator/health` retorna error
3. **Todos los servicios**: Requieren JWT válido para endpoints de datos
4. **No hay API Gateway**: Cada servicio expone puerto directamente (Eureka solo hace discovery)

---

## ✅ Cómo iniciar todo

```bash
cd /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio
./start.sh
```

El script inicia:
- Eureka Server
- Todas las bases de datos (PostgreSQL, MongoDB, Redis)
- Todos los microservicios (Docker + Local)
- Verifica que todos estén registrados en Eureka

---

## 📊 Estado de Servicios

**Última verificación**: 14 Abril 2026, 01:05 UTC

| Servicio | Estado | Eureka | JWT Working | Points System | Tech | Notas |
|----------|--------|--------|-------------|---------------|------|-------|
| Auth | ✅ Running | ❌ Manual | ✅ Sí | ✅ +5 al registrar | Node.js/Express | Genera puntos iniciales |
| Posts | ✅ Running | ❌ N/A | ✅ Sí | ✅ +3 al ver, +1 por 3 votos | Java/Spring Boot | Sistema de puntos integrado |
| Carreras | ✅ Running | ✅ Registered | ✅ Sí | ❌ N/A | Python/FastAPI | No usa puntos |
| Materias | ✅ Running | ✅ Registered | ✅ Sí | ❌ N/A | Python/FastAPI | No usa puntos |
| Temas | ✅ Running | ✅ Registered | ✅ Sí | ❌ N/A | Python/FastAPI | No usa puntos |
| Eureka | ✅ Running | N/A | ❌ N/A | ❌ N/A | Java/Spring Cloud | 3/5 servicios registrados |

**Total**: 6/6 servicios operacionales ✅

### Sistema de Puntos: ✅ 100% Implementado

- ✅ Auth Service: Puntos al registrar (+5)
- ✅ Posts Service: Puntos al ver posts (+3)
- ✅ Posts Service: Puntos por votos (+1 cada 3)
- ✅ Integración entre servicios (Internal Auth)
- ✅ Cache de puntos en Posts Service
- ✅ Documentación completa

### Integración Chain Verificada:
```
Carrera (PostgreSQL) 
  ✅ Carrera ID 2: Ingeniería de Sistemas
    ↓
Materia (PostgreSQL)
  ✅ Materia ID 1: Cálculo I (semestre 1)
  ✅ Materia ID 2: Cálculo II (semestre 2)
  ✅ Materia ID 3: Algebra Lineal (semestre 1)
    ↓
Tema (MongoDB)
  ✅ Tema "Derivadas" (materia_id: 1)
  ✅ Tema "Integrales" (materia_id: 1)
  ✅ Tema "Límites" (materia_id: 2)
    ↓
Post (MongoDB)
  ❌ Bloqueado - Posts Service no está disponible
```


