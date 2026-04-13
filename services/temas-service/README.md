# Temas Service

Microservicio encargado de la gestion de temas dentro de El Muro.

## Responsabilidades

- Crear, editar, consultar y deshabilitar temas.
- Organizar los temas por `materia_id`.
- Exponer un punto de consulta para obtener los posts asociados a un tema.

## Estado actual

Este servicio se implementa en `FastAPI` con persistencia en `MongoDB`.
La integracion con `materias-service` y `posts-service` se hace mediante HTTP.

## Casos de uso cubiertos

- `Crear tema`: solo `admin`.
- `Editar tema`: solo `admin`.
- `Deshabilitar tema`: solo `admin`.
- `Ver tema`: `admin` y `estudiante`.
- `Ver posts del tema`: `admin` y `estudiante`.

## Endpoints

- `POST /api/temas`
- `GET /api/temas`
- `GET /api/temas/{tema_id}`
- `PUT /api/temas/{tema_id}`
- `PATCH /api/temas/{tema_id}/disable`
- `GET /api/temas/{tema_id}/posts`
- `GET /health`

## Como funciona

1. El `admin` crea o actualiza temas enviando `nombre`, `descripcion` y `materia_id`.
2. Antes de guardar, `temas-service` consulta `materias-service` para validar que la materia exista.
3. Los temas se almacenan en MongoDB con el estado `esta_activo`.
4. Cuando un usuario consulta `/api/temas/{tema_id}/posts`, el servicio busca el tema localmente y luego consulta `posts-service` usando `temaId`.

## Como se comunica con el proyecto

- `auth-service`: no se consulta por HTTP en esta version, pero comparte el contrato del JWT (`userId`, `rol`) para autorizar acceso.
- `materias-service`: se consulta `GET /api/materias/{materia_id}` para validar la materia asociada.
- `posts-service`: se intenta consultar `GET /api/posts?temaId={tema_id}` o `GET /posts?temaId={tema_id}`.
- `eureka-server`: el servicio puede registrarse automaticamente cuando `EUREKA_ENABLED=true`.

## Ejecucion local

```bash
cd services/temas-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

## Variables de entorno

Toma como base el archivo `.env.example`.

Variables clave:

- `MONGO_URI`
- `MONGO_DATABASE`
- `SECRET_KEY`
- `MATERIAS_SERVICE_URL`
- `POSTS_SERVICE_URL`
- `EUREKA_ENABLED`
- `EUREKA_SERVER_URL`

## Notas de integracion

- La integracion de descubrimiento queda centrada en `eureka-server`; no se deja configuracion de gateway en esta rama.
- Si `posts-service` todavia no implementa filtro por `temaId`, el endpoint de posts del tema respondera con error `503` indicando que ese contrato aun no existe.
