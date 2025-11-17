@echo off
REM Script de inicio para Windows CMD
REM Sistema de Nómina de Conductores DRTC Puno

echo.
echo ========================================
echo   Sistema de Nomina DRTC Puno
echo ========================================
echo.

echo [1/5] Verificando Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta corriendo
    echo Por favor inicia Docker Desktop primero
    pause
    exit /b 1
)
echo OK: Docker esta corriendo

echo.
echo [2/5] Verificando archivo .env...
if not exist .env (
    echo Creando .env desde .env.example...
    copy .env.example .env
    echo IMPORTANTE: Edita el archivo .env antes de continuar
    pause
)
echo OK: Archivo .env existe

echo.
echo [3/5] Construyendo imagenes Docker...
docker-compose build
if errorlevel 1 (
    echo ERROR: Fallo al construir imagenes
    pause
    exit /b 1
)
echo OK: Imagenes construidas

echo.
echo [4/5] Iniciando servicios...
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar servicios
    pause
    exit /b 1
)
echo OK: Servicios iniciados

echo.
echo [5/5] Esperando a PostgreSQL...
timeout /t 15 /nobreak >nul

echo.
echo Ejecutando migraciones...
docker exec drtc-backend alembic upgrade head

echo.
echo Verificando setup...
docker exec drtc-backend python scripts/verify_setup.py

echo.
echo ========================================
echo   Sistema iniciado correctamente!
echo ========================================
echo.
echo Accesos:
echo   - Frontend: http://localhost:4321
echo   - Backend API: http://localhost:8002
echo   - Docs API: http://localhost:8002/docs
echo   - Nginx: http://localhost:8082
echo   - PgAdmin: http://localhost:5051
echo   - Redis: http://localhost:8083
echo.
echo Comandos utiles:
echo   - Ver logs: docker-compose logs -f
echo   - Detener: docker-compose down
echo.
pause
