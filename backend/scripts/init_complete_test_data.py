#!/usr/bin/env python
"""
Script para inicializar datos de prueba completos del sistema
Incluye: usuarios, empresas, autorizaciones, conductores, habilitaciones y pagos
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import Usuario, RolUsuario
from app.models.empresa import Empresa, TipoAutorizacion, AutorizacionEmpresa
from app.models.conductor import Conductor, EstadoConductor
from app.models.habilitacion import Habilitacion, EstadoHabilitacion, ConceptoTUPA, Pago, EstadoPago


async def init_test_data():
    """Inicializa datos de prueba completos"""
    
    # Crear engine y sesión
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("🚀 Iniciando creación de datos de prueba...")
        
        # 1. Crear usuarios
        print("\n👥 Creando usuarios...")
        
        # Superusuario
        superuser = Usuario(
            email="admin@drtc.gob.pe",
            password_hash=hash_password("Admin123!"),
            nombres="Administrador",
            apellidos="Sistema",
            rol=RolUsuario.SUPERUSUARIO,
            activo=True
        )
        session.add(superuser)
        
        # Director
        director = Usuario(
            email="director@drtc.gob.pe",
            password_hash=hash_password("Director123!"),
            nombres="Juan Carlos",
            apellidos="Mamani Quispe",
            rol=RolUsuario.DIRECTOR,
            activo=True
        )
        session.add(director)
        
        # Operario
        operario = Usuario(
            email="operario@drtc.gob.pe",
            password_hash=hash_password("Operario123!"),
            nombres="María Elena",
            apellidos="Condori Apaza",
            rol=RolUsuario.OPERARIO,
            activo=True
        )
        session.add(operario)
        
        await session.flush()
        
        # 2. Crear tipos de autorización
        print("\n📋 Creando tipos de autorización...")
        
        tipos_auth = [
            {
                "codigo": "TURISMO",
                "nombre": "Transporte Turístico",
                "descripcion": "Autorización para transporte de turistas",
                "requisitos_especiales": {"licencia_minima": "A-IIb"}
            },
            {
                "codigo": "AUTOCOLECTIVO",
                "nombre": "Servicio de Autocolectivo",
                "descripcion": "Autorización para servicio de autocolectivo",
                "requisitos_especiales": {"licencia_minima": "A-IIb"}
            },
            {
                "codigo": "MERCANCIAS",
                "nombre": "Transporte de Mercancías",
                "descripcion": "Autorización para transporte de carga",
                "requisitos_especiales": {"licencia_minima": "A-IIIb"}
            },
            {
                "codigo": "TRABAJADORES",
                "nombre": "Transporte de Trabajadores",
                "descripcion": "Autorización para transporte de personal",
                "requisitos_especiales": {"licencia_minima": "A-IIb"}
            },
            {
                "codigo": "ESTUDIANTES",
                "nombre": "Transporte Escolar",
                "descripcion": "Autorización para transporte de estudiantes",
                "requisitos_especiales": {"licencia_minima": "A-IIb"}
            }
        ]
        
        tipos_auth_objs = []
        for tipo_data in tipos_auth:
            tipo = TipoAutorizacion(**tipo_data)
            session.add(tipo)
            tipos_auth_objs.append(tipo)
        
        await session.flush()
        
        # 3. Crear conceptos TUPA
        print("\n💰 Creando conceptos TUPA...")
        
        concepto_hab = ConceptoTUPA(
            codigo="HAB-CONDUCTOR",
            descripcion="Habilitación de Conductor",
            monto=Decimal("50.00"),
            vigencia_desde=date.today() - timedelta(days=365),
            vigencia_hasta=None,
            activo=True
        )
        session.add(concepto_hab)
        await session.flush()
        
        # 4. Crear empresas con gerentes
        print("\n🏢 Creando empresas...")
        
        # Empresa 1: Transportes Puno SAC (Turismo)
        gerente1 = Usuario(
            email="gerente.puno@transportes.com",
            password_hash=hash_password("Gerente123!"),
            nombres="Roberto",
            apellidos="Flores Mamani",
            rol=RolUsuario.GERENTE,
            activo=True
        )
        session.add(gerente1)
        await session.flush()
        
        empresa1 = Empresa(
            ruc="20123456789",
            razon_social="Transportes Puno SAC",
            direccion="Av. El Sol 123, Puno",
            telefono="051-351234",
            email="contacto@transportespuno.com",
            gerente_id=gerente1.id,
            activo=True
        )
        session.add(empresa1)
        await session.flush()
        
        # Actualizar empresa_id del gerente
        gerente1.empresa_id = empresa1.id
        
        # Autorización de turismo para empresa 1
        auth1 = AutorizacionEmpresa(
            empresa_id=empresa1.id,
            tipo_autorizacion_id=tipos_auth_objs[0].id,  # TURISMO
            numero_resolucion="RD-2024-001-DRTC-PUNO",
            fecha_emision=date(2024, 1, 15),
            fecha_vencimiento=date(2025, 12, 31),
            vigente=True
        )
        session.add(auth1)
        
        # Empresa 2: Transportes Juliaca EIRL (Autocolectivo)
        gerente2 = Usuario(
            email="gerente.juliaca@transportes.com",
            password_hash=hash_password("Gerente123!"),
            nombres="Carmen Rosa",
            apellidos="Quispe Huanca",
            rol=RolUsuario.GERENTE,
            activo=True
        )
        session.add(gerente2)
        await session.flush()
        
        empresa2 = Empresa(
            ruc="20987654321",
            razon_social="Transportes Juliaca EIRL",
            direccion="Jr. San Román 456, Juliaca",
            telefono="051-321456",
            email="contacto@transportesjuliaca.com",
            gerente_id=gerente2.id,
            activo=True
        )
        session.add(empresa2)
        await session.flush()
        
        gerente2.empresa_id = empresa2.id
        
        # Autorización de autocolectivo para empresa 2
        auth2 = AutorizacionEmpresa(
            empresa_id=empresa2.id,
            tipo_autorizacion_id=tipos_auth_objs[1].id,  # AUTOCOLECTIVO
            numero_resolucion="RD-2024-002-DRTC-PUNO",
            fecha_emision=date(2024, 2, 20),
            fecha_vencimiento=date(2025, 12, 31),
            vigente=True
        )
        session.add(auth2)
        
        # Empresa 3: Transportes Altiplano SAC (Mercancías)
        gerente3 = Usuario(
            email="gerente.altiplano@transportes.com",
            password_hash=hash_password("Gerente123!"),
            nombres="Pedro Luis",
            apellidos="Ccama Apaza",
            rol=RolUsuario.GERENTE,
            activo=True
        )
        session.add(gerente3)
        await session.flush()
        
        empresa3 = Empresa(
            ruc="20456789123",
            razon_social="Transportes Altiplano SAC",
            direccion="Av. Circunvalación 789, Puno",
            telefono="051-367890",
            email="contacto@transportesaltiplano.com",
            gerente_id=gerente3.id,
            activo=True
        )
        session.add(empresa3)
        await session.flush()
        
        gerente3.empresa_id = empresa3.id
        
        # Autorización de mercancías para empresa 3
        auth3 = AutorizacionEmpresa(
            empresa_id=empresa3.id,
            tipo_autorizacion_id=tipos_auth_objs[2].id,  # MERCANCIAS
            numero_resolucion="RD-2024-003-DRTC-PUNO",
            fecha_emision=date(2024, 3, 10),
            fecha_vencimiento=date(2025, 12, 31),
            vigente=True
        )
        session.add(auth3)
        
        await session.flush()
        
        # 5. Crear conductores
        print("\n🚗 Creando conductores...")
        
        # Conductores para Empresa 1 (Turismo)
        conductores_empresa1 = [
            {
                "dni": "12345678",
                "nombres": "Juan Carlos",
                "apellidos": "Mamani Quispe",
                "fecha_nacimiento": date(1985, 5, 15),
                "direccion": "Jr. Lima 123, Puno",
                "telefono": "987654321",
                "email": "juan.mamani@email.com",
                "licencia_numero": "L12345678",
                "licencia_categoria": "A-IIIb",
                "licencia_emision": date(2020, 1, 15),
                "licencia_vencimiento": date(2026, 1, 15),
                "estado": EstadoConductor.HABILITADO
            },
            {
                "dni": "23456789",
                "nombres": "María Elena",
                "apellidos": "Condori Apaza",
                "fecha_nacimiento": date(1990, 8, 20),
                "direccion": "Av. El Sol 456, Puno",
                "telefono": "987654322",
                "email": "maria.condori@email.com",
                "licencia_numero": "L23456789",
                "licencia_categoria": "A-IIb",
                "licencia_emision": date(2021, 3, 10),
                "licencia_vencimiento": date(2026, 3, 10),
                "estado": EstadoConductor.HABILITADO
            }
        ]
        
        for conductor_data in conductores_empresa1:
            conductor = Conductor(empresa_id=empresa1.id, **conductor_data)
            session.add(conductor)
        
        # Conductores para Empresa 2 (Autocolectivo)
        conductores_empresa2 = [
            {
                "dni": "34567890",
                "nombres": "Pedro Luis",
                "apellidos": "Quispe Huanca",
                "fecha_nacimiento": date(1988, 3, 25),
                "direccion": "Jr. San Román 789, Juliaca",
                "telefono": "987654323",
                "email": "pedro.quispe@email.com",
                "licencia_numero": "L34567890",
                "licencia_categoria": "A-IIb",
                "licencia_emision": date(2019, 6, 20),
                "licencia_vencimiento": date(2026, 6, 20),
                "estado": EstadoConductor.PENDIENTE
            }
        ]
        
        for conductor_data in conductores_empresa2:
            conductor = Conductor(empresa_id=empresa2.id, **conductor_data)
            session.add(conductor)
        
        # Conductores para Empresa 3 (Mercancías)
        conductores_empresa3 = [
            {
                "dni": "45678901",
                "nombres": "Roberto Carlos",
                "apellidos": "Ccama Apaza",
                "fecha_nacimiento": date(1982, 11, 30),
                "direccion": "Av. Circunvalación 321, Puno",
                "telefono": "987654324",
                "email": "roberto.ccama@email.com",
                "licencia_numero": "L45678901",
                "licencia_categoria": "A-IIIc",
                "licencia_emision": date(2018, 9, 15),
                "licencia_vencimiento": date(2026, 9, 15),
                "estado": EstadoConductor.SUSPENDIDO
            }
        ]
        
        for conductor_data in conductores_empresa3:
            conductor = Conductor(empresa_id=empresa3.id, **conductor_data)
            session.add(conductor)
        
        await session.flush()
        
        # 6. Crear habilitaciones y pagos
        print("\n📄 Creando habilitaciones y pagos...")
        
        # Obtener conductores creados
        from sqlalchemy import select
        result = await session.execute(select(Conductor))
        conductores = result.scalars().all()
        
        for i, conductor in enumerate(conductores[:2]):  # Solo para los primeros 2
            # Crear habilitación
            habilitacion = Habilitacion(
                conductor_id=conductor.id,
                codigo_habilitacion=f"HAB-{datetime.now().strftime('%Y%m%d')}-{i+1:04d}",
                estado=EstadoHabilitacion.HABILITADO if conductor.estado == EstadoConductor.HABILITADO else EstadoHabilitacion.PENDIENTE,
                fecha_solicitud=datetime.now() - timedelta(days=30),
                fecha_habilitacion=datetime.now() - timedelta(days=15) if conductor.estado == EstadoConductor.HABILITADO else None,
                vigencia_hasta=date.today() + timedelta(days=365) if conductor.estado == EstadoConductor.HABILITADO else None
            )
            session.add(habilitacion)
            await session.flush()
            
            # Crear pago
            pago = Pago(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto_hab.id,
                numero_recibo=f"REC-{datetime.now().strftime('%Y%m%d')}-{i+1:04d}",
                monto=Decimal("50.00"),
                fecha_pago=date.today() - timedelta(days=20),
                entidad_bancaria="Banco de la Nación",
                estado=EstadoPago.CONFIRMADO if conductor.estado == EstadoConductor.HABILITADO else EstadoPago.PENDIENTE,
                fecha_confirmacion=datetime.now() - timedelta(days=18) if conductor.estado == EstadoConductor.HABILITADO else None
            )
            session.add(pago)
        
        await session.commit()
        
        print("\n✅ Datos de prueba creados exitosamente!")
        print("\n📊 Resumen:")
        print(f"  - Usuarios: 6 (1 admin, 1 director, 1 operario, 3 gerentes)")
        print(f"  - Empresas: 3 (con autorizaciones)")
        print(f"  - Tipos de Autorización: 5")
        print(f"  - Conductores: 4")
        print(f"  - Habilitaciones: 2")
        print(f"  - Pagos: 2")
        print("\n🔑 Credenciales de acceso:")
        print("  Admin: admin@drtc.gob.pe / Admin123!")
        print("  Director: director@drtc.gob.pe / Director123!")
        print("  Operario: operario@drtc.gob.pe / Operario123!")
        print("  Gerente 1: gerente.puno@transportes.com / Gerente123!")
        print("  Gerente 2: gerente.juliaca@transportes.com / Gerente123!")
        print("  Gerente 3: gerente.altiplano@transportes.com / Gerente123!")


if __name__ == "__main__":
    asyncio.run(init_test_data())
