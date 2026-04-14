#!/usr/bin/env bash
set -euo pipefail

EUREKA_BASE_URL="${EUREKA_BASE_URL:-http://localhost:8761}"
AUTH_BASE_URL="${AUTH_BASE_URL:-http://localhost:3000}"
APP_NAME="${APP_NAME:-AUTH-SERVICE}"

red() { printf '\033[31m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }
blue() { printf '\033[34m%s\033[0m\n' "$1"; }

blue "[1/3] Validando health de auth-service en ${AUTH_BASE_URL}/health"
HEALTH_RESPONSE="$(curl -fsS "${AUTH_BASE_URL}/health")" || {
  red "Fallo: auth-service no responde en /health"
  exit 1
}

echo "Health response: ${HEALTH_RESPONSE}"

grep -q 'auth-service online' <<<"${HEALTH_RESPONSE}" || {
  red "Fallo: respuesta de /health inesperada"
  exit 1
}

green "OK: auth-service responde correctamente"

blue "[2/3] Validando disponibilidad de Eureka en ${EUREKA_BASE_URL}/eureka/apps"
EUREKA_APPS="$(curl -fsS "${EUREKA_BASE_URL}/eureka/apps")" || {
  red "Fallo: Eureka no responde en /eureka/apps"
  exit 1
}

green "OK: Eureka responde"

blue "[3/3] Validando registro de ${APP_NAME} en Eureka"
EUREKA_APP_ENTRY="$(curl -fsS "${EUREKA_BASE_URL}/eureka/apps/${APP_NAME}" || true)"

if [[ -z "${EUREKA_APP_ENTRY}" ]]; then
  red "Fallo: no se pudo consultar la app ${APP_NAME} en Eureka"
  exit 1
fi

grep -q "<name>${APP_NAME}</name>" <<<"${EUREKA_APP_ENTRY}" || {
  red "Fallo: ${APP_NAME} no aparece registrado en Eureka"
  echo "Sugerencia: intenta APP_NAME=auth-service o APP_NAME=AUTH-SERVICE"
  exit 1
}

grep -q '<status>UP</status>' <<<"${EUREKA_APP_ENTRY}" || {
  red "Fallo: ${APP_NAME} aparece pero no está en estado UP"
  exit 1
}

green "OK: ${APP_NAME} está registrado y en estado UP"

echo ""
green "Smoke test completado exitosamente"
