# El Muro Microservices - Complete Codebase Analysis

## Executive Summary

El Muro is a polyglot microservices architecture for academic and social management. The system comprises 5 microservices across 3 different technology stacks (Node.js/TypeScript, Python/FastAPI, and Java/Spring Boot) with a hierarchical data structure: Carreras → Materias → Temas → Posts, with an Auth Service managing user authentication and points.

---

## 1. ARCHITECTURE OVERVIEW

### Technology Stack

| Service | Language | Framework | Database | Port |
|---------|----------|-----------|----------|------|
| Auth Service | TypeScript/Node.js | Express | MongoDB | 3000 |
| Carreras Service | Python | FastAPI | PostgreSQL | 8001 |
| Materias Service | Python | FastAPI | PostgreSQL | 8004 |
| Temas Service | Python | FastAPI | MongoDB | 8003 |
| Posts Service | Java | Spring Boot | MongoDB + Redis | 8002 |
| Eureka Server | Java | Spring Cloud | - | 8761 |

### Data Relationships

```
User (Auth Service)
  ├── puntos (points system)
  ├── rol (admin/estudiante)
  └── correo (institutional email)

Carrera (Carreras Service)
  └── has many Materias

Materia (Materias Service)
  ├── belongs to Carrera
  └── has many Temas

Tema (Temas Service)
  ├── belongs to Materia
  └── has many Posts

Post (Posts Service)
  ├── belongs to Tema
  ├── belongs to User (author)
  ├── accessPoints (requires points to unlock)
  └── votes (tracked via votedByUsers set)
```

---

## 2. AUTH SERVICE (TypeScript/Express/MongoDB)

**Location**: `/services/auth-service/`

### Key Files

- **Model**: `/src/models/User.model.ts`
- **Routes**: `/src/routes/auth.routes.ts`
- **Service**: `/src/services/Auth.service.ts`
- **Controller**: `/src/controllers/Auth.controller.ts`
- **Types**: `/src/types/user.types.ts`

### User Schema

```typescript
{
  nombre: string,                          // User's full name
  correo: string,                          // Institutional email (@uptc.edu.co)
  password: string,                        // Bcrypt hashed (min 8 chars)
  rol: 'admin' | 'estudiante',             // User role
  apodo: string,                           // Unique nickname (auto-generated)
  puntos: number,                          // Points balance (default 0, min 0)
  estaActivo: boolean,                     // Active status (default true)
  isVerified: boolean,                     // Email verified via OTP (default false)
  sheerIdVerificationId: string,           // SheerID verification token
  otpCode: string,                         // OTP for email verification
  failedLoginAttempts: number,             // Failed login counter (default 0)
  lockUntil: Date | null,                  // Account lock timestamp
  timestamps: true                         // createdAt, updatedAt auto-managed
}
```

### User Roles

- **admin**: Can manage users, disable accounts, assign roles
- **estudiante**: Can create posts, vote, access content with points

### API Endpoints

#### Public (No Auth Required)
```
POST   /api/auth/register          - Register new user
POST   /api/auth/verify-otp        - Verify email with OTP code
POST   /api/auth/login             - Login and get JWT token
```

#### Authenticated (Requires JWT Token)
```
GET    /api/auth/me/puntos         - Get current user's points
                                     (estudiante role only)
```

#### Admin Only
```
PATCH  /api/auth/admin/users/:userId/disable     - Disable user account
PATCH  /api/auth/admin/users/:userId/role        - Change user role
```

#### Internal Service Only (HMAC Signed)
```
PATCH  /api/auth/internal/users/:userId/deduct-points      - Deduct user points
                                                            - Body: { points: number, reason?: string }
```

### JWT Token Structure

```typescript
interface JwtPayload {
  userId: string;                          // MongoDB ObjectId as string
  rol: 'admin' | 'estudiante';             // User role
  expiresIn: '24h'                         // Configured in env (JWT_EXPIRES_IN_HOURS)
}
```

### Registration Flow

1. User calls `/register` with nombre, correo, password
2. Service validates:
   - Institutional email (@uptc.edu.co)
   - No duplicate email
   - Calls SheerID API for student verification
3. Generates unique apodo (adjective_animal_number format)
4. Generates 6-digit OTP code
5. Sends OTP via SMTP email
6. Returns userId, correo, apodo in response
7. User must call `/verify-otp` with email and OTP
8. Only verified users can login

### Login Flow

1. User submits email and password
2. Service finds user by email
3. Checks account lock status (if locked, fails)
4. Verifies password with bcrypt
5. Validates user is verified (isVerified=true)
6. Validates user is active (estaActivo=true)
7. Resets failedLoginAttempts counter
8. Signs JWT token with userId and rol
9. Returns { token, user: {...} }

### Points System

**Deduction** (via internal service endpoint):
- Called by Posts Service when user creates post with accessPoints > 0
- Called by Posts Service when user accesses paid post
- Called by reason: "create-post-access" or "access-post"
- Validates: points > 0, user exists, user is student, user verified and active, sufficient balance
- Uses MongoDB transaction for atomicity
- Returns { userId, puntos } after deduction

**Addition** (endpoint appears to be missing in code, but referenced by Posts Service):
- Called by Posts Service when post receives a vote
- Posts Service calls: `authClient.addPoints(post.authorId, 1, "post-voted")`
- Reason: "post-voted"
- **Note**: This endpoint is NOT implemented in auth routes - needs to be added

### Security Features

- Password: Bcrypt hashed (10 salt rounds)
- HMAC signed internal service requests (x-service-id, x-service-timestamp, x-service-signature)
- Account lock after MAX_LOGIN_ATTEMPTS (default 5)
- Lock duration: LOGIN_LOCK_MINUTES (configurable)
- OTP validation
- Email verification required before login
- Role-based access control via middleware

### Environment Variables Required

```
MONGO_URI                      - MongoDB connection string
JWT_SECRET                     - Secret for JWT signing
JWT_EXPIRES_IN_HOURS          - Token expiration (default 24)
SMTP_HOST, SMTP_PORT          - Email server config
SMTP_USER, SMTP_PASS          - Email credentials
SMTP_FROM                     - From email address
SHEERID_BASE_URL              - SheerID API endpoint
SHEERID_API_TOKEN             - SheerID authentication token
MAX_LOGIN_ATTEMPTS            - Failed login threshold (default 5)
LOGIN_LOCK_MINUTES            - Lock duration in minutes
```

---

## 3. CARRERAS SERVICE (Python/FastAPI/PostgreSQL)

**Location**: `/services/carreras-service/`

### Key Files

- **Model**: `/app/models/carrera.py`
- **Router**: `/app/routers/carreras.py`
- **Service**: `/app/services/carrera_service.py`
- **Schema**: `/app/schemas/carrera.py`

### Carrera Model (SQLAlchemy)

```python
class Carrera(Base):
    __tablename__ = "carreras"
    
    id: int                      # Primary key, auto-increment
    nombre: str                  # Unique, indexed
    descripcion: str             # Optional, nullable
    created_at: datetime         # Auto-set to UTC now
    updated_at: datetime         # Auto-update on modification
```

### API Endpoints

#### Public (No Auth)
```
GET    /api/carreras/_exists/{carrera_id}       - Check if carrera exists
                                                  Response: {"exists": true/false}
```

#### Authenticated (JWT Required)
```
GET    /api/carreras/                           - List all carreras (paginated)
                                                  Query params: skip=0, limit=100
GET    /api/carreras/{carrera_id}               - Get carrera with nested materias
POST   /api/carreras/crear                      - Create new carrera
                                                  Body: { nombre, descripcion? }
PUT    /api/carreras/{carrera_id}               - Update carrera (admin only)
DELETE /api/carreras/{carrera_id}               - Delete carrera + related materias (admin only)
```

### Inter-Service Communication

**Materias Service Client** in carrera_service.py:
- GET `/api/materias/carrera/{carrera_id}` → Get materias for a carrera
- DELETE `/api/materias/carrera/{carrera_id}/all` → Delete all materias when carrera deleted
- Timeout: 5 seconds
- On failure, logs warning but continues (graceful degradation)

### Business Logic

- **Create**: Validates unique nombre (case-insensitive), creates in DB
- **Get Detail**: Returns carrera + calls materias-service to fetch related materias
- **Update**: Validates new nombre uniqueness if changed
- **Delete**: Calls materias-service to delete all related materias first, then deletes carrera locally

---

## 4. MATERIAS SERVICE (Python/FastAPI/PostgreSQL)

**Location**: `/services/materias-service/`

### Key Files

- **Model**: `/app/models/materia.py`
- **Router**: `/app/routers/materias.py`
- **Service**: `/app/services/materia_service.py`
- **Schema**: `/app/schemas/materia.py`

### Materia Model (SQLAlchemy)

```python
class Materia(Base):
    __tablename__ = "materias"
    
    id: int                      # Primary key, auto-increment
    nombre: str                  # Indexed
    descripcion: str             # Optional
    semestre: int                # 1-10, indexed
    carrera_id: int              # Indexed (no FK, validated via API)
    created_at: datetime         # Auto-set
    updated_at: datetime         # Auto-update
```

### API Endpoints

#### Authenticated (JWT Required)
```
GET    /api/materias/                                - List all materias
                                                      Query params: skip=0, limit=100, carrera_id?
GET    /api/materias/carrera/{carrera_id}           - List materias by carrera
GET    /api/materias/{materia_id}                   - Get materia detail
POST   /api/materias/crear                          - Create materia (admin only)
                                                      Body: { nombre, descripcion?, semestre, carrera_id }
PUT    /api/materias/{materia_id}                   - Update materia (admin only)
```

#### Internal Service Only (No Auth Required)
```
DELETE /api/materias/carrera/{carrera_id}/all      - Delete all materias by carrera
                                                     Called by carreras-service
```

### Inter-Service Communication

**Carreras Service Client** in materia_service.py:
- GET `/api/carreras/_exists/{carrera_id}` → Validate carrera exists before creating materia
- Timeout: 5 seconds
- On error: Returns 404 if carrera doesn't exist, 503 if service unavailable

### Business Logic

- **Create**: Validates carrera exists via carreras-service, enforces unique nombre+carrera combination
- **Get by Carrera**: Simple query by carrera_id with pagination
- **Delete by Carrera**: Called by carreras-service (internal), deletes all related materias

---

## 5. TEMAS SERVICE (Python/FastAPI/MongoDB)

**Location**: `/services/temas-service/`

### Key Files

- **Repository**: `/app/repositories/tema_repository.py` (MongoDB abstraction)
- **Router**: `/app/routers/temas.py`
- **Service**: `/app/services/tema_service.py`
- **Schema**: `/app/schemas/tema.py`
- **External Clients**: `/app/services/external_clients.py`

### Tema Document (MongoDB)

```python
{
    _id: ObjectId,                      # MongoDB ID
    nombre: str,                        # Required
    descripcion: str,                   # Optional
    materia_id: int,                    # Reference to materias-service
    esta_activo: bool,                  # Default true
    created_at: datetime,               # UTC timestamp
    updated_at: datetime                # UTC timestamp
}
```

### Repository Pattern

The service uses an abstract `TemaRepository` with two implementations:

1. **MongoTemaRepository** (Production)
   - Uses PyMongo to interact with MongoDB
   - Converts _id to id in serialization
   - Implements filtering by materia_id, active status

2. **InMemoryTemaRepository** (Testing)
   - In-memory storage for unit tests
   - Mimics MongoDB behavior

### API Endpoints

#### Authenticated (JWT Required)
```
GET    /api/temas/                           - List all temas (active by default)
                                              Query params: materia_id?, include_inactive=false
GET    /api/temas/{tema_id}                  - Get tema detail
POST   /api/temas/                           - Create tema (admin only)
                                              Body: { nombre, descripcion?, materia_id }
PUT    /api/temas/{tema_id}                  - Update tema (admin only)
PATCH  /api/temas/{tema_id}/disable          - Soft-delete tema (admin only)
GET    /api/temas/{tema_id}/posts            - Get tema with related posts
```

### Inter-Service Communication

**MateriasClient**:
- GET `/api/materias/{materia_id}` → Validate materia exists before creating/updating tema
- Timeout: 5 seconds
- On error: 404 if materia not found, 503 if service down

**PostsClient**:
- GET `/api/posts?temaId={tema_id}` → Get posts for a tema
- Tries multiple endpoints (resilience)
- Timeout: 5 seconds
- Returns empty list on error (graceful degradation)

### Business Logic

- **Create**: Validates materia exists via materias-service
- **List**: Returns active temas by default (or all if include_inactive=true)
- **Disable**: Sets esta_activo=false (soft delete)
- **Get Posts**: Fetches tema + calls posts-service to get related posts

---

## 6. POSTS SERVICE (Java/Spring Boot/MongoDB)

**Location**: `/services/posts-service/`

### Key Files

- **Model**: `/src/main/java/...model/Post.java`
- **Controller**: `/src/main/java/.../controller/PostController.java`
- **Service**: `/src/main/java/.../service/PostService.java`
- **Cache Service**: `/src/main/java/.../service/PointsCacheService.java`
- **Auth Client**: `/src/main/java/.../client/impl/AuthWebClient.java`
- **DTOs**: `/src/main/java/.../dto/CreatePostRequest.java`, etc.

### Post Document (MongoDB)

```java
{
    id: int,                           // Auto-generated (sequential)
    title: string,                     // Required
    description: string,               // Required
    fileUrl: string,                   // Optional
    textContent: string,               // Optional
    votes: int,                        // Default 0
    accessPoints: int,                 // Points required to access (default 0)
    blocked: boolean,                  // true if accessPoints > 0
    createdAt: LocalDateTime,          // Auto-set
    authorId: int,                     // Reference to auth-service user ID
    topicId: int,                      // Reference to temas-service tema ID
    unlockedByUsers: Set<int>,         // Users who paid to access (Set for deduplication)
    votedByUsers: Set<int>             // Users who voted (Set for deduplication)
}
```

### API Endpoints

#### All Require JWT Authentication (Estudiante/Admin)
```
POST   /api/posts                     - Create post
                                       Body: { title, description, fileUrl?, textContent?, 
                                              accessPoints, topicId }
                                       Returns: PostResponse (201)

GET    /api/posts/{postId}            - Access/unlock post (deducts points if blocked)
                                       Returns: PostResponse (200)

GET    /api/posts/feed/latest?limit=20  - Get latest posts (feed)
                                       Cached response, 20-100 posts
                                       Returns: List[PostResponse] (200)

PUT    /api/posts/{postId}            - Update post (owner only, within 10 mins)
                                       Body: { title, description, fileUrl?, 
                                              textContent?, accessPoints, topicId }
                                       Returns: PostResponse (200)

POST   /api/posts/{postId}/vote       - Vote on post (add 1 vote, +1 point to author)
                                       Returns: PostResponse (200)

DELETE /api/posts/{postId}            - Delete post (owner or admin only)
                                       Returns: 204 No Content
```

### Post Creation Flow

1. **Validate**: User is authenticated and is 'estudiante' role
2. **Check Points**: If accessPoints > 0, verify user has sufficient points
3. **Deduct Points**: Call auth-service to deduct accessPoints from user
4. **Create Post**: Set id (auto-increment), blocked = (accessPoints > 0)
5. **Save**: Store in MongoDB
6. **Cache Invalidate**: Clear FEED_LATEST cache
7. **Return**: PostResponse

### Post Access/Unlock Flow

1. **Validate**: User is authenticated
2. **Find Post**: Get from MongoDB
3. **Check Locked Status**:
   - If blocked AND user not author:
     - Check if already unlocked by user (in unlockedByUsers set)
     - If not unlocked:
       - Verify user has sufficient points
       - Deduct points from auth-service
       - Add user to unlockedByUsers set
4. **Return**: PostResponse with content

### Post Voting Flow

1. **Validate**: User is authenticated, not post author
2. **Check Vote Status**: Ensure user not already in votedByUsers (idempotent via Set)
3. **Add Vote**:
   - Add user to votedByUsers set
   - Increment votes counter
4. **Award Points**: Call auth-service to add 1 point to post author
5. **Cache Invalidate**: Clear FEED_LATEST cache
6. **Return**: Updated PostResponse

### Post Update Flow

1. **Validate**: User is authenticated and is 'estudiante'
2. **Ownership Check**: Only post author can update
3. **Time Window Check**: Only allow updates within 10 minutes of creation
4. **Topic Validation**: Verify topicId exists in temas-service
5. **Update Fields**: title, description, fileUrl, textContent, accessPoints, blocked, topicId
6. **Save**: Update MongoDB document
7. **Cache Invalidate**: Clear FEED_LATEST cache

### Inter-Service Communication

**AuthClient** (via HMAC-signed requests):
- GET `POST /internal/users/{userId}/points` → Get user's current points (cached)
- PATCH `/internal/users/{userId}/deduct-points` → Deduct points with reason
- PATCH `/internal/users/{userId}/add-points` → Add points with reason
- All requests signed with: x-service-id, x-service-timestamp, x-service-signature (HMAC-SHA256)

**TopicClient**:
- GET `/api/temas/{topicId}` or similar → Validate topic exists
- Timeout: 5 seconds
- On error: Throws 400/503

### Caching Strategy

Uses Spring Cache abstractions with Redis:

1. **USER_POINTS**: Cache user points by userId
   - Invalidated after each points change
   - Used by PointsCacheService

2. **FEED_LATEST**: Cache latest feed by limit parameter
   - Invalidated on create, update, delete, vote operations
   - Reduces database load for frequent feed requests

### Points Economy

**How Points are Earned**:
- Each vote on a post = +1 point to author (not capped)
- Base points on registration: 0 (or seeded data)

**How Points are Spent**:
- Creating post with accessPoints > 0 = spend X points
- Accessing locked post = spend X points (post's accessPoints)

**Reasons Tracked**:
- "create-post-access": Initial points spent when creating post with accessPoints
- "access-post": Points spent to access blocked posts
- "post-voted": Points awarded for receiving votes

---

## 7. DATA RELATIONSHIPS SUMMARY

### Relationship Chain

```
User (Auth Service - MongoDB)
  ├─ id: string (MongoDB ObjectId)
  └─ puntos: number

Carrera (Carreras Service - PostgreSQL)
  ├─ id: int
  └─ Materias (via /api/materias/carrera/{carrera_id})

Materia (Materias Service - PostgreSQL)
  ├─ id: int
  ├─ carrera_id: int (FK reference)
  └─ Temas (via /api/temas?materia_id={id})

Tema (Temas Service - MongoDB)
  ├─ _id: ObjectId (returned as id: string)
  ├─ materia_id: int (reference)
  └─ Posts (via /api/posts?temaId={id} or /api/temas/{id}/posts)

Post (Posts Service - MongoDB)
  ├─ id: int
  ├─ topicId: int (= Tema.id)
  ├─ authorId: int (= User.id from Auth Service)
  ├─ accessPoints: int (points required to access)
  ├─ votes: int (accumulated)
  ├─ votedByUsers: Set<int> (user IDs who voted)
  └─ unlockedByUsers: Set<int> (user IDs who paid to access)
```

### Cross-Service Data Calls

1. **Carreras** → **Materias**
   - When fetching carrera detail: GET /api/materias/carrera/{carrera_id}
   - When deleting carrera: DELETE /api/materias/carrera/{carrera_id}/all

2. **Materias** → **Carreras**
   - When creating materia: GET /api/carreras/_exists/{carrera_id}

3. **Temas** → **Materias**
   - When creating/updating tema: GET /api/materias/{materia_id}

4. **Temas** → **Posts**
   - When getting posts for tema: GET /api/posts?temaId={tema_id}

5. **Posts** → **Auth Service**
   - Get user points: POST /internal/users/{userId}/points
   - Deduct points: PATCH /internal/users/{userId}/deduct-points
   - Add points: PATCH /internal/users/{userId}/add-points

6. **Posts** → **Temas**
   - When creating post: GET /api/temas/{topicId} (implied validation)

---

## 8. EXPECTED MISSING IMPLEMENTATIONS

Based on code analysis, the following needs implementation:

### 1. **Auth Service - Add Points Endpoint**
Posts Service calls `authClient.addPoints(userId, 1, "post-voted")` but:
- No endpoint exists in `/api/auth/routes/auth.routes.ts`
- No method exists in `Auth.service.ts`
- No method exists in `Auth.controller.ts`

**Should be**:
```
PATCH  /api/auth/internal/users/{userId}/add-points
       validateInternalService middleware
       Body: { points: number, reason?: string }
```

### 2. **Posts Service - Get Posts by Tema**
The `/api/temas/{tema_id}/posts` endpoint in temas-service calls:
```python
posts_client.get_posts_by_tema(tema_id, authorization)
```
But posts service doesn't appear to have an endpoint like:
```
GET    /api/posts?temaId={tema_id}
```

Should implement query parameter support for temaId.

### 3. **Service Discovery Missing**
Auth Service doesn't register with Eureka (noted in ENDPOINTS.md as "Manual"). Should integrate Netflix Eureka client.

### 4. **API Gateway Missing**
Each service exposes its own port directly. Should add API Gateway for unified entry point.

---

## 9. FILE STRUCTURE QUICK REFERENCE

```
services/
├── auth-service/
│   └── src/
│       ├── models/User.model.ts          (MongoDB schema)
│       ├── types/user.types.ts            (TypeScript interfaces)
│       ├── routes/auth.routes.ts          (API route definitions)
│       ├── services/Auth.service.ts       (Business logic)
│       ├── controllers/Auth.controller.ts (Request handling)
│       ├── middlewares/                   (Auth, role validation)
│       └── database/seeds/seed-users.ts   (Initial data)
│
├── carreras-service/
│   └── app/
│       ├── models/carrera.py              (SQLAlchemy model)
│       ├── schemas/carrera.py             (Pydantic schemas)
│       ├── routers/carreras.py            (Route definitions)
│       └── services/carrera_service.py    (Business logic)
│
├── materias-service/
│   └── app/
│       ├── models/materia.py              (SQLAlchemy model)
│       ├── schemas/materia.py             (Pydantic schemas)
│       ├── routers/materias.py            (Route definitions)
│       └── services/materia_service.py    (Business logic)
│
├── temas-service/
│   └── app/
│       ├── repositories/tema_repository.py (MongoDB abstraction)
│       ├── schemas/tema.py                (Pydantic schemas)
│       ├── routers/temas.py               (Route definitions)
│       ├── services/tema_service.py       (Business logic)
│       └── services/external_clients.py   (Inter-service calls)
│
└── posts-service/
    └── src/main/java/.../
        ├── model/Post.java                (MongoDB document)
        ├── controller/PostController.java (Request handling)
        ├── service/PostService.java       (Business logic)
        ├── service/PointsCacheService.java (Redis caching)
        ├── client/AuthClient.java         (Interface)
        ├── client/impl/AuthWebClient.java (Implementation)
        └── dto/CreatePostRequest.java     (Request DTOs)
```

---

## 10. IMPORTANT CONFIGURATION NOTES

### Internal Service Authentication

Posts Service communicates with Auth Service using HMAC-SHA256 signing:

**Headers Required**:
```
x-service-id: string                  // Service identifier
x-service-timestamp: long              // Current epoch milliseconds
x-service-signature: string            // HMAC-SHA256(serviceId + timestamp + method + path)
```

**Middleware** (Auth Service):
- `validateInternalService` middleware verifies the signature
- HMAC key comes from `INTERNAL_SERVICE_SECRET` env variable

### Email Verification

Auth Service uses:
- **SMTP**: For sending OTP codes
- **SheerID**: For student verification during registration
- **OTP**: 6-digit code sent to institutional email

Registration cannot complete without:
1. Valid SheerID API response
2. OTP verification email delivered
3. User confirming OTP

### Role-Based Access

```
Public Endpoints:
  - /api/auth/register
  - /api/auth/verify-otp
  - /api/auth/login
  - /api/carreras/_exists/{id}
  - /api/temas/{id}/disable (marked admin in code)

Admin Only:
  - All POST/PUT/DELETE in carreras, materias, temas
  - /api/auth/admin/* endpoints

Estudiante Only:
  - /api/auth/me/puntos
  - POST /api/posts
  - POST /api/posts/{id}/vote
  - GET /api/posts/feed/*

Internal Service Only:
  - /api/auth/internal/users/{userId}/deduct-points
  - /api/auth/internal/users/{userId}/add-points (missing)
```

---

## 11. KEY SERVICES LOCATIONS (ABSOLUTE PATHS)

```
Auth Service:
  - Model: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/auth-service/src/models/User.model.ts
  - Routes: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/auth-service/src/routes/auth.routes.ts
  - Service: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/auth-service/src/services/Auth.service.ts

Carreras Service:
  - Model: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/carreras-service/app/models/carrera.py
  - Router: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/carreras-service/app/routers/carreras.py
  - Service: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/carreras-service/app/services/carrera_service.py

Materias Service:
  - Model: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/materias-service/app/models/materia.py
  - Router: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/materias-service/app/routers/materias.py
  - Service: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/materias-service/app/services/materia_service.py

Temas Service:
  - Repository: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/temas-service/app/repositories/tema_repository.py
  - Router: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/temas-service/app/routers/temas.py
  - Service: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/temas-service/app/services/tema_service.py

Posts Service:
  - Model: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/posts-service/src/main/java/co/edu/uptc/swii/posts_service/model/Post.java
  - Controller: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/posts-service/src/main/java/co/edu/uptc/swii/posts_service/controller/PostController.java
  - Service: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/posts-service/src/main/java/co/edu/uptc/swii/posts_service/service/PostService.java
  - Auth Client: /Users/davidrodriguez/Desktop/Universidad/Software/Reto1er50/El-Muro-Microservicio/services/posts-service/src/main/java/co/edu/uptc/swii/posts_service/client/impl/AuthWebClient.java
```

---

## 12. SUMMARY TABLE - ENDPOINTS BY SERVICE

| Service | Create | Read | Update | Delete | Internal |
|---------|--------|------|--------|--------|----------|
| **Auth** | POST /register | GET /me/puntos | PATCH /admin/*/role | PATCH /admin/*/disable | PATCH /internal/*/deduct-points<br>PATCH /internal/*/add-points (MISSING) |
| **Carreras** | POST /crear | GET /, GET /{id}, GET /_exists/{id} | PUT /{id} | DELETE /{id} | - |
| **Materias** | POST /crear | GET /, GET /carrera/{id}, GET /{id} | PUT /{id} | DELETE /{id} | DELETE /carrera/{id}/all |
| **Temas** | POST / | GET /, GET /{id}, GET /{id}/posts | PUT /{id} | PATCH /{id}/disable | - |
| **Posts** | POST / | GET /{id}, GET /feed/latest | PUT /{id} | DELETE /{id} | POST /{id}/vote |

