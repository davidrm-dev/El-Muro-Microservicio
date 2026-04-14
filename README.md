# El Muro - Arquitectura de Microservicios

Arquitectura distribuida poliglota para gestion academica y social.

- Infraestructura en contenedores: Eureka + PostgreSQL + MongoDB + Redis.
- Microservicios de negocio en local (sin contenedores).
- Comunicacion entre microservicios por descubrimiento en Eureka (service names), no por `localhost` hardcodeado.

## Estructura

```text
/el-muro
├── /infrastructure
│   ├── docker-compose.yml         # Eureka + bases de datos + redis
│   └── /eureka-server             # Registro y descubrimiento (8761)
├── /services
│   ├── /auth-service              # Node.js + MongoDB (3000)
│   ├── /carreras-service          # FastAPI + PostgreSQL (8001)
│   ├── /materias-service          # FastAPI + PostgreSQL (8004)
│   ├── /posts-service             # Spring Boot + MongoDB + Redis (8002)
│   └── /temas-service             # FastAPI + MongoDB (8003)
├── start-local.sh                 # Arranque unificado Linux/macOS
├── start-local.ps1                # Arranque unificado Windows
└── README.md
```

## Puertos

- Eureka: `8761`
- Auth: `3000`
- Carreras: `8001`
- Materias: `8004`
- Temas: `8003`
- Posts: `8002`
- PostgreSQL carreras: `5434`
- PostgreSQL materias: `5433`
- MongoDB: `27017`
- Redis: `6379`

## Ejecucion rapida

### Linux/macOS

```bash
./start-local.sh
```

### Windows (PowerShell)

```powershell
.\start-local.ps1
```

Los scripts hacen lo siguiente:

1. Levantan infraestructura en `infrastructure/docker-compose.yml`.
2. Esperan disponibilidad de Eureka.
3. Ejecutan `auth-service`, `carreras-service`, `materias-service`, `temas-service` y `posts-service` en local.
4. Corren seeds:
   - `auth-service`: usuarios base.
   - `carreras-service`: seed idempotente.
   - `materias-service`: seed idempotente.
   - `posts-service`: seed automatico al iniciar si no hay posts.
5. Verifican health endpoints y registro en Eureka.

## Ejecucion manual (alternativa)

1) Infraestructura:

```bash
cd infrastructure
docker-compose up -d --remove-orphans
```

2) Microservicios locales (en terminales separadas):

```bash
# auth
cd services/auth-service
npm run dev

# carreras
cd services/carreras-service
./.venv_local/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# materias
cd services/materias-service
./.venv_local/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8004

# temas
cd services/temas-service
./.venv_local/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8003

# posts
cd services/posts-service
mvn -DskipTests package
INTERNAL_SERVICE_SECRET=internal-secret-uptc-2026 \
INTERNAL_SERVICE_ID=posts-service \
JWT_SECRET=tu-secret-key-super-segura-para-desarrollo-12345 \
MONGO_URI="mongodb://admin:password@localhost:27017/posts_service?authSource=admin" \
REDIS_HOST=localhost REDIS_PORT=6379 \
EUREKA_DEFAULT_ZONE="http://localhost:8761/eureka/" \
AUTH_SERVICE_NAME=auth-service TOPIC_SERVICE_NAME=temas-service \
java -jar target/posts-service-0.0.1-SNAPSHOT.jar
```

## Seeders

- Auth users: `services/auth-service/src/database/seeds/seed-users.ts`
  - Ejecutar: `npm run seed:users`
- Carreras: `services/carreras-service/scripts/seed.py`
  - Ejecutar: `PYTHONPATH=. ./.venv_local/Scripts/python.exe scripts/seed.py`
- Materias: `services/materias-service/scripts/seed.py`
  - Ejecutar: `PYTHONPATH=. ./.venv_local/Scripts/python.exe scripts/seed.py`
- Posts: automatico al iniciar (`SeedPostsConfig`) si la coleccion esta vacia.

## Verificacion rapida

```bash
curl -s http://localhost:3000/health
curl -s http://localhost:8001/health
curl -s http://localhost:8004/health
curl -s http://localhost:8003/health
curl -s http://localhost:8002/health
curl -s http://localhost:8761/eureka/apps
```

## Nota de comunicacion entre servicios

- Los servicios se registran en Eureka con `service_name`.
- Las llamadas internas resuelven destino via Eureka por nombre (`AUTH-SERVICE`, `POSTS-SERVICE`, etc.).
- No se usa `localhost` para la comunicacion logica entre microservicios.
