# ⚡ Guía Rápida de Inicio - Microservicios El Muro

## ⚠️ ARQUITECTURA: DOS BASES DE DATOS COMPLETAMENTE SEPARADAS

```
CARRERAS SERVICE (8001) ──────> carreras_db (PostgreSQL 5432)
                                [Base Independiente]

MATERIAS SERVICE (8002) ──────> materias_db (PostgreSQL 5433)
                                [Base Independiente]

✅ CERO compartición de datos entre servicios
✅ Cada servicio es completamente autónomo
✅ Comunicación SOLO por HTTP/REST API
```

---

## 🚀 Inicio en 5 Minutos

### 1. Levantar los Servicios

```bash
cd c:\UNIVERSIDAD\INGENIERIA\ SOFTWARE\ II\El-Muro-Microservicio\infrastructure

docker-compose up -d --build
```

**Esperar 1-2 minutos** (las BD se están inicializando)

### 2. Verificar que Todo Funciona

```bash
# Ver estado de los contenedores
docker ps

# Deberías ver:
# - carreras-db   (PostgreSQL, puerto 5432)
# - carreras-service (puerto 8001)
# - materias-db   (PostgreSQL, puerto 5433)
# - materias-service (puerto 8002)

# Health Check Carreras
curl -H "x-role: ADMIN" http://localhost:8001/health

# Health Check Materias
curl -H "x-role: ADMIN" http://localhost:8002/health
```

Respuesta esperada:
```json
{"service": "carreras-service", "status": "healthy"}
{"service": "materias-service", "status": "healthy"}
```

### 2b. VALIDAR QUE LAS DOS BDs ESTÁN SEPARADAS

```bash
# ===== CARRERAS_DB (PUERTO 5432) =====
# Ver tablas + datos de carreras_db
docker exec carreras-db psql -U usuario -d carreras_db -c "\dt"
docker exec carreras-db psql -U usuario -d carreras_db -c "SELECT * FROM carreras;"
docker exec carreras-db psql -U usuario -d carreras_db -c "SELECT * FROM materias;"

# ===== MATERIAS_DB (PUERTO 5433) =====
# Ver tablas + datos de materias_db  
docker exec materias-db psql -U usuario -d materias_db -c "\dt"
docker exec materias-db psql -U usuario -d materias_db -c "SELECT * FROM materias;"
docker exec materias-db psql -U usuario -d materias_db -c "SELECT * FROM temas;"

# RESULTADO ESPERADO:
# Carreras_db tiene:
#   - Tabla: carreras (creada con datos de seed)
#   - Tabla: materias (materias locales de este servicio)
#
# Materias_db tiene:
#   - Tabla: materias (completamente independiente)
#   - Tabla: temas (solo en este servicio)
#
# ✅ SI VES DATOS EN AMBAS = PERFECTO, ESTÁN SEPARADAS
```

### 3. Ir a Postman

1. Importar colección: `El-Muro-Microservicios.postman_collection.json`
2. Ejecutar requests de ejemplo

---

## 📝 Requests Básicos

### Crear Carrera (ADMIN)

```
POST http://localhost:8001/api/carreras/crear
Header: x-role: ADMIN

{
  "nombre": "Ingeniería de Sistemas",
  "descripcion": "Carrera de sistemas"
}
```

### Listar Carreras (CUALQUIERA)

```
GET http://localhost:8001/api/carreras
Header: x-role: ESTUDIANTE
```

### Crear Materia (ADMIN)

```
POST http://localhost:8002/api/materias/crear
Header: x-role: ADMIN

{
  "nombre": "Programación I",
  "semestre": 1,
  "carrera_id": 1,
  "descripcion": "Intro a programación"
}
```

### Crear Tema (ADMIN)

```
POST http://localhost:8002/api/materias/1/temas
Header: x-role: ADMIN

{
  "nombre": "Variables y Tipos",
  "descripcion": "Conceptos básicos"
}
```

---

## 🐳 Comandos Docker Útiles

```bash
# Ver logs (Comando útil para debug)
docker logs carreras-service
docker logs materias-service

# Ver estado de servicios
docker ps

# Detener todo
docker-compose down

# Reiniciar un servicio
docker-compose restart carreras-service

# Entrar a la BD directo
docker exec -it carreras-db psql -U usuario -d carreras_db
```

---

## 🗄️ Base de Datos - Queries Útiles

```sql
-- Conectar a la BD de carreras
docker exec -it carreras-db psql -U usuario -d carreras_db

-- Ver todas las carreras
SELECT * FROM carreras;

-- Ver todas las materias
SELECT * FROM materias;

-- Ver materias de carrera específica
SELECT * FROM materias WHERE carrera_id = 1;
```

---

## 📊 Datos Iniciales (Seed)

Se ejecutan **automáticamente** al iniciar:

### Carreras Precargadas:
1. Ingeniería de Sistemas
2. Ingeniería Electrónica
3. Ingeniería Industrial

### Materias Precargadas (8):
- Programación I (Semestre 1)
- Matemáticas Discretas (Semestre 1)
- Estructuras de Datos (Semestre 2)
- Base de Datos (Semestre 3)
- Y más...

### Temas Precargados (5):
- Variables y Tipos de Datos
- Funciones
- Lógica Proposicional
- Árboles
- Grafos

*Para agregar más datos, editar: `services/carreras-service/scripts/seed.py` y `services/materias-service/scripts/seed.py`*

---

## 🔐 Control de Acceso

### Roles Disponibles:

```
x-role: ADMIN
  ✅ Crear carreras
  ✅ Actualizar carreras
  ✅ Eliminar carreras
  ✅ Crear materias
  ✅ Crear temas
  ✅ Listar (lectura)

x-role: ESTUDIANTE
  ❌ No puede crear/editar/eliminar
  ✅ Solo puede LEER
```

### Ejemplo - Error sin Rol:

```
GET http://localhost:8001/api/carreras
(sin header x-role)

❌ Respuesta:
{"detail": "No role provided..."}
```

---

## 🔗 Puertos y URLs

| Servicio | Puerto | URL | Health |
|----------|--------|-----|--------|
| Carreras Service | 8001 | http://localhost:8001 | http://localhost:8001/health |
| Materias Service | 8002 | http://localhost:8002 | http://localhost:8002/health |
| Carreras DB | 5432 | localhost | - |
| Materias DB | 5433 | localhost | - |

---

## 📚 API Documentation Automática

Ambos servicios tienen Swagger integrado:

- Carreras: http://localhost:8001/docs
- Materias: http://localhost:8002/docs

*Abre en el navegador y prueba directamente desde ahí*

---

## 🛠️ Para Desarrollo (Sin Docker)

### Carreras Service

```bash
cd services/carreras-service

# Setup
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python scripts/seed.py

# Iniciar
uvicorn app.main:app --port 8001 --reload
```

### Materias Service

```bash
cd services/materias-service

# Setup (igual al anterior)
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python scripts/seed.py

# Iniciar
uvicorn app.main:app --port 8002 --reload
```

---

## ❌ Problemas Comunes

### "Connection refused en puerto 8001"

```bash
# Verificar si el contenedor está corriendo
docker ps

# Si no está, iniciar de nuevo
docker-compose up -d --build
```

### "Database connection error"

```bash
# Esperar a que PostgreSQL esté listo (hasta 30s)
# O ver logs:
docker logs carreras-db

# Reiniciar las BDs:
docker-compose restart carreras-db materias-db
```

### "ImportError: No module named 'app'"

```bash
# Dentro del contenedor, instalar dependencias:
docker-compose exec carreras-service pip install -r requirements.txt
```

---

## ✅ Checklist de Verificación

- [ ] Docker Compose corriendo: `docker ps`
- [ ] Carrera Health OK: http://localhost:8001/health (con header x-role)
- [ ] Materias Health OK: http://localhost:8002/health (con header x-role)
- [ ] Colección de Postman importada
- [ ] Crear carrera de prueba
- [ ] Crear materia de prueba
- [ ] Crear tema de prueba
- [ ] Verificar en BD: `SELECT * FROM carreras;`

---

## 📖 Documentación Completa

Ver: `MICROSERVICIOS_DOCUMENTACION.md`

---

**Última actualización**: Enero 2024
**Status**: ✅ Listo para usar
