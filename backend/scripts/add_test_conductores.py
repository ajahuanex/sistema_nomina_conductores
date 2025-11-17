"""
Script para agregar conductores de prueba
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
import sys
from datetime import datetime, timedelta

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Conductor, Empresa, EstadoConductor

# URL de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://drtc_user:drtc_password_2024@localhost:5434/drtc_nomina"
)


async def add_test_conductores():
    """Agregar conductores de prueba"""
    print("=" * 60)
    print("AGREGANDO CONDUCTORES DE PRUEBA")
    print("=" * 60)
    
    # Crear engine y session
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Primero necesitamos una empresa
            result = await session.execute(select(Empresa).limit(1))
            empresa = result.scalar_one_or_none()
            
            if not empresa:
                print("\n⚠ No hay empresas registradas. Creando empresa de prueba...")
                from app.models.empresa import AutorizacionEmpresa, TipoAutorizacion
                from sqlalchemy import select as sql_select
                
                # Buscar tipo de autorización
                tipo_result = await session.execute(
                    sql_select(TipoAutorizacion).where(TipoAutorizacion.codigo == "TURISMO")
                )
                tipo_autorizacion = tipo_result.scalar_one_or_none()
                
                if not tipo_autorizacion:
                    # Crear tipo de autorización si no existe
                    tipo_autorizacion = TipoAutorizacion(
                        codigo="TURISMO",
                        nombre="Servicio de Transporte Turístico",
                        descripcion="Transporte de turistas"
                    )
                    session.add(tipo_autorizacion)
                    await session.flush()
                
                empresa = Empresa(
                    ruc="20123456789",
                    razon_social="Transportes El Rápido S.A.C.",
                    direccion="Av. El Sol 123, Puno",
                    telefono="051-123456",
                    email="contacto@elrapido.com",
                    activo=True
                )
                session.add(empresa)
                await session.flush()
                
                # Agregar autorización a la empresa
                autorizacion = AutorizacionEmpresa(
                    empresa_id=empresa.id,
                    tipo_autorizacion_id=tipo_autorizacion.id,
                    numero_resolucion="RD-001-2024",
                    fecha_emision=datetime(2024, 1, 1).date(),
                    fecha_vencimiento=datetime(2029, 1, 1).date(),
                    vigente=True
                )
                session.add(autorizacion)
                await session.flush()
                
                print(f"  ✓ Empresa creada: {empresa.razon_social}")
                print(f"  ✓ Autorización agregada: {tipo_autorizacion.nombre}")
            
            # Conductores de prueba
            conductores_prueba = [
                {
                    "dni": "12345678",
                    "nombres": "Juan Carlos",
                    "apellidos": "Mamani Quispe",
                    "fecha_nacimiento": datetime(1985, 5, 15).date(),
                    "direccion": "Jr. Lima 456, Puno",
                    "telefono": "951234567",
                    "email": "juan.mamani@email.com",
                    "licencia_numero": "Q12345678",
                    "licencia_categoria": "A-IIIb",
                    "licencia_emision": datetime(2020, 1, 15).date(),
                    "licencia_vencimiento": datetime(2027, 1, 15).date(),
                    "certificado_medico_numero": "CM-2024-001",
                    "certificado_medico_vencimiento": datetime(2025, 1, 10).date(),
                    "empresa_id": empresa.id,
                    "estado": EstadoConductor.HABILITADO
                },
                {
                    "dni": "23456789",
                    "nombres": "María Elena",
                    "apellidos": "Condori Flores",
                    "fecha_nacimiento": datetime(1990, 8, 20).date(),
                    "direccion": "Av. Circunvalación 789, Puno",
                    "telefono": "962345678",
                    "email": "maria.condori@email.com",
                    "licencia_numero": "Q23456789",
                    "licencia_categoria": "A-IIIb",
                    "licencia_emision": datetime(2021, 3, 10).date(),
                    "licencia_vencimiento": datetime(2026, 3, 10).date(),
                    "certificado_medico_numero": "CM-2024-002",
                    "certificado_medico_vencimiento": datetime(2025, 2, 15).date(),
                    "empresa_id": empresa.id,
                    "estado": EstadoConductor.PENDIENTE
                },
                {
                    "dni": "34567890",
                    "nombres": "Pedro Luis",
                    "apellidos": "Huanca Apaza",
                    "fecha_nacimiento": datetime(1988, 12, 5).date(),
                    "direccion": "Jr. Arequipa 321, Puno",
                    "telefono": "973456789",
                    "email": "pedro.huanca@email.com",
                    "licencia_numero": "Q34567890",
                    "licencia_categoria": "A-IIIb",
                    "licencia_emision": datetime(2019, 6, 20).date(),
                    "licencia_vencimiento": datetime(2026, 6, 20).date(),
                    "certificado_medico_numero": "CM-2024-003",
                    "certificado_medico_vencimiento": datetime(2025, 3, 20).date(),
                    "empresa_id": empresa.id,
                    "estado": EstadoConductor.HABILITADO
                },
                {
                    "dni": "45678901",
                    "nombres": "Ana Rosa",
                    "apellidos": "Pari Ccama",
                    "fecha_nacimiento": datetime(1992, 3, 18).date(),
                    "direccion": "Av. La Torre 654, Puno",
                    "telefono": "984567890",
                    "email": "ana.pari@email.com",
                    "licencia_numero": "Q45678901",
                    "licencia_categoria": "A-IIIb",
                    "licencia_emision": datetime(2022, 9, 5).date(),
                    "licencia_vencimiento": datetime(2027, 9, 5).date(),
                    "certificado_medico_numero": "CM-2024-004",
                    "certificado_medico_vencimiento": datetime(2025, 4, 10).date(),
                    "empresa_id": empresa.id,
                    "estado": EstadoConductor.OBSERVADO
                },
                {
                    "dni": "56789012",
                    "nombres": "Roberto Carlos",
                    "apellidos": "Choque Nina",
                    "fecha_nacimiento": datetime(1987, 7, 25).date(),
                    "direccion": "Jr. Puno 987, Puno",
                    "telefono": "995678901",
                    "email": "roberto.choque@email.com",
                    "licencia_numero": "Q56789012",
                    "licencia_categoria": "A-IIIb",
                    "licencia_emision": datetime(2020, 11, 15).date(),
                    "licencia_vencimiento": datetime(2027, 11, 15).date(),
                    "certificado_medico_numero": "CM-2024-005",
                    "certificado_medico_vencimiento": datetime(2025, 5, 5).date(),
                    "empresa_id": empresa.id,
                    "estado": EstadoConductor.HABILITADO
                }
            ]
            
            print("\nCreando conductores de prueba...")
            
            for conductor_data in conductores_prueba:
                # Verificar si el conductor ya existe
                result = await session.execute(
                    select(Conductor).where(Conductor.dni == conductor_data["dni"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"  ⚠ Conductor ya existe: {conductor_data['dni']} - {conductor_data['nombres']} {conductor_data['apellidos']}")
                else:
                    conductor = Conductor(**conductor_data)
                    session.add(conductor)
                    print(f"  ✓ Conductor creado: {conductor_data['dni']} - {conductor_data['nombres']} {conductor_data['apellidos']} ({conductor_data['estado'].value})")
            
            await session.commit()
            
            print("\n" + "=" * 60)
            print("✓ CONDUCTORES DE PRUEBA CREADOS")
            print("=" * 60)
            print("\nPuedes ver los conductores en:")
            print("  http://localhost:4321/conductores")
            print("\nO probar los endpoints en:")
            print("  http://localhost:8002/api/docs")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_test_conductores())
