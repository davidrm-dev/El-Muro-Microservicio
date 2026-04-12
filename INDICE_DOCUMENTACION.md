# 📚 Índice de Documentación - El Muro Microservicios

## 📍 Comienza Por Aquí

### 🚀 Primera Vez?
1. Leer → [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) (5 min)
2. Leer → [GUIA_RAPIDA.md](GUIA_RAPIDA.md) (5 min)
3. Ejecutar → `docker-compose up -d --build` (2 min)
4. Importar → Postman collection y probar

### 📖 Documentación Completa
- [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md) - 1000+ líneas (TODO)
- [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md) - Integración entre servicios
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios

---

## 🎯 Por Tipo de Tarea

### 🚀 "Quiero empezar rápido"
→ [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
- Levantar servicios en 5 minutos
- Primeros requests
- Troubleshooting básico

### 📚 "Necesito toda la información"
→ [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md)
- Arquitectura detallada
- Todos los endpoints documentados
- Instalación paso-a-paso
- Migraciones de BD
- Autenticación y seguridad
- Buenas prácticas

### 🔗 "¿Cómo se integran los servicios?"
→ [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)
- Relación Carreras ↔ Materias
- Dos opciones de integración
- Service-to-service communication
- Preparación para nuevos servicios

### 📋 "Quiero ver qué se implementó"
→ [CHANGELOG.md](CHANGELOG.md) o [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)

### 🧪 "Quiero probar en Postman"
→ `El-Muro-Microservicios.postman_collection.json`
- Importar en Postman (Ctrl+O)
- 20+ requests listos para probar

---

## 📘 Por Sección

### 🎓 Carreras Service (Puerto 8001)

**Código**: `services/carreras-service/`

**Endpoints**:
```
POST   /api/carreras/crear              # Crear carrera
GET    /api/carreras/                   # Listar carreras
GET    /api/carreras/{id}               # Obtener carrera
PUT    /api/carreras/{id}               # Actualizar
DELETE /api/carreras/{id}               # Eliminar

POST   /api/carreras/{id}/materias      # Crear materia en carrera
GET    /api/carreras/{id}/materias      # Listar materias
```

**Para aprender**:
- [MICROSERVICIOS_DOCUMENTACION.md#Microservicio-de-Carreras](MICROSERVICIOS_DOCUMENTACION.md)
- [MICROSERVICIOS_DOCUMENTACION.md#API-Endpoints](MICROSERVICIOS_DOCUMENTACION.md)

### 📚 Materias Service (Puerto 8002)

**Código**: `services/materias-service/`

**Endpoints**:
```
POST   /api/materias/crear               # Crear materia
GET    /api/materias/                    # Listar materias
GET    /api/materias/{id}                # Obtener materia
PUT    /api/materias/{id}                # Actualizar
DELETE /api/materias/{id}                # Eliminar

POST   /api/materias/{id}/temas          # Crear tema
GET    /api/materias/{id}/temas          # Listar temas
DELETE /api/materias/temas/{id}          # Eliminar tema
```

**Para aprender**:
- [MICROSERVICIOS_DOCUMENTACION.md#Microservicio-de-Materias](MICROSERVICIOS_DOCUMENTACION.md)
- [MICROSERVICIOS_DOCUMENTACION.md#API-Endpoints](MICROSERVICIOS_DOCUMENTACION.md)

### 🐳 Docker & DevOps

**Archivo**: `infrastructure/docker-compose.yml`

**Para aprender**:
- [GUIA_RAPIDA.md#Levantar-los-Servicios](GUIA_RAPIDA.md)
- [MICROSERVICIOS_DOCUMENTACION.md#Docker](MICROSERVICIOS_DOCUMENTACION.md)
- [MICROSERVICIOS_DOCUMENTACION.md#Levantar-los-Servicios](MICROSERVICIOS_DOCUMENTACION.md)

### 🔐 Autenticación & Roles

**Headers**:
```
x-role: ADMIN          # Acceso total
x-role: ESTUDIANTE     # Solo lectura
```

**Para aprender**:
- [MICROSERVICIOS_DOCUMENTACION.md#Autenticación-y-Roles](MICROSERVICIOS_DOCUMENTACION.md)
- [MICROSERVICIOS_DOCUMENTACION.md#Futura-Integración-JWT](MICROSERVICIOS_DOCUMENTACION.md)

### 🔗 Integración entre Servicios

**Para aprender**:
- [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)
- [MICROSERVICIOS_DOCUMENTACION.md#Integración-entre-Microservicios](MICROSERVICIOS_DOCUMENTACION.md)

---

## 🛠️ Por Concepto Técnico

### Base de Datos

**PostgreSQL - Estructura**:
- [MICROSERVICIOS_DOCUMENTACION.md#BASE-DE-DATOS](MICROSERVICIOS_DOCUMENTACION.md)

**Migraciones - Alembic**:
- [MICROSERVICIOS_DOCUMENTACION.md#Migraciones-de-Base-de-Datos](MICROSERVICIOS_DOCUMENTACION.md)

**Data Seeding**:
- `services/carreras-service/scripts/seed.py`
- `services/materias-service/scripts/seed.py`
- [MICROSERVICIOS_DOCUMENTACION.md#Data-Seeding](MICROSERVICIOS_DOCUMENTACION.md)

### Validaciones

**Pydantic Schemas**:
- `services/carreras-service/app/schemas/carrera.py`
- `services/materias-service/app/schemas/materia.py`
- [MICROSERVICIOS_DOCUMENTACION.md#Validación-Robusta](MICROSERVICIOS_DOCUMENTACION.md)

### Testing

**Ejemplos**:
- `services/carreras-service/tests/test_carreras.py`
- `services/materias-service/tests/test_materias.py`

**Cómo ejecutar**:
```bash
docker-compose exec carreras-service pytest tests/
docker-compose exec materias-service pytest tests/
```

---

## 📊 Por Rol

### 👨‍💻 Desarrollador Backend

**Empender por**:
1. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
2. [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md)
3. Revisar código en `services/`

**Documentación técnica**:
- Arquitectura: [MICROSERVICIOS_DOCUMENTACION.md#Arquitectura](MICROSERVICIOS_DOCUMENTACION.md)
- Estructura: [MICROSERVICIOS_DOCUMENTACION.md#Estructura-del-Proyecto](MICROSERVICIOS_DOCUMENTACION.md)
- Integración: [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)

### 🧪 QA / Tester

**Empezar por**:
1. [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
2. [El-Muro-Microservicios.postman_collection.json](El-Muro-Microservicios.postman_collection.json)
3. [MICROSERVICIOS_DOCUMENTACION.md#Pruebas-en-Postman](MICROSERVICIOS_DOCUMENTACION.md)

**Test cases**:
- Crear recursos
- Listar recursos
- Obtener detalle
- Actualizar
- Eliminar
- Control de acceso
- Errores

### 📚 Arquitecto / Lead

**Leer**:
1. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
2. [MICROSERVICIOS_DOCUMENTACION.md#Arquitectura](MICROSERVICIOS_DOCUMENTACION.md)
3. [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)

**Revisar**:
- Estructura de carpetas
- Patrones de código
- Integración entre servicios

### 📋 PM / Product Owner

**Leer**:
1. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) (5 min)
2. [CHANGELOG.md](CHANGELOG.md) (5 min)

**Ver estado**: [MICROSERVICIOS_DOCUMENTACION.md#Tabla-de-Contenidos](MICROSERVICIOS_DOCUMENTACION.md)

---

## 🆘 Troubleshooting

**Error común?** → [MICROSERVICIOS_DOCUMENTACION.md#Troubleshooting](MICROSERVICIOS_DOCUMENTACION.md)

**Comandos útiles?** → [GUIA_RAPIDA.md#Comandos-Docker-Útiles](GUIA_RAPIDA.md)

**Problema de BD?** → [GUIA_RAPIDA.md#Base-de-Datos](GUIA_RAPIDA.md)

---

## 🎓 Por Nivel de Conocimiento

### Principiante

**Secuencia**:
1. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
2. [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
3. Ejecutar `docker-compose up`
4. Usar Postman collection

**Evitar por ahora**: Código interno, migraciones

### Intermedio

**Secuencia**:
1. [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md)
2. Revisar código en `services/`
3. [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)
4. Experimentar con cambios

**Próximo paso**: Modificar servicios, crear tests

### Avanzado

**Secuencia**:
1. Entender arquitectura completa
2. Leer y modificar el código
3. Crear nuevas features
4. Implementar JWT real
5. Escalar a nuevos servicios

**Referencias**: Todas las documentaciones, código Python

---

## 📚 Índice de Documentación Disponible

### Archivos Principales

| Archivo | Líneas | Propósito | Leer En |
|---------|--------|-----------|---------|
| RESUMEN_EJECUTIVO.md | 400 | Overview general | 5 min |
| GUIA_RAPIDA.md | 260 | Inicio rápido | 5 min |
| MICROSERVICIOS_DOCUMENTACION.md | 1000+ | Todo completo | 1 hora |
| INTEGRACION_MICROSERVICIOS.md | 600+ | Integración | 30 min |
| CHANGELOG.md | 400 | Cambios realizados | 10 min |
| README.md | 200+ | Overview proyecto | 10 min |

### Colección Postman

| Archivo | Requests | Propósito |
|---------|----------|-----------|
| El-Muro-Microservicios.postman_collection.json | 20+ | Tests en Postman |

---

## 🔍 Buscar Temas Específicos

### A
- **Alembic** → [MICROSERVICIOS_DOCUMENTACION.md#Migraciones-de-Base-de-Datos](MICROSERVICIOS_DOCUMENTACION.md)
- **API Endpoints** → [MICROSERVICIOS_DOCUMENTACION.md#API-Endpoints](MICROSERVICIOS_DOCUMENTACION.md)
- **Autenticación** → [MICROSERVICIOS_DOCUMENTACION.md#Autenticación-y-Roles](MICROSERVICIOS_DOCUMENTACION.md)
- **Arquitectura** → [MICROSERVICIOS_DOCUMENTACION.md#Arquitectura](MICROSERVICIOS_DOCUMENTACION.md)

### B
- **Base de Datos** → [MICROSERVICIOS_DOCUMENTACION.md#BASE-DE-DATOS](MICROSERVICIOS_DOCUMENTACION.md)
- **Backend Stack** → [MICROSERVICIOS_DOCUMENTACION.md#Stack-Tecnológico](MICROSERVICIOS_DOCUMENTACION.md)
- **Buenas Prácticas** → [MICROSERVICIOS_DOCUMENTACION.md#Buenas-Prácticas-Implementadas](MICROSERVICIOS_DOCUMENTACION.md)

### C
- **Carreras Service** → Ver secciones en [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md)
- **Control de Acceso** → [MICROSERVICIOS_DOCUMENTACION.md#Autenticación-y-Roles](MICROSERVICIOS_DOCUMENTACION.md)
- **CORS** → [MICROSERVICIOS_DOCUMENTACION.md#Características-Docker](MICROSERVICIOS_DOCUMENTACION.md)

### D
- **Docker** → [GUIA_RAPIDA.md#Levantar-los-Servicios](GUIA_RAPIDA.md) o [MICROSERVICIOS_DOCUMENTACION.md#Docker](MICROSERVICIOS_DOCUMENTACION.md)
- **Database Design** → [MICROSERVICIOS_DOCUMENTACION.md#Esquema-de-Base-de-Datos](MICROSERVICIOS_DOCUMENTACION.md)

### E
- **Endpoints** → [MICROSERVICIOS_DOCUMENTACION.md#API-Endpoints](MICROSERVICIOS_DOCUMENTACION.md)
- **Ejemplos de Requests** → [MICROSERVICIOS_DOCUMENTACION.md#Ejemplos-de-Pruebas](MICROSERVICIOS_DOCUMENTACION.md)

### F
- **FastAPI** → [MICROSERVICIOS_DOCUMENTACION.md#Stack-Tecnológico](MICROSERVICIOS_DOCUMENTACION.md)
- **Foreign Key** → [INTEGRACION_MICROSERVICIOS.md#Opción-1-Por-Foreign-Key](INTEGRACION_MICROSERVICIOS.md)

### G
- **Getting Started** → [GUIA_RAPIDA.md](GUIA_RAPIDA.md)

### H
- **Health Checks** → [MICROSERVICIOS_DOCUMENTACION.md#Health-Checks](MICROSERVICIOS_DOCUMENTACION.md)

### I
- **Integración** → [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md) o [MICROSERVICIOS_DOCUMENTACION.md#Integración-entre-Microservicios](MICROSERVICIOS_DOCUMENTACION.md)

### J
- **JWT** → [MICROSERVICIOS_DOCUMENTACION.md#Futura-Integración-JWT](MICROSERVICIOS_DOCUMENTACION.md)

### M
- **Materias Service** → Todas las secciones en [MICROSERVICIOS_DOCUMENTACION.md](MICROSERVICIOS_DOCUMENTACION.md)
- **Migraciones** → [MICROSERVICIOS_DOCUMENTACION.md#Migraciones-de-Base-de-Datos](MICROSERVICIOS_DOCUMENTACION.md)

### P
- **Postman** → [MICROSERVICIOS_DOCUMENTACION.md#Pruebas-en-Postman](MICROSERVICIOS_DOCUMENTACION.md) o [GUIA_RAPIDA.md#Ir-a-Postman](GUIA_RAPIDA.md)
- **PostgreSQL** → [MICROSERVICIOS_DOCUMENTACION.md#BASE-DE-DATOS](MICROSERVICIOS_DOCUMENTACION.md)

### R
- **Roles** → [MICROSERVICIOS_DOCUMENTACION.md#Autenticación-y-Roles](MICROSERVICIOS_DOCUMENTACION.md)
- **REST API** → [MICROSERVICIOS_DOCUMENTACION.md#API-Endpoints](MICROSERVICIOS_DOCUMENTACION.md)

### S
- **SQLAlchemy** → [MICROSERVICIOS_DOCUMENTACION.md#Stack-Tecnológico](MICROSERVICIOS_DOCUMENTACION.md)
- **Security** → [MICROSERVICIOS_DOCUMENTACION.md#Autenticación-y-Roles](MICROSERVICIOS_DOCUMENTACION.md)
- **Seed/Datos Iniciales** → [GUIA_RAPIDA.md#Datos-Iniciales](GUIA_RAPIDA.md) o [MICROSERVICIOS_DOCUMENTACION.md#Data-Seeding](MICROSERVICIOS_DOCUMENTACION.md)

### T
- **Testing** → [MICROSERVICIOS_DOCUMENTACION.md#Testing](MICROSERVICIOS_DOCUMENTACION.md)
- **Troubleshooting** → [MICROSERVICIOS_DOCUMENTACION.md#Troubleshooting](MICROSERVICIOS_DOCUMENTACION.md) o [GUIA_RAPIDA.md#Problemas-Comunes](GUIA_RAPIDA.md)

### V
- **Variables de Entorno** → [MICROSERVICIOS_DOCUMENTACION.md#Variables-de-Entorno](MICROSERVICIOS_DOCUMENTACION.md)

---

## 🎯 Quick Links

- **Levantar Servicios**: [GUIA_RAPIDA.md#Levantar-los-Servicios](GUIA_RAPIDA.md)
- **Hacer Primer Request**: [GUIA_RAPIDA.md#Requests-Básicos](GUIA_RAPIDA.md)
- **Ver Datos en BD**: [GUIA_RAPIDA.md#Base-de-Datos](GUIA_RAPIDA.md)
- **Integración**: [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)
- **JWT**: [MICROSERVICIOS_DOCUMENTACION.md#Futura-Integración-JWT](MICROSERVICIOS_DOCUMENTACION.md)
- **Próximos Pasos**: [MICROSERVICIOS_DOCUMENTACION.md#Próximos-Pasos](MICROSERVICIOS_DOCUMENTACION.md)

---

## 📞 Preguntas Frecuentes

**¿Por dónde empiezo?**
→ [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) (5 min) + [GUIA_RAPIDA.md](GUIA_RAPIDA.md) (5 min)

**¿Cómo hago mi primer request?**
→ [GUIA_RAPIDA.md#Requests-Básicos](GUIA_RAPIDA.md)

**¿Cuál es la estructura del proyecto?**
→ [MICROSERVICIOS_DOCUMENTACION.md#Estructura-del-Proyecto](MICROSERVICIOS_DOCUMENTACION.md)

**¿Los servicios se comunican entre sí?**
→ [INTEGRACION_MICROSERVICIOS.md](INTEGRACION_MICROSERVICIOS.md)

**¿Cómo agrego JWT real?**
→ [MICROSERVICIOS_DOCUMENTACION.md#Futura-Integración-JWT](MICROSERVICIOS_DOCUMENTACION.md)

---

## 📍 Ubicación de Archivos

```
El-Muro-Microservicio/
├── RESUMEN_EJECUTIVO.md                    ← EMPIEZA AQUÍ
├── GUIA_RAPIDA.md                          ← O AQUÍ
├── MICROSERVICIOS_DOCUMENTACION.md         ← Documentación completa
├── INTEGRACION_MICROSERVICIOS.md           ← Integración
├── CHANGELOG.md                            ← Cambios
├── INDICE_DOCUMENTACION.md                 ← ESTE ARCHIVO
├── README.md                               ← Overview proyecto
├── El-Muro-Microservicios.postman_collection.json
└── services/
    ├── carreras-service/
    └── materias-service/
```

---

**Versión**: 1.0.0
**Actualizado**: Enero 2024

¿Necesitas ayuda? Consulta [MICROSERVICIOS_DOCUMENTACION.md#Troubleshooting](MICROSERVICIOS_DOCUMENTACION.md)
