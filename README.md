# El Muro - Arquitectura de Microservicios

Arquitectura distribuida políglota para la gestión académica y social. Los microservicios se ejecutan de forma nativa (Local), mientras que la persistencia se gestiona mediante contenedores Docker.

## Estructura del Repositorio

```text
/el-muro
├── /infrastructure
│   ├── docker-compose.yml         # Orquestación de MongoDB y PostgreSQL
│   └── /eureka-server             # Registro y Descubrimiento (Spring Cloud) puerto 8761
├── /services
│   ├── /auth-service              # David: TS + MongoDB (Puerto 3000)
│   │   └── /src/database/seeds    # Scripts de población de usuarios/roles
│   ├── /carreras-service          # Karen: Python + PostgreSQL (Puerto 8001)
│   │   └── /scripts               # Seed de carreras
│   ├── /materias-service          # Karen: Python + PostgreSQL (Puerto 8002)
│   │   └── /scripts/seeds         # Scripts SQL/Python para materias
│   ├── /posts-service             # Angela: Java + MongoDB (Puerto 8002)
│   │   └── /src/main/resources    # data.json o scripts de inicialización
│   └── /temas-service             # Anthony: Python + MongoDB (Puerto 8003)
│       └── /seeds                 # Scripts de carga de temas iniciales
├── /frontend                      # Aplicación React
└── README.md
```
## Configuración y Ejecución
1. **Iniciar la Infraestructura**: Navega a la carpeta `infrastructure` y ejecuta:
   ```bash
   docker-compose up -d
   ```
   Esto levantará MongoDB y PostgreSQL en los puertos configurados.
2. **Ejecutar los Microservicios**: Cada microservicio se ejecuta de forma nativa. Asegúrate de tener las dependencias instaladas y las variables de entorno configuradas para conectarse a las bases de datos.
3. **Poblar las Bases de Datos**: Utiliza los scripts de semillas proporcionados en cada microservicio para cargar datos iniciales en MongoDB y PostgreSQL.
4. **Acceder a la Aplicación**: La aplicación frontend se conecta a los microservicios a través de sus respectivos puertos. Asegúrate de que todos los servicios estén en ejecución para una experiencia completa.

## Variables de Entorno
Cada microservicio requiere variables de entorno para la configuración de la base de datos y el registro en Eureka. Asegúrate de configurar correctamente estas variables antes de ejecutar los servicios.

## Seeders

### Auth Service (MongoDB)

El microservicio `auth-service` incluye un seeder de usuarios base en:

- `services/auth-service/src/database/seeds/seed-users.ts`

Usuarios creados/actualizados por defecto:

- `admin.principal@uptc.edu.co` (rol `admin`, activo, verificado)
- `estudiante.uno@uptc.edu.co` (rol `estudiante`, puntos iniciales 120)
- `estudiante.dos@uptc.edu.co` (rol `estudiante`, puntos iniciales 40, deshabilitado)

### Cómo correr el seeder

1. Asegúrate de tener MongoDB corriendo y `MONGO_URI` configurada.
2. Instala dependencias del servicio:

```bash
cd services/auth-service
npm install
```

3. Ejecuta el seeder:

```bash
npm run seed:users
```

El script es idempotente (si el usuario existe por correo, lo actualiza; si no existe, lo crea).