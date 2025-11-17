"""
Script para poblar datos base del sistema
"""
import asyncio
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import os
import sys

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import (
    Usuario, RolUsuario,
    TipoAutorizacion,
    TipoInfraccion, GravedadInfraccion,
    ConceptoTUPA
)
from app.core.database import Base

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# URL de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://drtc_user:change_this_secure_password_in_production@localhost:5432/drtc_nomina"
)


async def create_usuarios_sistema(session: AsyncSession):
    """Crear usuarios del sistema para pruebas"""
    print("Creando usuarios del sistema...")
    
    usuarios = [
        {
            "email": "admin@drtc.gob.pe",
            "password": "Admin123!",
            "nombres": "Administrador",
            "apellidos": "Sistema",
            "rol": RolUsuario.SUPERUSUARIO,
            "dni": "00000001"
        },
        {
            "email": "director@drtc.gob.pe",
            "password": "Director123!",
            "nombres": "Juan Carlos",
            "apellidos": "Pérez Mamani",
            "rol": RolUsuario.DIRECTOR,
            "dni": "12345678"
        },
        {
            "email": "subdirector@drtc.gob.pe",
            "password": "Subdirector123!",
            "nombres": "María Elena",
            "apellidos": "Quispe Condori",
            "rol": RolUsuario.SUBDIRECTOR,
            "dni": "23456789"
        },
        {
            "email": "operario@drtc.gob.pe",
            "password": "Operario123!",
            "nombres": "Pedro Luis",
            "apellidos": "Huanca Flores",
            "rol": RolUsuario.OPERARIO,
            "dni": "34567890"
        }
    ]
    
    for user_data in usuarios:
        password = user_data.pop("password")
        usuario = Usuario(
            **user_data,
            password_hash=pwd_context.hash(password),
            activo=True
        )
        session.add(usuario)
        print(f"  ✓ {usuario.rol.value}: {usuario.email}")
    
    await session.commit()
    print(f"✓ {len(usuarios)} usuarios del sistema creados")


async def create_tipos_autorizacion(session: AsyncSession):
    """Crear tipos de autorización predefinidos"""
    print("\nCreando tipos de autorización...")
    
    tipos = [
        {
            "codigo": "MERCANCIAS",
            "nombre": "Transporte de Mercancías",
            "descripcion": "Autorización para transporte de carga y mercancías en general",
            "requisitos_especiales": {
                "licencia_minima": ["A-IIIb", "A-IIIc"],
                "certificaciones": ["Certificado de operador de carga"]
            }
        },
        {
            "codigo": "TURISMO",
            "nombre": "Transporte de Turismo",
            "descripcion": "Autorización para transporte turístico de pasajeros",
            "requisitos_especiales": {
                "licencia_minima": ["A-IIb", "A-IIIa", "A-IIIb", "A-IIIc"],
                "certificaciones": ["Curso de turismo", "Primeros auxilios"]
            }
        },
        {
            "codigo": "TRABAJADORES",
            "nombre": "Transporte de Trabajadores",
            "descripcion": "Autorización para transporte de personal de empresas",
            "requisitos_especiales": {
                "licencia_minima": ["A-IIb", "A-IIIa", "A-IIIb", "A-IIIc"],
                "certificaciones": ["Curso de seguridad vial"]
            }
        },
        {
            "codigo": "ESPECIALES",
            "nombre": "Servicios Especiales",
            "descripcion": "Autorización para servicios especiales de transporte",
            "requisitos_especiales": {
                "licencia_minima": ["A-IIIa", "A-IIIb", "A-IIIc"],
                "certificaciones": ["Certificación especial según servicio"]
            }
        },
        {
            "codigo": "ESTUDIANTES",
            "nombre": "Transporte de Estudiantes",
            "descripcion": "Autorización para transporte escolar",
            "requisitos_especiales": {
                "licencia_minima": ["A-IIb", "A-IIIa", "A-IIIb", "A-IIIc"],
                "certificaciones": ["Curso de transporte escolar", "Certificado de antecedentes"]
            }
        },
        {
            "codigo": "RESIDUOS_PELIGROSOS",
            "nombre": "Transporte de Residuos Peligrosos",
            "descripcion": "Autorización para transporte de materiales peligrosos",
            "requisitos_especiales": {
                "licencia_minima": ["A-IIIb", "A-IIIc"],
                "certificaciones": [
                    "Certificación HAZMAT",
                    "Curso de manejo de materiales peligrosos",
                    "Certificado de salud especial"
                ]
            }
        }
    ]
    
    for tipo_data in tipos:
        tipo = TipoAutorizacion(**tipo_data)
        session.add(tipo)
        print(f"  ✓ {tipo.nombre}")
    
    await session.commit()
    print(f"✓ {len(tipos)} tipos de autorización creados")


async def create_tipos_infraccion(session: AsyncSession):
    """Crear tipos de infracciones según normativa MTC"""
    print("\nCreando tipos de infracciones...")
    
    infracciones = [
        # Infracciones LEVES
        {
            "codigo": "L001",
            "descripcion": "No portar documentos del vehículo",
            "gravedad": GravedadInfraccion.LEVE,
            "puntos": 5,
            "activo": "true"
        },
        {
            "codigo": "L002",
            "descripcion": "Exceso de velocidad menor a 10 km/h",
            "gravedad": GravedadInfraccion.LEVE,
            "puntos": 5,
            "activo": "true"
        },
        {
            "codigo": "L003",
            "descripcion": "No usar cinturón de seguridad",
            "gravedad": GravedadInfraccion.LEVE,
            "puntos": 10,
            "activo": "true"
        },
        {
            "codigo": "L004",
            "descripcion": "Estacionar en lugar prohibido",
            "gravedad": GravedadInfraccion.LEVE,
            "puntos": 5,
            "activo": "true"
        },
        
        # Infracciones GRAVES
        {
            "codigo": "G001",
            "descripcion": "Exceso de velocidad entre 10 y 50 km/h",
            "gravedad": GravedadInfraccion.GRAVE,
            "puntos": 30,
            "activo": "true"
        },
        {
            "codigo": "G002",
            "descripcion": "No respetar señal de alto o semáforo en rojo",
            "gravedad": GravedadInfraccion.GRAVE,
            "puntos": 40,
            "activo": "true"
        },
        {
            "codigo": "G003",
            "descripcion": "Conducir sin licencia vigente",
            "gravedad": GravedadInfraccion.GRAVE,
            "puntos": 50,
            "activo": "true"
        },
        {
            "codigo": "G004",
            "descripcion": "Adelantar en curva o zona prohibida",
            "gravedad": GravedadInfraccion.GRAVE,
            "puntos": 40,
            "activo": "true"
        },
        {
            "codigo": "G005",
            "descripcion": "Transportar pasajeros sin autorización",
            "gravedad": GravedadInfraccion.GRAVE,
            "puntos": 50,
            "activo": "true"
        },
        
        # Infracciones MUY GRAVES
        {
            "codigo": "MG001",
            "descripcion": "Conducir en estado de ebriedad",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 100,
            "activo": "true"
        },
        {
            "codigo": "MG002",
            "descripcion": "Conducir bajo efectos de drogas",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 100,
            "activo": "true"
        },
        {
            "codigo": "MG003",
            "descripcion": "Exceso de velocidad mayor a 50 km/h",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 80,
            "activo": "true"
        },
        {
            "codigo": "MG004",
            "descripcion": "Causar accidente con víctimas",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 100,
            "activo": "true"
        },
        {
            "codigo": "MG005",
            "descripcion": "Fuga del lugar del accidente",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 100,
            "activo": "true"
        },
        {
            "codigo": "MG006",
            "descripcion": "Negarse a prueba de alcoholemia",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 100,
            "activo": "true"
        },
        {
            "codigo": "MG007",
            "descripcion": "Transportar carga peligrosa sin autorización",
            "gravedad": GravedadInfraccion.MUY_GRAVE,
            "puntos": 100,
            "activo": "true"
        }
    ]
    
    for infraccion_data in infracciones:
        infraccion = TipoInfraccion(**infraccion_data)
        session.add(infraccion)
        print(f"  ✓ [{infraccion.gravedad.value.upper()}] {infraccion.descripcion}")
    
    await session.commit()
    print(f"✓ {len(infracciones)} tipos de infracciones creados")


async def create_conceptos_tupa(session: AsyncSession):
    """Crear conceptos TUPA con montos vigentes"""
    print("\nCreando conceptos TUPA...")
    
    conceptos = [
        {
            "codigo": "TUPA-001",
            "descripcion": "Habilitación de conductor - Primera vez",
            "monto": 150.00,
            "vigencia_desde": date.today(),
            "vigencia_hasta": date(2025, 12, 31),
            "activo": "true"
        },
        {
            "codigo": "TUPA-002",
            "descripcion": "Renovación de habilitación de conductor",
            "monto": 100.00,
            "vigencia_desde": date.today(),
            "vigencia_hasta": date(2025, 12, 31),
            "activo": "true"
        },
        {
            "codigo": "TUPA-003",
            "descripcion": "Duplicado de certificado de habilitación",
            "monto": 50.00,
            "vigencia_desde": date.today(),
            "vigencia_hasta": date(2025, 12, 31),
            "activo": "true"
        },
        {
            "codigo": "TUPA-004",
            "descripcion": "Modificación de datos de conductor",
            "monto": 30.00,
            "vigencia_desde": date.today(),
            "vigencia_hasta": date(2025, 12, 31),
            "activo": "true"
        }
    ]
    
    for concepto_data in conceptos:
        concepto = ConceptoTUPA(**concepto_data)
        session.add(concepto)
        print(f"  ✓ {concepto.descripcion} - S/ {concepto.monto}")
    
    await session.commit()
    print(f"✓ {len(conceptos)} conceptos TUPA creados")


async def seed_database():
    """Función principal para poblar la base de datos"""
    print("=" * 60)
    print("POBLANDO BASE DE DATOS CON DATOS INICIALES")
    print("=" * 60)
    
    # Crear engine y session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Crear datos base
            await create_usuarios_sistema(session)
            await create_tipos_autorizacion(session)
            await create_tipos_infraccion(session)
            await create_conceptos_tupa(session)
            
            print("\n" + "=" * 60)
            print("✓ BASE DE DATOS POBLADA EXITOSAMENTE")
            print("=" * 60)
            print("\nCredenciales de usuarios de prueba:")
            print("\n  SUPERUSUARIO:")
            print("    Email: admin@drtc.gob.pe")
            print("    Password: Admin123!")
            print("\n  DIRECTOR:")
            print("    Email: director@drtc.gob.pe")
            print("    Password: Director123!")
            print("\n  SUBDIRECTOR:")
            print("    Email: subdirector@drtc.gob.pe")
            print("    Password: Subdirector123!")
            print("\n  OPERARIO:")
            print("    Email: operario@drtc.gob.pe")
            print("    Password: Operario123!")
            print("\n⚠ IMPORTANTE: Cambie las contraseñas después del primer login")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error al poblar base de datos: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
