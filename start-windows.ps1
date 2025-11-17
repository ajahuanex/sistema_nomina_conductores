# Script de inicio para Windows PowerShell
# Sistema de Nómina de Conductores DRTC Puno

Write-Host "🚀 Iniciando Sistema de Nómina de Conductores DRTC Puno..." -ForegroundColor Green

# Verificar que Docker esté corriendo
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker no está corriendo. Por favor inicia Docker Desktop primero." -ForegroundColor Red
    Write-Host "   Presiona Enter después de iniciar Docker Desktop..." -ForegroundColor Yellow
    Read-Host
}

# Verificar que existe el archivo .env
if (-not (Test-Path .env)) {
    Write-Host "📝 Creando archivo .env desde .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Por favor edita el archivo .env con tus configuraciones antes de continuar." -ForegroundColor Yellow
    Write-Host "   Presiona Enter cuando hayas terminado..." -ForegroundColor Yellow
    Read-Host
}

# Construir imágenes
Write-Host "🔨 Construyendo imágenes Docker..." -ForegroundColor Cyan
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al construir las imágenes" -ForegroundColor Red
    exit 1
}

# Iniciar servicios en modo desarrollo
Write-Host "🐳 Iniciando servicios en modo desarrollo..." -ForegroundColor Cyan
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar los servicios" -ForegroundColor Red
    exit 1
}

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar estado de los servicios
Write-Host "`n📊 Estado de los servicios:" -ForegroundColor Cyan
docker-compose ps

# Ejecutar migraciones
Write-Host "`n📊 Ejecutando migraciones de base de datos..." -ForegroundColor Cyan
docker exec drtc-backend alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Las migraciones fallaron. Puede que necesites crearlas primero." -ForegroundColor Yellow
}

# Verificar setup
Write-Host "`n🔍 Verificando configuración..." -ForegroundColor Cyan
docker exec drtc-backend python scripts/verify_setup.py

Write-Host "`n✅ Sistema iniciado correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Accesos:" -ForegroundColor Cyan
Write-Host "   - Frontend: http://localhost:4321" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8002" -ForegroundColor White
Write-Host "   - Documentación API: http://localhost:8002/docs" -ForegroundColor White
Write-Host "   - Nginx Proxy: http://localhost:8082" -ForegroundColor White
Write-Host "   - PgAdmin: http://localhost:5051 (admin@drtc.local / admin)" -ForegroundColor White
Write-Host "   - Redis Commander: http://localhost:8083" -ForegroundColor White
Write-Host ""
Write-Host "📝 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   - Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   - Ver logs backend: docker-compose logs -f backend" -ForegroundColor White
Write-Host "   - Detener: docker-compose down" -ForegroundColor White
Write-Host "   - Reiniciar: docker-compose restart" -ForegroundColor White
Write-Host ""
