@echo off
REM Script para ejecutar migraciones de Alembic en Windows

echo Ejecutando migraciones de base de datos...

REM Verificar que estamos en el directorio correcto
if not exist "alembic.ini" (
    echo Error: alembic.ini no encontrado. Ejecuta este script desde el directorio backend/
    exit /b 1
)

REM Ejecutar migraciones
alembic upgrade head

if %ERRORLEVEL% EQU 0 (
    echo Migraciones completadas exitosamente
) else (
    echo Error al ejecutar migraciones
    exit /b 1
)
