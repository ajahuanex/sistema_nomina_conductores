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
