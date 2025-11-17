"""
Script para agregar usuarios de prueba sin borrar datos existentes
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext
import os
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Usuario, RolUsuario

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# URL de base de datos - usar la del .env o la de producción
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://drtc_user:drtc_password_2024@localhost:5434/drtc_nomina"
)


async def add_test_users():
    """Agregar usuarios de prueba"""
    print("=" * 60)
    print("AGREGANDO USUARIOS DE PRUEBA")
    print("=" * 60)
    
    # Crear engine y session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            usuarios_prueba = [
                {
                    "email": "director@drtc.gob.pe",
                    "password": "Director123!",
                    "nombres": "Juan Carlos",
                    "apellidos": "Pérez Mamani",
                    "rol": RolUsuario.DIRECTOR
                },
                {
                    "email": "subdirector@drtc.gob.pe",
                    "password": "Subdirector123!",
                    "nombres": "María Elena",
                    "apellidos": "Quispe Condori",
                    "rol": RolUsuario.SUBDIRECTOR
                },
                {
                    "email": "operario@drtc.gob.pe",
                    "password": "Operario123!",
                    "nombres": "Pedro Luis",
                    "apellidos": "Huanca Flores",
                    "rol": RolUsuario.OPERARIO
                }
            ]
            
            print("\nVerificando y creando usuarios...")
            
            for user_data in usuarios_prueba:
                # Verificar si el usuario ya existe
                result = await session.execute(
                    select(Usuario).where(Usuario.email == user_data["email"])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"  ⚠ Usuario ya existe: {user_data['email']}")
                    # Actualizar contraseña
                    existing_user.password_hash = pwd_context.hash(user_data["password"])
                    print(f"    ✓ Contraseña actualizada")
                else:
                    # Crear nuevo usuario
                    password = user_data.pop("password")
                    usuario = Usuario(
                        **user_data,
                        password_hash=pwd_context.hash(password),
                        activo=True
                    )
                    session.add(usuario)
                    print(f"  ✓ Usuario creado: {user_data['email']} ({user_data['rol'].value})")
            
            await session.commit()
            
            print("\n" + "=" * 60)
            print("✓ USUARIOS DE PRUEBA CONFIGURADOS")
            print("=" * 60)
            print("\nCredenciales de usuarios de prueba:")
            print("\n  DIRECTOR:")
            print("    Email: director@drtc.gob.pe")
            print("    Password: Director123!")
            print("\n  SUBDIRECTOR:")
            print("    Email: subdirector@drtc.gob.pe")
            print("    Password: Subdirector123!")
            print("\n  OPERARIO:")
            print("    Email: operario@drtc.gob.pe")
            print("    Password: Operario123!")
            print("\n⚠ IMPORTANTE: Estos son usuarios de prueba")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_test_users())
