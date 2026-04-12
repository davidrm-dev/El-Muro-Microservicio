# 🗄️ ARQUITECTURA: DOS BASES DE DATOS COMPLETAMENTE INDEPENDIENTES

## ⚠️ PUNTO CRÍTICO

**Este proyecto implementa DOS instancias de PostgreSQL completamente separadas e independientes.**

**NO es una sola base de datos compartida.**

---

## 1️⃣ SEPARACIÓN FÍSICA

### carreras-db (Instancia 1)
```yaml
Tipo:      PostgreSQL 15
Puerto:    5432
Host:      carreras-db
Usuario:   usuario
Contraseña: password
Base:      carreras_db
Volumen:   carreras-db-data
```

**Tablas:**
- `carreras` - Información de carreras académicas
- `materias` - Materias asociadas a carreras (FK → carreras.id)

---

### materias-db (Instancia 2)
```yaml
Tipo:      PostgreSQL 15
Puerto:    5433
Host:      materias-db
Usuario:   usuario
Contraseña: password
Base:      materias_db
Volumen:   materias-db-data
```

**Tablas:**
- `materias` - Materias del servicio (independiente de carreras_db.materias)
- `temas` - Temas de materias

---

## 2️⃣ ARCHIVOS QUE PRUEBAN LA SEPARACIÓN

### docker-compose.yml (Líneas relevantes)

```yaml
services:
  # ===== BD 1 =====
  carreras-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: carreras_db  # ← Base de datos 1
    ports:
      - "5432:5432"             # ← Puerto 1
    volumes:
      - carreras-db-data:/var/lib/postgresql/data

  # ===== BD 2 =====
  materias-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: materias_db  # ← Base de datos 2
    ports:
      - "5433:5432"             # ← Puerto 2 (diferente)
    volumes:
      - materias-db-data:/var/lib/postgresql/data  # ← Volumen diferente

volumes:
  carreras-db-data:     # ← Volumen 1
  materias-db-data:     # ← Volumen 2
```

### Configuración de cada Servicio

**Carreras Service:**
```env
DATABASE_URL=postgresql://usuario:password@carreras-db:5432/carreras_db
POSTGRES_HOST=carreras-db
POSTGRES_PORT=5432
POSTGRES_DB=carreras_db
```

**Materias Service:**
```env
DATABASE_URL=postgresql://usuario:password@materias-db:5432/materias_db
POSTGRES_HOST=materias-db
POSTGRES_PORT=5432
POSTGRES_DB=materias_db
```

---

## 3️⃣ CÓMO VERIFICAR LA SEPARACIÓN

### Opción A: Ver Contenedores Activos

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
```

**Deberías ver:**
```
carreras-db    0.0.0.0:5432->5432/tcp    Up
materias-db    0.0.0.0:5433->5432/tcp    Up
```

Note: **Puerto 5432 vs 5433** ← Diferentes

---

### Opción B: Acceder a Cada BD Directamente

```bash
# ===== Conectar a carreras_db (Puerto 5432) =====
psql -h localhost -p 5432 -U usuario -d carreras_db

# Dentro de psql:
\l               # Listar bases de datos
\dt              # Listar tablas
SELECT * FROM carreras;
SELECT * FROM materias;
\q               # Salir
```

```bash
# ===== Conectar a materias_db (Puerto 5433) =====
psql -h localhost -p 5433 -U usuario -d materias_db

# Dentro de psql:
\l               # Listar bases de datos
\dt              # Listar tablas
SELECT * FROM materias;
SELECT * FROM temas;
\q               # Salir
```

---

### Opción C: Usando Docker Exec

```bash
# ===== VER BASES EN CARRERAS =====
docker exec carreras-db psql -U usuario -d carreras_db -c "\l"
docker exec carreras-db psql -U usuario -d carreras_db -c "\dt"
docker exec carreras-db psql -U usuario -d carreras_db -c "SELECT COUNT(*) FROM carreras;"
docker exec carreras-db psql -U usuario -d carreras_db -c "SELECT COUNT(*) FROM materias;"

# ===== VER BASES EN MATERIAS =====
docker exec materias-db psql -U usuario -d materias_db -c "\l"
docker exec materias-db psql -U usuario -d materias_db -c "\dt"
docker exec materias-db psql -U usuario -d materias_db -c "SELECT COUNT(*) FROM materias;"
docker exec materias-db psql -U usuario -d materias_db -c "SELECT COUNT(*) FROM temas;"
```

---

## 4️⃣ SCHEMA COMPLETO

### carreras_db - Schema

```sql
-- TABLE: carreras
CREATE TABLE carreras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_carrera_nombre ON carreras(nombre);

-- TABLE: materias (en carreras_db)
CREATE TABLE materias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    semestre INTEGER NOT NULL,
    carrera_id INTEGER NOT NULL REFERENCES carreras(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materia_carrera ON materias(carrera_id);
CREATE INDEX idx_materia_semestre ON materias(semestre);
```

---

### materias_db - Schema

```sql
-- TABLE: materias (en materias_db)
CREATE TABLE materias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    semestre INTEGER NOT NULL,
    carrera_id INTEGER NOT NULL,  -- Referencia (NO FK a otra BD)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materia_nombre ON materias(nombre);
CREATE INDEX idx_materia_carrera_id ON materias(carrera_id);
CREATE INDEX idx_materia_semestre ON materias(semestre);

-- TABLE: temas (solo en materias_db)
CREATE TABLE temas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    materia_id INTEGER NOT NULL REFERENCES materias(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tema_nombre ON temas(nombre);
CREATE INDEX idx_tema_materia ON temas(materia_id);
```

---

## 5️⃣ PATRÓN IMPLEMENTADO: Database-per-Service

Este es un patrón de microservicios recomendado:

```
Service 1 ─────► Database 1 (Independent)
Service 2 ─────► Database 2 (Independent)
Service 3 ─────► Database 3 (Independent)
```

**Ventajas:**
- ✅ Escalabilidad independiente
- ✅ Cambios de BD sin afectar otros servicios
- ✅ Fácil de reemplazar BD (ej: cambiar PostgreSQL a MongoDB)
- ✅ Autonomía total del servicio
- ✅ Recuperación independiente ante fallos

**Desventajas Manejadas:**
- ⚠️ Datos duplicados → Aceptable, cada servicio maneja sus datos
- ⚠️ Consistencia eventual → Comunicación HTTP REST
- ⚠️ Transacciones distribuidas → No necesarias (services independientes)

---

## 6️⃣ INTEGRACIÓN ENTRE SERVICIOS

Como cada servicio tiene su BD independiente, la comunicación es:

### carreras-service → materias-service

**Cuando necesita validar una materia:**
1. Recibe una solicitud HTTP (POST, GET, etc.)
2. Valida en su propia BD (`carreras_db`)
3. Si necesita datos del otro servicio, realiza llamada HTTP
4. **NO accede directamente a `materias_db`**

### Ejemplo: Crear una Materia

```
Cliente HTTP
    │
    ├─► carreras-service (8001)
    │   │ Accede a carreras_db (5432)
    │   │
    │   └─► Si necesita validar carrera_id:
    │       └─► Llamada HTTP a materias-service
    │           │
    │           └─► materias-service (8002)
    │               └─ Accede a materias_db (5433)
```

---

## 7️⃣ CONFIRMACIÓN FINAL

✅ **DOS bases de datos separadas implementadas**

- [x] carreras-db en puerto 5432
- [x] materias-db en puerto 5433
- [x] Volúmenes independientes
- [x] Migraciones independientes (Alembic)
- [x] Seeds independientes
- [x] Servicios conectan a su BD correspondiente
- [x] Documentación clara del patrón

---

## 📚 Referencias en Documentación

- **README.md** - Arquitectura visual
- **GUIA_RAPIDA.md** - Comandos para verificar separación
- **MICROSERVICIOS_DOCUMENTACION.md** - Detalles técnicos completos
- **INTEGRACION_MICROSERVICIOS.md** - Cómo comunican servicios sin compartir BD
