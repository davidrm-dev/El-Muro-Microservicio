Param()

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Infra = Join-Path $Root "infrastructure"
$Services = Join-Path $Root "services"

function Info($m) { Write-Host "[INFO] $m" }
function Ok($m) { Write-Host "[OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }

function Wait-Http($url, $retries = 40, $sleep = 2) {
  for ($i = 0; $i -lt $retries; $i++) {
    try {
      Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 5 | Out-Null
      return $true
    } catch {
      Start-Sleep -Seconds $sleep
    }
  }
  return $false
}

function Stop-Port($port) {
  $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  foreach ($c in $conns) {
    try {
      Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
      Warn "Puerto $port liberado (PID $($c.OwningProcess))"
    } catch {}
  }
}

Info "Levantando infraestructura docker"
docker-compose -f (Join-Path $Infra "docker-compose.yml") up -d --remove-orphans | Out-Null
if (-not (Wait-Http "http://localhost:8761/eureka/apps" 60 2)) {
  throw "Eureka no estuvo disponible"
}
Ok "Infraestructura lista"

Stop-Port 3000
Info "Iniciando auth-service"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev > auth-service.log 2>&1" -WorkingDirectory (Join-Path $Services "auth-service") -WindowStyle Hidden | Out-Null
if (-not (Wait-Http "http://localhost:3000/health" 40 2)) { throw "auth-service no responde" }
Ok "auth-service listo"

Stop-Port 8001
Info "Iniciando carreras-service"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c .venv_local\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > carreras-local.log 2>&1" -WorkingDirectory (Join-Path $Services "carreras-service") -WindowStyle Hidden | Out-Null
if (-not (Wait-Http "http://localhost:8001/health" 40 2)) { throw "carreras-service no responde" }
Ok "carreras-service listo"

Stop-Port 8004
Info "Iniciando materias-service"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c .venv_local\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8004 > materias-local.log 2>&1" -WorkingDirectory (Join-Path $Services "materias-service") -WindowStyle Hidden | Out-Null
if (-not (Wait-Http "http://localhost:8004/health" 40 2)) { throw "materias-service no responde" }
Ok "materias-service listo"

Stop-Port 8003
Info "Iniciando temas-service"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c .venv_local\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8003 > temas-local.log 2>&1" -WorkingDirectory (Join-Path $Services "temas-service") -WindowStyle Hidden | Out-Null
if (-not (Wait-Http "http://localhost:8003/health" 40 2)) { throw "temas-service no responde" }
Ok "temas-service listo"

Stop-Port 8002
Info "Compilando posts-service"
Push-Location (Join-Path $Services "posts-service")
mvn -q -DskipTests package | Out-Null
Pop-Location

Info "Iniciando posts-service"
$postsCmd = @(
  'set INTERNAL_SERVICE_SECRET=internal-secret-uptc-2026',
  'set INTERNAL_SERVICE_ID=posts-service',
  'set JWT_SECRET=tu-secret-key-super-segura-para-desarrollo-12345',
  'set MONGO_URI=mongodb://admin:password@localhost:27017/posts_service?authSource=admin',
  'set REDIS_HOST=localhost',
  'set REDIS_PORT=6379',
  'set EUREKA_DEFAULT_ZONE=http://localhost:8761/eureka/',
  'set AUTH_SERVICE_NAME=auth-service',
  'set TOPIC_SERVICE_NAME=temas-service',
  'java -jar target/posts-service-0.0.1-SNAPSHOT.jar > posts-service-jar.log 2>&1'
) -join ' && '
Start-Process -FilePath "cmd.exe" -ArgumentList "/c $postsCmd" -WorkingDirectory (Join-Path $Services "posts-service") -WindowStyle Hidden | Out-Null
if (-not (Wait-Http "http://localhost:8002/health" 60 2)) { throw "posts-service no responde" }
Ok "posts-service listo"

Info "Ejecutando seeds"
Push-Location (Join-Path $Services "auth-service")
npm run seed:users | Out-Null
Pop-Location
Push-Location (Join-Path $Services "carreras-service")
cmd /c "set PYTHONPATH=. && .venv_local\Scripts\python.exe scripts\seed.py" | Out-Null
Pop-Location
Push-Location (Join-Path $Services "materias-service")
cmd /c "set PYTHONPATH=. && .venv_local\Scripts\python.exe scripts\seed.py" | Out-Null
Pop-Location
Ok "Seeds aplicadas"

Info "Verificando Eureka"
$apps = Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8761/eureka/apps"
foreach ($svc in @("AUTH-SERVICE", "POSTS-SERVICE", "CARRERAS-SERVICE", "MATERIAS-SERVICE", "TEMAS-SERVICE")) {
  if ($apps.Content -match $svc) { Ok "$svc registrado" } else { Warn "$svc no aparece en Eureka" }
}

Info "Sistema listo"
Info "Auth: http://localhost:3000/health"
Info "Carreras: http://localhost:8001/health"
Info "Materias: http://localhost:8004/health"
Info "Temas: http://localhost:8003/health"
Info "Posts: http://localhost:8002/health"
Info "Eureka: http://localhost:8761"
