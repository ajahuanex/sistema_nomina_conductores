#!/bin/bash

# Script de inicio rápido para el proyecto

echo "🚀 Iniciando Sistema de Nómina de Conductores DRTC Puno..."

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "⚠️  Por favor edita el archivo .env con tus configuraciones antes de continuar."
    echo "   Presiona Enter cuando hayas terminado..."
    read
fi

# Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose build

# Iniciar servicios
echo "🐳 Iniciando servicios..."
docker-compose up -d

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 10

# Ejecutar migraciones
echo "📊 Ejecutando migraciones de base de datos..."
docker exec -it drtc-backend alembic upgrade head

# Crear usuario superusuario
echo "👤 Creando usuario superusuario..."
docker exec -it drtc-backend python -c "
from app.core.database import AsyncSessionLocal
from app.models.user import Usuario, RolUsuario
from passlib.context import CryptContext
import asyncio

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def create_superuser():
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe
        from sqlalchemy import select
        result = await session.execute(
            select(Usuario).where(Usuario.email == 'admin@drtc-puno.gob.pe')
        )
        if result.scalar_one_or_none():
            print('Superusuario ya existe')
            return
        
        usuario = Usuario(
            email='admin@drtc-puno.gob.pe',
            password_hash=pwd_context.hash('admin123'),
            nombres='Administrador',
            apellidos='Sistema',
            rol=RolUsuario.SUPERUSUARIO,
            activo=True
        )
        session.add(usuario)
        await session.commit()
        print('✅ Superusuario creado: admin@drtc-puno.gob.pe / admin123')

asyncio.run(create_superuser())
" 2>/dev/null || echo "⚠️  No se pudo crear el superusuario automáticamente"

echo ""
echo "✅ Sistema iniciado correctamente!"
echo ""
echo "📍 Accesos:"
echo "   - Frontend: http://localhost"
echo "   - Backend API: http://localhost/api"
echo "   - Documentación API: http://localhost/docs"
echo "   - PgAdmin: http://localhost:5050"
echo "   - Redis Commander: http://localhost:8081"
echo ""
echo "👤 Credenciales por defecto:"
echo "   Email: admin@drtc-puno.gob.pe"
echo "   Password: admin123"
echo ""
echo "📝 Para ver logs: docker-compose logs -f"
echo "🛑 Para detener: docker-compose down"
echo ""
