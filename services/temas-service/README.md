# Temas Service

Microservicio encargado de la gestion de temas dentro de El Muro.

## Responsabilidades

- Crear, editar, consultar y deshabilitar temas.
- Organizar los temas por `materia_id`.
- Exponer un punto de consulta para obtener los posts asociados a un tema.
- Registrarse en `eureka-server` para descubrimiento de servicios.

## Como funciona

1. El cliente envia un JWT en el header `Authorization`.
2. `temas-service` valida el token y el rol (`admin` o `estudiante`).
3. Para crear o actualizar un tema con `materia_id`, el servicio consulta `materias-service`.
4. Los temas se guardan en MongoDB en la coleccion `temas`.
5. Para consultar los posts de un tema, el servicio busca primero el tema localmente y luego consulta `posts-service`.
6. Si `EUREKA_ENABLED=true`, el servicio se registra automaticamente en `eureka-server`.

## JWT De Prueba

El servicio valida JWT con las variables:

- `SECRET_KEY`
- `ALGORITHM`

En el estado actual del archivo local `services/temas-service/.env`, la clave es:

```env
SECRET_KEY=1234
ALGORITHM=HS256
```

Importante:

- Esta clave de prueba debe sincronizarse con la que use `auth-service`.
- Si `auth-service` firma con otra clave, `temas-service` respondera `401 Invalid token`.

### Generar un token admin de prueba

```powershell
python -c "import jwt; print(jwt.encode({'userId':'admin-1','rol':'admin'}, '1234', algorithm='HS256'))"
```

### Generar un token estudiante de prueba

```powershell
python -c "import jwt; print(jwt.encode({'userId':'est-1','rol':'estudiante'}, '1234', algorithm='HS256'))"
```

## Levantar Solo Este Microservicio Con Su Base De Datos

### 1. Levantar MongoDB

Desde `infrastructure/`:

```powershell
docker compose up -d
```

Eso levanta el servicio `mongo-temas` definido en `infrastructure/docker-compose.yml`.

### 2. Revisar el `.env`

El archivo local ya existe en `services/temas-service/.env`.

Valores relevantes:

```env
SERVICE_PORT=8003
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=temas_db
SECRET_KEY=1234
EUREKA_ENABLED=true
EUREKA_SERVER_URL=http://localhost:8761/eureka/
```

### 3. Levantar Eureka

Desde `infrastructure/eureka-server/`:

```powershell
.\mvnw.cmd spring-boot:run
```

Panel:

- `http://localhost:8761`

### 4. Levantar `temas-service`

Desde `services/temas-service/`:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

### 5. Verificaciones basicas

Health:

```powershell
curl http://localhost:8003/health
```

Root:

```powershell
curl http://localhost:8003/
```

Pruebas unitarias:

```powershell
.\.venv\Scripts\python -m pytest
```

Registro en Eureka:

- Abrir `http://localhost:8761`
- Verificar que aparezca `TEMAS-SERVICE`

## Headers Comunes

### Endpoints publicos

- `GET /`
- `GET /health`

No requieren autenticacion.

### Endpoints protegidos

Requieren:

```http
Authorization: Bearer <jwt>
```

Si el token falta o es invalido, la respuesta es:

```json
{
  "detail": "Authorization header missing"
}
```

o:

```json
{
  "detail": "Invalid token"
}
```

## Endpoints

### `GET /`

Descripcion:

- Endpoint raiz del microservicio.

Headers:

- No requiere.

Body:

- No aplica.

Respuesta `200`:

```json
{
  "service": "temas-service",
  "version": "1.0.0",
  "status": "running"
}
```

### `GET /health`

Descripcion:

- Health check del microservicio.

Headers:

- No requiere.

Body:

- No aplica.

Respuesta `200`:

```json
{
  "service": "temas-service",
  "status": "healthy"
}
```

### `POST /api/temas`

Descripcion:

- Crea un nuevo tema.
- Solo rol `admin`.
- Antes de guardar, valida la existencia de la materia en `materias-service`.

Headers:

```http
Authorization: Bearer <jwt-admin>
Content-Type: application/json
```

Body:

```json
{
  "nombre": "Matrices",
  "descripcion": "Operaciones basicas y determinantes",
  "materia_id": 1
}
```

Respuesta `201`:

```json
{
  "id": "6619ef5b8a2f9d6f6f8e1111",
  "nombre": "Matrices",
  "descripcion": "Operaciones basicas y determinantes",
  "materia_id": 1,
  "esta_activo": true,
  "created_at": "2026-04-13T12:00:00Z",
  "updated_at": "2026-04-13T12:00:00Z"
}
```

Errores frecuentes:

- `401`: token faltante o invalido.
- `403`: el usuario no es `admin`.
- `404`: la materia no existe.
- `422`: body invalido.
- `503`: `materias-service` no esta disponible.

### `GET /api/temas`

Descripcion:

- Lista temas.
- Permite filtrar por `materia_id`.
- Por defecto solo retorna temas activos.

Headers:

```http
Authorization: Bearer <jwt-admin-o-estudiante>
```

Query params:

- `materia_id` opcional
- `include_inactive` opcional, por defecto `false`

Ejemplo:

```http
GET /api/temas?materia_id=1&include_inactive=true
```

Respuesta `200`:

```json
[
  {
    "id": "6619ef5b8a2f9d6f6f8e1111",
    "nombre": "Matrices",
    "descripcion": "Operaciones basicas y determinantes",
    "materia_id": 1,
    "esta_activo": true,
    "created_at": "2026-04-13T12:00:00Z",
    "updated_at": "2026-04-13T12:00:00Z"
  }
]
```

Errores frecuentes:

- `401`: token faltante o invalido.
- `422`: query invalida.

### `GET /api/temas/{tema_id}`

Descripcion:

- Obtiene un tema por id.
- Disponible para `admin` y `estudiante`.

Headers:

```http
Authorization: Bearer <jwt-admin-o-estudiante>
```

Body:

- No aplica.

Respuesta `200`:

```json
{
  "id": "6619ef5b8a2f9d6f6f8e1111",
  "nombre": "Matrices",
  "descripcion": "Operaciones basicas y determinantes",
  "materia_id": 1,
  "esta_activo": true,
  "created_at": "2026-04-13T12:00:00Z",
  "updated_at": "2026-04-13T12:00:00Z"
}
```

Errores frecuentes:

- `401`: token faltante o invalido.
- `404`: tema no encontrado.

### `PUT /api/temas/{tema_id}`

Descripcion:

- Actualiza un tema existente.
- Solo rol `admin`.
- Si envias `materia_id`, vuelve a validar esa materia en `materias-service`.

Headers:

```http
Authorization: Bearer <jwt-admin>
Content-Type: application/json
```

Body:

```json
{
  "nombre": "Matrices avanzadas",
  "descripcion": "Transformaciones lineales",
  "materia_id": 1
}
```

Tambien puedes enviar actualizacion parcial:

```json
{
  "descripcion": "Nuevo alcance del tema"
}
```

Respuesta `200`:

```json
{
  "id": "6619ef5b8a2f9d6f6f8e1111",
  "nombre": "Matrices avanzadas",
  "descripcion": "Transformaciones lineales",
  "materia_id": 1,
  "esta_activo": true,
  "created_at": "2026-04-13T12:00:00Z",
  "updated_at": "2026-04-13T12:10:00Z"
}
```

Errores frecuentes:

- `401`: token faltante o invalido.
- `403`: el usuario no es `admin`.
- `404`: tema o materia no encontrados.
- `422`: body invalido.
- `503`: `materias-service` no esta disponible.

### `PATCH /api/temas/{tema_id}/disable`

Descripcion:

- Deshabilita un tema.
- Solo rol `admin`.
- No elimina el documento; cambia `esta_activo` a `false`.

Headers:

```http
Authorization: Bearer <jwt-admin>
```

Body:

- No aplica.

Respuesta `200`:

```json
{
  "id": "6619ef5b8a2f9d6f6f8e1111",
  "nombre": "Matrices",
  "descripcion": "Operaciones basicas y determinantes",
  "materia_id": 1,
  "esta_activo": false,
  "created_at": "2026-04-13T12:00:00Z",
  "updated_at": "2026-04-13T12:15:00Z"
}
```

Errores frecuentes:

- `401`: token faltante o invalido.
- `403`: el usuario no es `admin`.
- `404`: tema no encontrado.

### `GET /api/temas/{tema_id}/posts`

Descripcion:

- Retorna el tema y los posts asociados.
- Disponible para `admin` y `estudiante`.
- Busca el tema localmente y luego consulta `posts-service` con `temaId`.

Headers:

```http
Authorization: Bearer <jwt-admin-o-estudiante>
```

Body:

- No aplica.

Respuesta `200`:

```json
{
  "tema": {
    "id": "6619ef5b8a2f9d6f6f8e1111",
    "nombre": "Matrices",
    "descripcion": "Operaciones basicas y determinantes",
    "materia_id": 1,
    "esta_activo": true,
    "created_at": "2026-04-13T12:00:00Z",
    "updated_at": "2026-04-13T12:00:00Z"
  },
  "posts": [
    {
      "id": "post-1",
      "titulo": "Apuntes de algebra",
      "temaId": "6619ef5b8a2f9d6f6f8e1111"
    }
  ]
}
```

Errores frecuentes:

- `401`: token faltante o invalido.
- `404`: tema no encontrado.
- `503`: `posts-service` no esta disponible.
- `503`: `posts-service` aun no expone filtro por `temaId`.

## Comunicacion Con Otros Servicios

- `auth-service`: comparte el contrato del JWT. Este servicio espera `userId` y `rol`.
- `materias-service`: se consulta `GET /api/materias/{materia_id}` para validar relaciones antes de crear o actualizar.
- `posts-service`: se consulta `GET /api/posts?temaId={tema_id}` o `GET /posts?temaId={tema_id}`.
- `eureka-server`: recibe el registro del servicio si `EUREKA_ENABLED=true`.

## Variables De Entorno

Archivo base:

- `services/temas-service/.env.example`

Archivo local:

- `services/temas-service/.env`

Variables clave:

- `SERVICE_NAME`
- `SERVICE_PORT`
- `MONGO_URI`
- `MONGO_DATABASE`
- `TEMAS_COLLECTION`
- `SECRET_KEY`
- `ALGORITHM`
- `MATERIAS_SERVICE_URL`
- `POSTS_SERVICE_URL`
- `EUREKA_ENABLED`
- `EUREKA_SERVER_URL`
- `EUREKA_INSTANCE_HOST`
- `EUREKA_INSTANCE_IP`
- `REQUEST_TIMEOUT_SECONDS`
