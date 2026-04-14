# El Muro - Endpoints principales

Este documento resume endpoints clave para smoke tests del sistema corriendo con:

- Infraestructura en Docker
- Microservicios en local
- Discovery por Eureka

## Health checks

- `GET http://localhost:3000/health` (auth)
- `GET http://localhost:8001/health` (carreras)
- `GET http://localhost:8004/health` (materias)
- `GET http://localhost:8003/health` (temas)
- `GET http://localhost:8002/health` (posts)

## Eureka

- `GET http://localhost:8761/eureka/apps`
- `GET http://localhost:8761/eureka/apps/AUTH-SERVICE`
- `GET http://localhost:8761/eureka/apps/POSTS-SERVICE`
- `GET http://localhost:8761/eureka/apps/CARRERAS-SERVICE`
- `GET http://localhost:8761/eureka/apps/MATERIAS-SERVICE`
- `GET http://localhost:8761/eureka/apps/TEMAS-SERVICE`

## Auth Service (`http://localhost:3000`)

- `POST /api/auth/login`
- `GET /api/auth/me/puntos`
- `PATCH /api/auth/internal/users/{userId}/deduct-points` (interno)
- `PATCH /api/auth/internal/users/{userId}/add-points` (interno)
- `GET /api/auth/internal/users/{userId}/points` (interno)

## Carreras Service (`http://localhost:8001`)

- `GET /api/carreras/`
- `GET /api/carreras/{carreraId}`
- `GET /api/carreras/_exists/{carreraId}` (publico interno)

## Materias Service (`http://localhost:8004`)

- `GET /api/materias/`
- `GET /api/materias/{materiaId}`
- `GET /api/materias/carrera/{carreraId}`
- `POST /api/materias/crear`
- `DELETE /api/materias/carrera/{carreraId}/all` (interno)

## Temas Service (`http://localhost:8003`)

- `GET /api/temas`
- `POST /api/temas`
- `GET /api/temas/{temaId}`
- `GET /api/temas/{temaId}/posts`
- `GET /api/temas/internal/{temaId}/exists` (interno para posts)

## Posts Service (`http://localhost:8002`)

- `GET /api/posts?temaId={temaId}`
- `POST /api/posts`
- `GET /api/posts/{postId}`
- `POST /api/posts/{postId}/view`
- `POST /api/posts/{postId}/vote`
- `GET /api/posts/feed/latest?limit=20`

## Smoke flow sugerido

1. Login admin y estudiante en auth.
2. Consultar carreras y materias.
3. Crear tema (admin).
4. Crear post (estudiante) con `topicId` del tema creado.
5. Consultar `GET /api/posts?temaId=...`.
6. Consultar `GET /api/temas/{temaId}/posts` para validar integracion temas -> posts.
