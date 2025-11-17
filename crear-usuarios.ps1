# Script para crear usuarios de prueba
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CREANDO USUARIOS DE PRUEBA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar que Docker esté corriendo
Write-Host "`nVerificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker no está corriendo" -ForegroundColor Red
    Write-Host "Por favor inicia Docker Desktop y vuelve a intentar" -ForegroundColor Yellow
    exit 1
}

# Verificar que el contenedor de PostgreSQL esté corriendo
Write-Host "Verificando PostgreSQL..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=postgres" --format "{{.Names}}"
if (-not $postgresRunning) {
    Write-Host "PostgreSQL no está corriendo. Iniciando contenedores..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Esperando 15 segundos para que PostgreSQL inicie..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
}

# Ejecutar script de creación de usuarios
Write-Host "`nCreando usuarios de prueba..." -ForegroundColor Yellow
cd backend
python scripts/add_test_users.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "USUARIOS CREADOS EXITOSAMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nPuedes iniciar sesión con:" -ForegroundColor Cyan
    Write-Host "  Director: director@drtc.gob.pe / Director123!" -ForegroundColor White
    Write-Host "  Subdirector: subdirector@drtc.gob.pe / Subdirector123!" -ForegroundColor White
    Write-Host "  Operario: operario@drtc.gob.pe / Operario123!" -ForegroundColor White
} else {
    Write-Host "`nERROR al crear usuarios" -ForegroundColor Red
    Write-Host "Revisa los logs arriba para más detalles" -ForegroundColor Yellow
}

cd ..
