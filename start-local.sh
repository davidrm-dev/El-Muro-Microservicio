#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$ROOT_DIR/infrastructure"
SERVICES_DIR="$ROOT_DIR/services"

green() { printf "[OK] %s\n" "$1"; }
warn() { printf "[WARN] %s\n" "$1"; }
info() { printf "[INFO] %s\n" "$1"; }
err() { printf "[ERR] %s\n" "$1"; }

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    err "Falta comando requerido: $1"
    exit 1
  fi
}

wait_http() {
  local url="$1"
  local retries="${2:-40}"
  local delay="${3:-2}"
  local i
  for ((i=1; i<=retries; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

kill_port_if_busy() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids="$(lsof -ti tcp:"$port" || true)"
    if [[ -n "$pids" ]]; then
      warn "Liberando puerto $port"
      kill -9 $pids || true
    fi
  fi
}

start_infra() {
  info "Levantando infraestructura docker (eureka + db + redis)"
  docker-compose -f "$INFRA_DIR/docker-compose.yml" up -d --remove-orphans
  wait_http "http://localhost:8761/eureka/apps" 60 2 || {
    err "Eureka no estuvo disponible a tiempo"
    exit 1
  }
  green "Infraestructura lista"
}

start_auth() {
  info "Iniciando auth-service"
  kill_port_if_busy 3000
  (cd "$SERVICES_DIR/auth-service" && npm run dev > auth-service.log 2>&1 &) 
  wait_http "http://localhost:3000/health" 40 2 || {
    err "auth-service no responde"
    exit 1
  }
  green "auth-service listo"
}

start_carreras() {
  info "Iniciando carreras-service"
  kill_port_if_busy 8001
  (cd "$SERVICES_DIR/carreras-service" && ./.venv_local/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > carreras-local.log 2>&1 &) 
  wait_http "http://localhost:8001/health" 40 2 || {
    err "carreras-service no responde"
    exit 1
  }
  green "carreras-service listo"
}

start_materias() {
  info "Iniciando materias-service"
  kill_port_if_busy 8004
  (cd "$SERVICES_DIR/materias-service" && ./.venv_local/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8004 > materias-local.log 2>&1 &) 
  wait_http "http://localhost:8004/health" 40 2 || {
    err "materias-service no responde"
    exit 1
  }
  green "materias-service listo"
}

start_temas() {
  info "Iniciando temas-service"
  kill_port_if_busy 8003
  (cd "$SERVICES_DIR/temas-service" && ./.venv_local/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > temas-local.log 2>&1 &) 
  wait_http "http://localhost:8003/health" 40 2 || {
    err "temas-service no responde"
    exit 1
  }
  green "temas-service listo"
}

start_posts() {
  info "Compilando/Iniciando posts-service"
  kill_port_if_busy 8002
  (cd "$SERVICES_DIR/posts-service" && mvn -q -DskipTests package)
  (
    cd "$SERVICES_DIR/posts-service"
    INTERNAL_SERVICE_SECRET=internal-secret-uptc-2026 \
    INTERNAL_SERVICE_ID=posts-service \
    JWT_SECRET=tu-secret-key-super-segura-para-desarrollo-12345 \
    MONGO_URI="mongodb://admin:password@localhost:27017/posts_service?authSource=admin" \
    REDIS_HOST=localhost \
    REDIS_PORT=6379 \
    EUREKA_DEFAULT_ZONE="http://localhost:8761/eureka/" \
    AUTH_SERVICE_NAME=auth-service \
    TOPIC_SERVICE_NAME=temas-service \
    java -jar target/posts-service-0.0.1-SNAPSHOT.jar > posts-service-jar.log 2>&1 &
  )
  wait_http "http://localhost:8002/health" 60 2 || {
    err "posts-service no responde"
    exit 1
  }
  green "posts-service listo"
}

run_seeds() {
  info "Ejecutando seeds"
  (cd "$SERVICES_DIR/auth-service" && npm run seed:users >/dev/null)
  (cd "$SERVICES_DIR/carreras-service" && PYTHONPATH=. ./.venv_local/Scripts/python.exe scripts/seed.py >/dev/null || true)
  (cd "$SERVICES_DIR/materias-service" && PYTHONPATH=. ./.venv_local/Scripts/python.exe scripts/seed.py >/dev/null || true)
  green "Seeds aplicadas (idempotentes)"
}

verify_eureka() {
  info "Verificando registro en Eureka"
  local apps
  apps="$(curl -fsS http://localhost:8761/eureka/apps || true)"
  for app in AUTH-SERVICE POSTS-SERVICE CARRERAS-SERVICE MATERIAS-SERVICE TEMAS-SERVICE; do
    if echo "$apps" | grep -q "$app"; then
      green "$app registrado"
    else
      warn "$app no aparece en Eureka"
    fi
  done
}

main() {
  require_cmd docker-compose
  require_cmd curl
  require_cmd npm
  require_cmd mvn

  start_infra
  start_auth
  start_carreras
  start_materias
  start_temas
  start_posts
  run_seeds
  verify_eureka

  info "Sistema listo"
  info "Auth: http://localhost:3000/health"
  info "Carreras: http://localhost:8001/health"
  info "Materias: http://localhost:8004/health"
  info "Temas: http://localhost:8003/health"
  info "Posts: http://localhost:8002/health"
  info "Eureka: http://localhost:8761"
}

main "$@"
