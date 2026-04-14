#!/bin/bash

echo "Comandos rapidos - El Muro"
echo

echo "1) Levantar solo infraestructura (Docker)"
echo "   cd infrastructure && docker-compose up -d --remove-orphans"
echo

echo "2) Arranque unificado de todo en local"
echo "   ./start-local.sh"
echo "   # En Windows: .\\start-local.ps1"
echo

echo "3) Verificar health de microservicios"
echo "   curl -s http://localhost:3000/health"
echo "   curl -s http://localhost:8001/health"
echo "   curl -s http://localhost:8004/health"
echo "   curl -s http://localhost:8003/health"
echo "   curl -s http://localhost:8002/health"
echo

echo "4) Ver registro en Eureka"
echo "   curl -s http://localhost:8761/eureka/apps"
echo "   curl -s http://localhost:8761/eureka/apps/AUTH-SERVICE"
echo "   curl -s http://localhost:8761/eureka/apps/POSTS-SERVICE"
echo "   curl -s http://localhost:8761/eureka/apps/CARRERAS-SERVICE"
echo "   curl -s http://localhost:8761/eureka/apps/MATERIAS-SERVICE"
echo "   curl -s http://localhost:8761/eureka/apps/TEMAS-SERVICE"
echo

echo "5) Seeds"
echo "   cd services/auth-service && npm run seed:users"
echo "   cd services/carreras-service && PYTHONPATH=. ./.venv_local/Scripts/python.exe scripts/seed.py"
echo "   cd services/materias-service && PYTHONPATH=. ./.venv_local/Scripts/python.exe scripts/seed.py"
echo "   # posts-service siembra automaticamente al iniciar (si vacio)"
echo

echo "6) Logs"
echo "   docker-compose -f infrastructure/docker-compose.yml logs -f eureka-server"
echo "   tail -f services/auth-service/auth-service.log"
echo "   tail -f services/posts-service/posts-service-jar.log"
echo "   tail -f services/carreras-service/carreras-local.log"
echo "   tail -f services/materias-service/materias-local.log"
echo "   tail -f services/temas-service/temas-local.log"
