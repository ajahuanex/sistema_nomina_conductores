"""
Configuración de pytest y fixtures
"""
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

# Import all models FIRST to register them with Base.metadata
import app.models  # noqa: F401

from app.core.database import Base
from app.models.user import Usuario, RolUsuario

# URL de base de datos de prueba
# Note: Using file-based SQLite for tests because in-memory databases
# don't share state across connections in async context
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.close()


@pytest_asyncio.fixture
async def usuario_superusuario(db_session: AsyncSession) -> Usuario:
    """Create test superuser"""
    usuario = Usuario(
        email="superuser@test.com",
        password_hash="hashed_password",
        nombres="Super",
        apellidos="Usuario",
        rol=RolUsuario.SUPERUSUARIO,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
async def usuario_gerente(db_session: AsyncSession) -> Usuario:
    """Create test gerente"""
    usuario = Usuario(
        email="gerente@test.com",
        password_hash="hashed_password",
        nombres="Gerente",
        apellidos="Test",
        rol=RolUsuario.GERENTE,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> Usuario:
    """Create test user for authentication tests"""
    from app.core.security import hash_password
    
    usuario = Usuario(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nombres="Test",
        apellidos="User",
        rol=RolUsuario.DIRECTOR,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """Create test client"""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.core.database import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(test_user: Usuario) -> dict:
    """Create authentication headers with valid token"""
    from app.core.security import create_access_token
    
    token = create_access_token({
        "sub": str(test_user.id),
        "email": test_user.email,
        "rol": test_user.rol.value
    })
    
    return {"Authorization": f"Bearer {token}"}



@pytest_asyncio.fixture
async def superusuario_usuario(db_session: AsyncSession) -> Usuario:
    """Create superusuario for tests"""
    from app.core.security import hash_password
    
    usuario = Usuario(
        email="superusuario@drtc.gob.pe",
        password_hash=hash_password("superusuario123!"),
        nombres="Super",
        apellidos="Usuario",
        rol=RolUsuario.SUPERUSUARIO,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
async def director_usuario(db_session: AsyncSession) -> Usuario:
    """Create director for tests"""
    from app.core.security import hash_password
    
    usuario = Usuario(
        email="director@drtc.gob.pe",
        password_hash=hash_password("director123!"),
        nombres="Director",
        apellidos="Test",
        rol=RolUsuario.DIRECTOR,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
async def operario_usuario(db_session: AsyncSession) -> Usuario:
    """Create operario for tests"""
    from app.core.security import hash_password
    
    usuario = Usuario(
        email="operario@drtc.gob.pe",
        password_hash=hash_password("operario123!"),
        nombres="Operario",
        apellidos="Test",
        rol=RolUsuario.OPERARIO,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
async def superusuario_token(superusuario_usuario: Usuario) -> str:
    """Create access token for superusuario"""
    from app.core.security import create_access_token
    
    token = create_access_token({
        "sub": str(superusuario_usuario.id),
        "email": superusuario_usuario.email,
        "rol": superusuario_usuario.rol.value
    })
    
    return token


@pytest_asyncio.fixture
async def director_token(director_usuario: Usuario) -> str:
    """Create access token for director"""
    from app.core.security import create_access_token
    
    token = create_access_token({
        "sub": str(director_usuario.id),
        "email": director_usuario.email,
        "rol": director_usuario.rol.value
    })
    
    return token


@pytest_asyncio.fixture
async def operario_token(operario_usuario: Usuario) -> str:
    """Create access token for operario"""
    from app.core.security import create_access_token
    
    token = create_access_token({
        "sub": str(operario_usuario.id),
        "email": operario_usuario.email,
        "rol": operario_usuario.rol.value
    })
    
    return token


# Factories para Empresa y relacionados

@pytest_asyncio.fixture
def tipo_autorizacion_factory(db_session: AsyncSession):
    """Factory para crear tipos de autorización"""
    from app.models.empresa import TipoAutorizacion
    
    async def _create(**kwargs):
        defaults = {
            "codigo": f"TIPO_{kwargs.get('codigo', 'TEST')}",
            "nombre": kwargs.get("nombre", "Tipo Test"),
            "descripcion": kwargs.get("descripcion", "Descripción de prueba"),
            "requisitos_especiales": kwargs.get("requisitos_especiales", {})
        }
        defaults.update(kwargs)
        
        tipo = TipoAutorizacion(**defaults)
        db_session.add(tipo)
        await db_session.commit()
        await db_session.refresh(tipo)
        return tipo
    
    return _create


@pytest_asyncio.fixture
def empresa_factory(db_session: AsyncSession):
    """Factory para crear empresas"""
    from app.models.empresa import Empresa, AutorizacionEmpresa
    from datetime import date, timedelta
    import random
    
    async def _create(**kwargs):
        # Generar RUC único si no se proporciona
        if 'ruc' not in kwargs:
            kwargs['ruc'] = f"20{random.randint(100000000, 999999999)}"
        
        defaults = {
            "razon_social": kwargs.get("razon_social", "Empresa Test SAC"),
            "direccion": kwargs.get("direccion", "Av. Test 123"),
            "telefono": kwargs.get("telefono", "051-123456"),
            "email": kwargs.get("email", f"empresa{random.randint(1000, 9999)}@test.com"),
            "gerente_id": kwargs.get("gerente_id", None),
            "activo": kwargs.get("activo", True)
        }
        defaults.update(kwargs)
        
        empresa = Empresa(**defaults)
        db_session.add(empresa)
        await db_session.commit()
        await db_session.refresh(empresa)
        return empresa
    
    async def _create_with_autorizacion(tipo_autorizacion, **kwargs):
        """Crea empresa con una autorización"""
        empresa = await _create(**kwargs)
        
        autorizacion = AutorizacionEmpresa(
            empresa_id=empresa.id,
            tipo_autorizacion_id=tipo_autorizacion.id,
            numero_resolucion=f"RD-2024-{random.randint(1000, 9999)}",
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            vigente=True
        )
        db_session.add(autorizacion)
        await db_session.commit()
        await db_session.refresh(empresa)
        
        return empresa
    
    _create.create_with_autorizacion = _create_with_autorizacion
    
    return _create


@pytest_asyncio.fixture
def autorizacion_empresa_factory(db_session: AsyncSession):
    """Factory para crear autorizaciones de empresa"""
    from app.models.empresa import AutorizacionEmpresa
    from datetime import date, timedelta
    import random
    
    async def _create(**kwargs):
        defaults = {
            "numero_resolucion": kwargs.get("numero_resolucion", f"RD-2024-{random.randint(1000, 9999)}"),
            "fecha_emision": kwargs.get("fecha_emision", date.today()),
            "fecha_vencimiento": kwargs.get("fecha_vencimiento", date.today() + timedelta(days=365)),
            "vigente": kwargs.get("vigente", True)
        }
        defaults.update(kwargs)
        
        autorizacion = AutorizacionEmpresa(**defaults)
        db_session.add(autorizacion)
        await db_session.commit()
        await db_session.refresh(autorizacion)
        return autorizacion
    
    return _create


@pytest_asyncio.fixture
def conductor_factory(db_session: AsyncSession, empresa_factory):
    """Factory para crear conductores"""
    from app.models.conductor import Conductor, EstadoConductor
    from datetime import date, timedelta
    import random
    
    async def _create(**kwargs):
        # Crear empresa si no se proporciona empresa_id
        if 'empresa_id' not in kwargs:
            empresa = await empresa_factory()
            kwargs['empresa_id'] = empresa.id
        
        # Generar DNI único si no se proporciona
        if 'dni' not in kwargs:
            kwargs['dni'] = f"{random.randint(10000000, 99999999)}"
        
        defaults = {
            "nombres": kwargs.get("nombres", "Conductor"),
            "apellidos": kwargs.get("apellidos", "Test"),
            "fecha_nacimiento": kwargs.get("fecha_nacimiento", date(1990, 1, 1)),
            "direccion": kwargs.get("direccion", "Jr. Test 456"),
            "telefono": kwargs.get("telefono", "987654321"),
            "email": kwargs.get("email", f"conductor{random.randint(1000, 9999)}@test.com"),
            "licencia_numero": kwargs.get("licencia_numero", f"L{random.randint(10000000, 99999999)}"),
            "licencia_categoria": kwargs.get("licencia_categoria", "A-IIIb"),
            "licencia_emision": kwargs.get("licencia_emision", date.today() - timedelta(days=365)),
            "licencia_vencimiento": kwargs.get("licencia_vencimiento", date.today() + timedelta(days=365)),
            "estado": kwargs.get("estado", EstadoConductor.PENDIENTE)
        }
        defaults.update(kwargs)
        
        conductor = Conductor(**defaults)
        db_session.add(conductor)
        await db_session.commit()
        await db_session.refresh(conductor)
        return conductor
    
    return _create



@pytest_asyncio.fixture
async def gerente_usuario_with_empresa(db_session: AsyncSession, empresa_factory) -> tuple[Usuario, any]:
    """Create gerente with empresa for tests"""
    from app.core.security import hash_password
    
    # Crear empresa primero
    empresa = await empresa_factory()
    
    # Crear gerente
    usuario = Usuario(
        email="gerente@empresa.com",
        password_hash=hash_password("gerente123!"),
        nombres="Gerente",
        apellidos="Empresa",
        rol=RolUsuario.GERENTE,
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    
    # Asignar gerente a empresa
    empresa.gerente_id = usuario.id
    await db_session.commit()
    await db_session.refresh(empresa)
    
    return usuario, empresa


@pytest_asyncio.fixture
async def auth_headers_gerente(gerente_usuario_with_empresa) -> dict:
    """Create authentication headers for gerente"""
    from app.core.security import create_access_token
    
    usuario, empresa = gerente_usuario_with_empresa
    
    token = create_access_token({
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value
    })
    
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_operario(operario_usuario: Usuario) -> dict:
    """Create authentication headers for operario"""
    from app.core.security import create_access_token
    
    token = create_access_token({
        "sub": str(operario_usuario.id),
        "email": operario_usuario.email,
        "rol": operario_usuario.rol.value
    })
    
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def empresa_test(db_session: AsyncSession, usuario_gerente: Usuario):
    """Create test empresa with gerente"""
    from app.models.empresa import Empresa
    
    empresa = Empresa(
        ruc="20123456789",
        razon_social="Transportes Test SAC",
        direccion="Av. Test 123",
        telefono="051-123456",
        email="test@transportes.com",
        gerente_id=usuario_gerente.id,
        activo=True
    )
    db_session.add(empresa)
    await db_session.commit()
    await db_session.refresh(empresa)
    return empresa


# Factories para Habilitación y Pago

@pytest_asyncio.fixture
def habilitacion_factory(db_session: AsyncSession, conductor_factory):
    """Factory para crear habilitaciones"""
    from app.models.habilitacion import Habilitacion, EstadoHabilitacion
    from datetime import datetime, date, timedelta
    import random
    
    async def _create(**kwargs):
        # Crear conductor si no se proporciona conductor_id
        if 'conductor_id' not in kwargs:
            conductor = await conductor_factory()
            kwargs['conductor_id'] = conductor.id
        
        # Generar código único si no se proporciona
        if 'codigo_habilitacion' not in kwargs:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_id = f"{random.randint(10000000, 99999999)}"
            kwargs['codigo_habilitacion'] = f"HAB-{timestamp}-{unique_id}"
        
        defaults = {
            "estado": kwargs.get("estado", EstadoHabilitacion.PENDIENTE),
            "observaciones": kwargs.get("observaciones", None),
            "revisado_por": kwargs.get("revisado_por", None),
            "aprobado_por": kwargs.get("aprobado_por", None),
            "habilitado_por": kwargs.get("habilitado_por", None),
            "fecha_solicitud": kwargs.get("fecha_solicitud", datetime.utcnow()),
            "fecha_revision": kwargs.get("fecha_revision", None),
            "fecha_aprobacion": kwargs.get("fecha_aprobacion", None),
            "fecha_habilitacion": kwargs.get("fecha_habilitacion", None),
            "vigencia_hasta": kwargs.get("vigencia_hasta", None)
        }
        defaults.update(kwargs)
        
        habilitacion = Habilitacion(**defaults)
        db_session.add(habilitacion)
        await db_session.commit()
        await db_session.refresh(habilitacion)
        return habilitacion
    
    return _create


@pytest_asyncio.fixture
def concepto_tupa_factory(db_session: AsyncSession):
    """Factory para crear conceptos TUPA"""
    from app.models.habilitacion import ConceptoTUPA
    from datetime import date, timedelta
    from decimal import Decimal
    import random
    
    async def _create(**kwargs):
        defaults = {
            "codigo": kwargs.get("codigo", f"TUPA-{random.randint(1000, 9999)}"),
            "descripcion": kwargs.get("descripcion", "Concepto TUPA de prueba"),
            "monto": kwargs.get("monto", Decimal("150.00")),
            "vigencia_desde": kwargs.get("vigencia_desde", date.today()),
            "vigencia_hasta": kwargs.get("vigencia_hasta", None),
            "activo": kwargs.get("activo", True)
        }
        defaults.update(kwargs)
        
        concepto = ConceptoTUPA(**defaults)
        db_session.add(concepto)
        await db_session.commit()
        await db_session.refresh(concepto)
        return concepto
    
    return _create


@pytest_asyncio.fixture
def pago_factory(db_session: AsyncSession, concepto_tupa_factory):
    """Factory para crear pagos"""
    from app.models.habilitacion import Pago, EstadoPago
    from datetime import date
    from decimal import Decimal
    import random
    
    async def _create(**kwargs):
        # Crear concepto TUPA si no se proporciona
        if 'concepto_tupa_id' not in kwargs:
            concepto = await concepto_tupa_factory()
            kwargs['concepto_tupa_id'] = concepto.id
        
        defaults = {
            "numero_recibo": kwargs.get("numero_recibo", f"REC-2024-{random.randint(10000, 99999)}"),
            "monto": kwargs.get("monto", Decimal("150.00")),
            "fecha_pago": kwargs.get("fecha_pago", date.today()),
            "entidad_bancaria": kwargs.get("entidad_bancaria", "Banco de la Nación"),
            "estado": kwargs.get("estado", EstadoPago.PENDIENTE),
            "observaciones": kwargs.get("observaciones", None),
            "registrado_por": kwargs.get("registrado_por", None),
            "fecha_confirmacion": kwargs.get("fecha_confirmacion", None),
            "confirmado_por": kwargs.get("confirmado_por", None)
        }
        defaults.update(kwargs)
        
        pago = Pago(**defaults)
        db_session.add(pago)
        await db_session.commit()
        await db_session.refresh(pago)
        return pago
    
    return _create


@pytest_asyncio.fixture
def usuario_factory(db_session: AsyncSession):
    """Factory para crear usuarios"""
    from app.models.user import Usuario, RolUsuario
    from app.core.security import hash_password
    import random
    
    async def _create(**kwargs):
        defaults = {
            "email": kwargs.get("email", f"usuario{random.randint(1000, 9999)}@test.com"),
            "password_hash": kwargs.get("password_hash", hash_password("password123")),
            "nombres": kwargs.get("nombres", "Usuario"),
            "apellidos": kwargs.get("apellidos", "Test"),
            "rol": kwargs.get("rol", RolUsuario.OPERARIO),
            "activo": kwargs.get("activo", True)
        }
        defaults.update(kwargs)
        
        usuario = Usuario(**defaults)
        db_session.add(usuario)
        await db_session.commit()
        await db_session.refresh(usuario)
        return usuario
    
    return _create


# Factories for testing

class UsuarioFactory:
    """Factory for creating Usuario instances"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.counter = 0
    
    async def create(self, **kwargs):
        from app.models.user import Usuario, RolUsuario
        self.counter += 1
        defaults = {
            "email": f"user{self.counter}@test.com",
            "password_hash": "hashed_password",
            "nombres": f"Usuario{self.counter}",
            "apellidos": "Test",
            "rol": RolUsuario.OPERARIO,
            "activo": True
        }
        defaults.update(kwargs)
        usuario = Usuario(**defaults)
        self.db_session.add(usuario)
        await self.db_session.commit()
        await self.db_session.refresh(usuario)
        return usuario


class EmpresaFactory:
    """Factory for creating Empresa instances"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.counter = 0
    
    async def create(self, **kwargs):
        from app.models.empresa import Empresa
        self.counter += 1
        defaults = {
            "ruc": f"2012345678{self.counter:01d}",
            "razon_social": f"Empresa Test {self.counter}",
            "direccion": f"Av. Test {self.counter}",
            "telefono": "987654321",
            "email": f"empresa{self.counter}@test.com",
            "activo": True
        }
        defaults.update(kwargs)
        empresa = Empresa(**defaults)
        self.db_session.add(empresa)
        await self.db_session.commit()
        await self.db_session.refresh(empresa)
        return empresa


class ConductorFactory:
    """Factory for creating Conductor instances"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.counter = 0
        self.empresa_factory = EmpresaFactory(db_session)
    
    async def create(self, **kwargs):
        from app.models.conductor import Conductor, EstadoConductor
        from datetime import date, timedelta
        self.counter += 1
        
        # Crear empresa si no se proporciona empresa_id
        if 'empresa_id' not in kwargs:
            empresa = await self.empresa_factory.create()
            kwargs['empresa_id'] = empresa.id
        
        defaults = {
            "dni": f"1234567{self.counter:01d}",
            "nombres": f"Conductor{self.counter}",
            "apellidos": "Test",
            "fecha_nacimiento": date(1990, 1, 1),
            "direccion": f"Jr. Test {self.counter}",
            "telefono": "987654321",
            "email": f"conductor{self.counter}@test.com",
            "licencia_numero": f"L{self.counter:08d}",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date.today() - timedelta(days=365),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "estado": EstadoConductor.PENDIENTE
        }
        defaults.update(kwargs)
        conductor = Conductor(**defaults)
        self.db_session.add(conductor)
        await self.db_session.commit()
        await self.db_session.refresh(conductor)
        return conductor


class HabilitacionFactory:
    """Factory for creating Habilitacion instances"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.counter = 0
        self.conductor_factory = None
    
    async def create(self, **kwargs):
        from app.models.habilitacion import Habilitacion, EstadoHabilitacion
        from datetime import datetime
        self.counter += 1
        
        # Crear conductor si no se proporciona conductor_id
        if 'conductor_id' not in kwargs:
            if self.conductor_factory is None:
                self.conductor_factory = ConductorFactory(self.db_session)
            conductor = await self.conductor_factory.create()
            kwargs['conductor_id'] = conductor.id
        
        defaults = {
            "codigo_habilitacion": f"HAB-{datetime.now().strftime('%Y%m%d')}-{self.counter:04d}",
            "estado": EstadoHabilitacion.PENDIENTE
        }
        defaults.update(kwargs)
        habilitacion = Habilitacion(**defaults)
        self.db_session.add(habilitacion)
        await self.db_session.commit()
        await self.db_session.refresh(habilitacion)
        return habilitacion


class ConceptoTUPAFactory:
    """Factory for creating ConceptoTUPA instances"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.counter = 0
    
    async def create(self, **kwargs):
        from app.models.habilitacion import ConceptoTUPA
        from datetime import date
        from decimal import Decimal
        self.counter += 1
        defaults = {
            "codigo": f"TUPA-{self.counter:03d}",
            "descripcion": f"Concepto TUPA {self.counter}",
            "monto": Decimal("50.00"),
            "vigencia_desde": date.today(),
            "vigencia_hasta": None,
            "activo": True
        }
        defaults.update(kwargs)
        concepto = ConceptoTUPA(**defaults)
        self.db_session.add(concepto)
        await self.db_session.commit()
        await self.db_session.refresh(concepto)
        return concepto


class PagoFactory:
    """Factory for creating Pago instances"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.counter = 0
    
    async def create(self, **kwargs):
        from app.models.habilitacion import Pago, EstadoPago
        from datetime import date
        from decimal import Decimal
        self.counter += 1
        defaults = {
            "numero_recibo": f"REC-{self.counter:06d}",
            "monto": Decimal("50.00"),
            "fecha_pago": date.today(),
            "entidad_bancaria": "Banco de la Nación",
            "estado": EstadoPago.PENDIENTE
        }
        defaults.update(kwargs)
        pago = Pago(**defaults)
        self.db_session.add(pago)
        await self.db_session.commit()
        await self.db_session.refresh(pago)
        return pago


@pytest_asyncio.fixture
async def usuario_factory(db_session: AsyncSession):
    """Fixture for UsuarioFactory"""
    return UsuarioFactory(db_session)


@pytest_asyncio.fixture
async def empresa_factory(db_session: AsyncSession):
    """Fixture for EmpresaFactory"""
    return EmpresaFactory(db_session)


@pytest_asyncio.fixture
async def conductor_factory(db_session: AsyncSession):
    """Fixture for ConductorFactory"""
    return ConductorFactory(db_session)


@pytest_asyncio.fixture
async def habilitacion_factory(db_session: AsyncSession):
    """Fixture for HabilitacionFactory"""
    return HabilitacionFactory(db_session)


@pytest_asyncio.fixture
async def concepto_tupa_factory(db_session: AsyncSession):
    """Fixture for ConceptoTUPAFactory"""
    return ConceptoTUPAFactory(db_session)


@pytest_asyncio.fixture
async def pago_factory(db_session: AsyncSession):
    """Fixture for PagoFactory"""
    return PagoFactory(db_session)


# Fixtures para tests de API

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """Fixture for AsyncClient"""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.core.database import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(usuario_superusuario: Usuario):
    """Fixture for authentication headers"""
    from app.core.security import create_access_token
    
    access_token = create_access_token(data={"sub": usuario_superusuario.email})
    
    return {
        "Authorization": f"Bearer {access_token}"
    }
