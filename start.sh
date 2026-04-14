#!/bin/bash

# ============================================================================
# Script para iniciar El Muro - Microservices Architecture
# Inicia todos los servicios necesarios para el proyecto
# ============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRASTRUCTURE_DIR="$PROJECT_ROOT/infrastructure"
SERVICES_DIR="$PROJECT_ROOT/services"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    print_success "Docker verificado"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    print_success "Docker Compose verificado"
}

start_infrastructure() {
    print_header "Iniciando Infraestructura (Eureka, Bases de Datos, Redis)"
    
    cd "$INFRASTRUCTURE_DIR"
    
    # Eliminar versión obsoleta del yaml
    if grep -q "^version:" docker-compose.yml; then
        print_warning "Eliminando atributo version obsoleto de docker-compose.yml"
        sed -i.bak '/^version:/d' docker-compose.yml
        rm -f docker-compose.yml.bak
    fi
    
    docker-compose up -d eureka-server carreras-db materias-db mongo-db redis-db
    print_success "Infraestructura iniciada"
    
    # Esperar a que Eureka esté listo
    print_warning "Esperando a que Eureka esté disponible..."
    sleep 10
    
    for i in {1..30}; do
        if curl -s http://localhost:8761/eureka/apps > /dev/null 2>&1; then
            print_success "Eureka está disponible"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Timeout esperando Eureka"
            exit 1
        fi
        echo -n "."
        sleep 1
    done
}

start_docker_services() {
    print_header "Iniciando Servicios en Docker"
    
    cd "$INFRASTRUCTURE_DIR"
    
    docker-compose up -d carreras-service materias-service temas-service
    print_success "Servicios Docker iniciados (Carreras, Materias, Temas)"
    
    # Esperar a que los servicios se registren en Eureka
    sleep 5
}

start_auth_service() {
    print_header "Iniciando Auth Service (Node.js)"
    
    cd "$SERVICES_DIR/auth-service"
    
    # Verificar que npm esté instalado
    if ! command -v npm &> /dev/null; then
        print_error "npm no está instalado"
        exit 1
    fi
    
    # Matar proceso anterior si existe
    pkill -f "node.*auth-service" 2>/dev/null || true
    sleep 1
    
    # Iniciar en background
    npm start > /tmp/auth-service.log 2>&1 &
    
    # Esperar a que esté listo
    print_warning "Esperando Auth Service..."
    sleep 5
    
    for i in {1..30}; do
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            print_success "Auth Service está disponible"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Timeout esperando Auth Service"
            tail -20 /tmp/auth-service.log
            exit 1
        fi
        echo -n "."
        sleep 1
    done
}

start_posts_service() {
    print_header "Iniciando Posts Service (Java/Spring Boot)"
    
    cd "$SERVICES_DIR/posts-service"
    
    # Encontrar Java
    JAVA_HOME=$(/usr/libexec/java_home -v 21+ 2>/dev/null || /usr/libexec/java_home -v 25+ 2>/dev/null)
    
    if [ -z "$JAVA_HOME" ]; then
        # Intentar con el path de brew
        if [ -d "/opt/homebrew/Cellar/openjdk" ]; then
            JAVA_VERSION=$(ls -1 /opt/homebrew/Cellar/openjdk | sort -V | tail -1)
            JAVA_HOME="/opt/homebrew/Cellar/openjdk/$JAVA_VERSION"
        else
            print_error "Java no encontrado"
            exit 1
        fi
    fi
    
    export JAVA_HOME
    print_warning "Usando Java: $JAVA_HOME"
    
    # Matar proceso anterior si existe
    pkill -f "java.*posts-service" 2>/dev/null || true
    sleep 1
    
    # Iniciar en background
    $JAVA_HOME/bin/java -jar target/posts-service-0.0.1-SNAPSHOT.jar > /tmp/posts-service.log 2>&1 &
    
    # Esperar a que esté listo
    print_warning "Esperando Posts Service..."
    sleep 10
    
    for i in {1..60}; do
        if curl -s http://localhost:8002/actuator/health > /dev/null 2>&1; then
            print_success "Posts Service está disponible"
            break
        fi
        if [ $i -eq 60 ]; then
            print_warning "Posts Service tardó más de lo esperado, continuando..."
            break
        fi
        echo -n "."
        sleep 1
    done
}

verify_services() {
    print_header "Verificando Servicios"
    
    # Array de servicios a verificar
    declare -a services=(
        "Auth:http://localhost:3000/health"
        "Posts:http://localhost:8002/actuator/health"
        "Carreras:http://localhost:8001/health"
        "Materias:http://localhost:8004/health"
        "Temas:http://localhost:8003/health"
        "Eureka:http://localhost:8761/eureka/apps"
    )
    
    echo ""
    for service in "${services[@]}"; do
        IFS=':' read -r name url <<< "$service"
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$name Service"
        else
            print_warning "$name Service (no responde aún)"
        fi
    done
    
    echo ""
    print_header "Servicios Registrados en Eureka"
    curl -s http://localhost:8761/eureka/apps | grep -o '<app>[^<]*</app>' | sed 's/<[^>]*>//g' | sort | sed 's/^/  ✅ /'
}

show_summary() {
    print_header "🚀 El Muro Microservices - INICIADO"
    
    echo ""
    echo -e "${BLUE}Servicios disponibles:${NC}"
    echo "  🔐 Auth Service      → http://localhost:3000"
    echo "  📝 Posts Service     → http://localhost:8002"
    echo "  🏫 Carreras Service  → http://localhost:8001"
    echo "  📚 Materias Service  → http://localhost:8004"
    echo "  🎯 Temas Service     → http://localhost:8003"
    echo "  📋 Eureka Server     → http://localhost:8761"
    echo ""
    echo -e "${BLUE}Bases de Datos:${NC}"
    echo "  🐘 PostgreSQL Carreras → localhost:5434"
    echo "  🐘 PostgreSQL Materias → localhost:5433"
    echo "  🍃 MongoDB             → localhost:27017"
    echo "  🔴 Redis               → localhost:6379"
    echo ""
    echo -e "${BLUE}Ver logs:${NC}"
    echo "  tail -f /tmp/auth-service.log"
    echo "  tail -f /tmp/posts-service.log"
    echo "  docker-compose -f $INFRASTRUCTURE_DIR/docker-compose.yml logs -f [service]"
    echo ""
}

# Main execution
main() {
    print_header "🚀 Iniciando El Muro - Microservices Architecture"
    
    check_docker
    check_docker_compose
    
    start_infrastructure
    start_docker_services
    start_auth_service
    start_posts_service
    
    verify_services
    show_summary
}

# Run main
main "$@"
