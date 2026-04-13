# El Muro - Arquitectura de Microservicios

Arquitectura distribuida poliglota para la gestion academica y social. Los microservicios se ejecutan de forma nativa y el descubrimiento de servicios se centraliza en Eureka.

## Estructura del Repositorio

```text
/el-muro
|-- /infrastructure
|   |-- docker-compose.yml         # Orquestacion de bases de datos y apoyo local
|   |-- /eureka-server             # Registro y descubrimiento (Spring Cloud) puerto 8761
|-- /services
|   |-- /auth-service              # TS + MongoDB (Puerto 3000)
|   |-- /materias-service          # Python + PostgreSQL
|   |-- /posts-service             # Java + MongoDB (Puerto 8002)
|   `-- /temas-service             # Python + MongoDB (Puerto 8003)
|-- /frontend
`-- README.md
```

## Temas Service

El microservicio `temas-service` vive en `services/temas-service` y cubre los casos de uso del documento para gestion de temas:

- Crear tema
- Editar tema
- Deshabilitar tema
- Ver tema
- Ver posts del tema

Su documentacion detallada esta en `services/temas-service/README.md`.

## Integracion entre servicios

- `auth-service` aporta el JWT con `userId` y `rol`.
- `temas-service` valida `materia_id` contra `materias-service`.
- `temas-service` consulta `posts-service` para listar posts por `temaId`.
- `temas-service` puede registrarse en `eureka-server`.
