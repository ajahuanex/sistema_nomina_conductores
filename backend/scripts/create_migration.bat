@echo off
REM Script para crear una nueva migración de Alembic en Windows

if "%~1"=="" (
    echo Error: Debes proporcionar un mensaje para la migracion
    echo Uso: scripts\create_migration.bat "mensaje descriptivo"
    exit /b 1
)

echo Creando nueva migracion: %~1

REM Verificar que estamos en el directorio correcto
if not exist "alembic.ini" (
    echo Error: alembic.ini no encontrado. Ejecuta este script desde el directorio backend/
    exit /b 1
)

REM Crear migración con autogenerate
alembic revision --autogenerate -m "%~1"

if %ERRORLEVEL% EQU 0 (
    echo Migracion creada exitosamente
    echo Revisa el archivo generado en alembic/versions/
    echo Para aplicar la migracion, ejecuta: scripts\run_migrations.bat
) else (
    echo Error al crear migracion
    exit /b 1
)
