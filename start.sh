#!/bin/bash

# Compatibilidad: delega al script nuevo unificado
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/start-local.sh" "$@"
