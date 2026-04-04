# Guía de Pull Requests — El Muro

Bienvenido al workflow de El Muro. Esta guía te ayuda a contribuir de manera ordenada y eficiente.

## Antes de Hacer un Pull Request

### 1. **Sincroniza tu rama con `main`**
```bash
git checkout main
git pull origin main
git checkout tu-rama
git rebase main
```

### 2. **Asegúrate de que tu código funciona**
- El servicio arranca sin errores
- Las conexiones a BD están configuradas
- Si hay tests, todos pasan
- El código respeta el estilo del proyecto

### 3. **Carga los datos de semilla si aplica**
Si tu PR incluye cambios en modelos o esquemas, ejecuta los scripts correspondientes:
```bash
# Ejemplo para auth-service
cd services/auth-service/src/database/seeds
# Ejecuta el script de población
```

## 📝 Estructura del Pull Request

### **Título claros y descriptivos**
- `feat: Agregar autenticación con JWT en auth-service`
- `fix: Corregir conexión a MongoDB en posts-service`
- `docs: Actualizar README con instrucciones de setup`
- `cambios` | `fix` | `actualización`

### **Convenciones de nomenclatura**
Usamos **Conventional Commits**:
- `feat:` — Nueva funcionalidad
- `fix:` — Corrección de bugs
- `docs:` — Cambios en documentación
- `refactor:` — Reestructuración sin cambiar funcionalidad
- `test:` — Agregar o modificar tests
- `chore:` — Cambios de build, dependencias, configuración

## Checklist antes de abrir el PR

- Mi rama está actualizada con `main`
- He probado que mi código funciona localmente
- He actualizado el README si hay cambios importantes
- He agregado datos de semilla si fue necesario
- No hay archivos sensibles (`.env` real, credenciales, etc.)
- Mi código sigue el estilo del servicio correspondiente

## Información del PR

Por favor, completa la descripción incluyendo:

### **Qué cambios hago**
Describe brevemente qué problema resuelves o qué feature agregas.

### **Microservicio(s) afectado(s)**
- auth-service (David)
- materias-service (Karen)
- posts-service (Angela)
- temas-service (Anthony)
- frontend (Todos)
- infrastructure (Todos)

### **Testing**
¿Cómo probaste tu cambio? Pasos concretos reproducibles.

### **Variables de entorno o configuración**
¿Se necesitan cambios en `.env` o configuración?

## Después de abrir el PR

1. **Pide review** a los dueños del servicio afectado
2. **Responde comentarios** de forma constructiva
3. **Haz rebase** si hay conflictos con `main`
4. **No mergues tu propio PR** (espera al menos 1 aprobación)

## Rutas por responsable

| Servicio | Puerto | Responsable |
|----------|--------|-------------|
| auth-service | 3000 | David |
| materias-service | 8001 | Karen |
| posts-service | 8002 | Angela |
| temas-service | 8003 | Anthony |
| frontend | 3001 | Todos |
| infrastructure | — | Todos |

## Preguntas Frecuentes

**P: ¿Puedo hacer PR directamente a `main` desde mi rama?**
R: Sí, siempre que esté actualizada y pase los checks.

**P: ¿Qué pasa si hay conflictos?**
R: Resuélvelos localmente con `git rebase main`, prueba nuevamente y haz push.

**P: ¿Cuánto tiempo tarda la revisión?**
R: Idealmente 24-48 horas. Si es urgente, menciona al equipo en el PR.

**P: ¿Puedo cambiar algo después de hacer el PR?**
R: Sí, haz commit, esa vez sutil no abierto la rama otra vez en tu editor local y haz push. Se actualizará automáticamente.

---

