"""
Script para agregar autorización a la empresa de prueba
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import os
import sys
from datetime import datetime

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.empresa import Empresa, AutorizacionEmpresa, TipoAutorizacion

# URL de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://drtc_user:drtc_password_2024@postgres:5432/drtc_nomina"
)


async def add_authorization():
    """Agregar autorización a empresa"""
    print("=" * 60)
    print("AGREGANDO AUTORIZACIÓN A EMPRESA")
    print("=" * 60)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Buscar empresa
            result = await session.execute(
                select(Empresa).where(Empresa.ruc == "20123456789")
            )
            empresa = result.scalar_one_or_none()
            
            if not empresa:
                print("\n✗ Empresa no encontrada")
                return
            
            print(f"\n✓ Empresa encontrada: {empresa.razon_social}")
            
            # Buscar o crear tipo de autorización
            tipo_result = await session.execute(
                select(TipoAutorizacion).where(TipoAutorizacion.codigo == "TURISMO")
            )
            tipo = tipo_result.scalar_one_or_none()
            
            if not tipo:
                tipo = TipoAutorizacion(
                    codigo="TURISMO",
                    nombre="Servicio de Transporte Turístico",
                    descripcion="Transporte de turistas"
                )
                session.add(tipo)
                await session.flush()
                print(f"✓ Tipo de autorización creado: {tipo.nombre}")
            else:
                print(f"✓ Tipo de autorización encontrado: {tipo.nombre}")
            
            # Verificar si ya tiene autorización
            auth_result = await session.execute(
                select(AutorizacionEmpresa).where(
                    AutorizacionEmpresa.empresa_id == empresa.id,
                    AutorizacionEmpresa.tipo_autorizacion_id == tipo.id
                )
            )
            existing_auth = auth_result.scalar_one_or_none()
            
            if existing_auth:
                print("\n⚠ La empresa ya tiene esta autorización")
                print(f"  Número: {existing_auth.numero_resolucion}")
                print(f"  Vigente: {existing_auth.vigente}")
            else:
                # Crear autorización
                autorizacion = AutorizacionEmpresa(
                    empresa_id=empresa.id,
                    tipo_autorizacion_id=tipo.id,
                    numero_resolucion="RD-001-2024",
                    fecha_emision=datetime(2024, 1, 1).date(),
                    fecha_vencimiento=datetime(2029, 1, 1).date(),
                    vigente=True
                )
                session.add(autorizacion)
                await session.commit()
                print(f"\n✓ Autorización agregada a {empresa.razon_social}")
                print(f"  Número: {autorizacion.numero_resolucion}")
                print(f"  Vigencia: {autorizacion.fecha_emision} - {autorizacion.fecha_vencimiento}")
            
            print("\n" + "=" * 60)
            print("✓ PROCESO COMPLETADO")
            print("=" * 60)
            print("\nAhora puedes crear conductores para esta empresa.")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_authorization())
