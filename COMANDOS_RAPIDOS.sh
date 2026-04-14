#!/bin/bash

# ============================================================
# COMANDOS RÁPIDOS - Revisión y Pruebas de Microservicios
# ============================================================

echo "🚀 Comandos Rápidos para El Muro - Microservicios"
echo ""

# ============================================================
# 1. INFRAESTRUCTURA
# ============================================================

echo "📦 1. INFRAESTRUCTURA"
echo "   Iniciar todos los servicios de infraestructura:"
echo "   cd infrastructure && docker-compose up -d"
echo ""
echo "   Ver estado:"
echo "   docker-compose ps"
echo ""

# ============================================================
# 2. EUREKA SERVER
# ============================================================

echo "📡 2. EUREKA SERVER (Puerto 8761)"
echo "   Ver dashboard: http://localhost:8761"
echo ""
echo "   Listar todas las aplicaciones:"
echo "   curl -s http://localhost:8761/eureka/apps"
echo ""
echo "   Ver una aplicación específica:"
echo "   curl -s http://localhost:8761/eureka/apps/AUTH-SERVICE"
echo "   curl -s http://localhost:8761/eureka/apps/POSTS-SERVICE"
echo ""

# ============================================================
# 3. AUTH SERVICE
# ============================================================

echo "🔐 3. AUTH SERVICE (Puerto 3000)"
echo ""
echo "   Health Check:"
echo "   curl -s http://localhost:3000/health"
echo ""
echo "   Registro (requiere @uptc.edu.co):"
echo "   curl -X POST http://localhost:3000/api/auth/register \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"correo\": \"test@uptc.edu.co\", \"contraseña\": \"Pass123!\"}'"
echo ""
echo "   Login:"
echo "   curl -X POST http://localhost:3000/api/auth/login \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"correo\": \"test@uptc.edu.co\", \"contraseña\": \"Pass123!\"}'"
echo ""

# ============================================================
# 4. POSTS SERVICE
# ============================================================

echo "📝 4. POSTS SERVICE (Puerto 8002 - Java)"
echo ""
echo "   Compilar:"
echo "   cd services/posts-service && mvn clean package -DskipTests"
echo ""
echo "   Ejecutar (con Java 21+):"
echo "   export JAVA_HOME=/opt/homebrew/Cellar/openjdk/25.0.1/libexec/openjdk.jdk/Contents/Home"
echo "   java -jar target/posts-service-0.0.1-SNAPSHOT.jar"
echo ""
echo "   Ver si está registrado en Eureka:"
echo "   curl -s http://localhost:8761/eureka/apps/POSTS-SERVICE"
echo ""
echo "   Intentar acceso (requiere token JWT):"
echo "   curl -v http://localhost:8002/api/posts/1"
echo ""

# ============================================================
# 5. CARRERAS SERVICE
# ============================================================

echo "🎓 5. CARRERAS SERVICE (Puerto 8001 - Python/FastAPI)"
echo ""
echo "   Iniciar via Docker:"
echo "   cd infrastructure && docker-compose up -d carreras-service"
echo ""
echo "   Health Check:"
echo "   curl -s http://localhost:8001/health"
echo ""
echo "   Ver OpenAPI:"
echo "   curl -s http://localhost:8001/docs"
echo ""
echo "   Obtener Carreras (requiere token):"
echo "   curl -s http://localhost:8001/api/carreras/"
echo ""

# ============================================================
# 6. HERRAMIENTAS
# ============================================================

echo "🔧 6. HERRAMIENTAS"
echo ""
echo "   Ver logs de un contenedor:"
echo "   docker logs -f eureka-server"
echo "   docker logs -f carreras-service"
echo ""
echo "   Ver logs de archivo:"
echo "   tail -f /tmp/posts-service.log"
echo "   tail -f /tmp/auth-service.log"
echo ""

# ============================================================
# 7. VERIFICACIÓN COMPLETA
# ============================================================

echo "✅ 7. VERIFICACIÓN COMPLETA"
echo ""
echo "   Script para verificar todos los servicios:"
echo ""
echo "   #!/bin/bash"
echo "   echo 'Eureka:' && curl -s http://localhost:8761/eureka/apps | grep -c application"
echo "   echo 'Auth:' && curl -s http://localhost:3000/health"
echo "   echo 'Posts:' && curl -s -o /dev/null -w '%{http_code}' http://localhost:8002/api/posts/1"
echo "   echo 'Carreras:' && curl -s http://localhost:8001/health"
echo ""

# ============================================================
# 8. TROUBLESHOOTING
# ============================================================

echo "🐛 8. TROUBLESHOOTING"
echo ""
echo "   ¿Posts no inicia? Verifica Java version:"
echo "   java -version"
echo "   # Debe ser 21+, si es 17, usa:"
echo "   export JAVA_HOME=/opt/homebrew/Cellar/openjdk/25.0.1/libexec/openjdk.jdk/Contents/Home"
echo ""
echo "   ¿Carreras no conecta a BD? Verifica PostgreSQL:"
echo "   docker exec carreras-db psql -U usuario -d carreras_db -c '\\\\dt'"
echo ""
echo "   ¿MongoDB no accesible? Verifica contenedor:"
echo "   docker logs mongo-db | tail -20"
echo ""

echo ""
echo "✨ Para más información, ver:"
echo "   - RESUMEN_FINAL_PRUEBAS.md"
echo "   - PRUEBAS_ENDPOINTS_CURL.md"
echo "   - LEEME_PRIMERO.md"
