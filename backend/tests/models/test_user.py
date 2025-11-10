"""
Tests para modelo Usuario
"""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Usuario, RolUsuario


@pytest.mark.asyncio
async def test_crear_usuario(db_session: AsyncSession):
    """Test crear usuario básico"""
    usuario = Usuario(
        email="test@example.com",
        password_hash="hashed_password",
        nombres="Juan",
        apellidos="Pérez",
        rol=RolUsuario.OPERARIO,
        activo=True
    )
    
    db_session.add(usuario)
    await db_session.commit()
    await db_session.refresh(usuario)
    
    assert usuario.id is not None
    assert usuario.email == "test@example.com"
    assert usuario.rol == RolUsuario.OPERARIO
    assert usuario.activo is True
    assert usuario.created_at is not None
    assert usuario.updated_at is not None


@pytest.mark.asyncio
async def test_nombre_completo(usuario_superusuario: Usuario):
    """Test propiedad nombre_completo"""
    assert usuario_superusuario.nombre_completo == "Super Usuario"


@pytest.mark.asyncio
async def test_tiene_rol(usuario_superusuario: Usuario, usuario_gerente: Usuario):
    """Test método tiene_rol"""
    assert usuario_superusuario.tiene_rol(RolUsuario.SUPERUSUARIO)
    assert usuario_superusuario.tiene_rol(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR)
    assert not usuario_superusuario.tiene_rol(RolUsuario.GERENTE)
    
    assert usuario_gerente.tiene_rol(RolUsuario.GERENTE)
    assert not usuario_gerente.tiene_rol(RolUsuario.SUPERUSUARIO)


@pytest.mark.asyncio
async def test_es_administrador(usuario_superusuario: Usuario, usuario_gerente: Usuario):
    """Test método es_administrador"""
    assert usuario_superusuario.es_administrador() is True
    assert usuario_gerente.es_administrador() is False


@pytest.mark.asyncio
async def test_puede_habilitar(usuario_superusuario: Usuario, usuario_gerente: Usuario):
    """Test método puede_habilitar"""
    assert usuario_superusuario.puede_habilitar() is True
    assert usuario_gerente.puede_habilitar() is False


@pytest.mark.asyncio
async def test_email_unico(db_session: AsyncSession):
    """Test que email debe ser único"""
    usuario1 = Usuario(
        email="duplicado@test.com",
        password_hash="hash1",
        nombres="Usuario",
        apellidos="Uno",
        rol=RolUsuario.OPERARIO,
        activo=True
    )
    
    db_session.add(usuario1)
    await db_session.commit()
    
    usuario2 = Usuario(
        email="duplicado@test.com",
        password_hash="hash2",
        nombres="Usuario",
        apellidos="Dos",
        rol=RolUsuario.OPERARIO,
        activo=True
    )
    
    db_session.add(usuario2)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_buscar_por_email(db_session: AsyncSession, usuario_superusuario: Usuario):
    """Test buscar usuario por email"""
    result = await db_session.execute(
        select(Usuario).where(Usuario.email == "superuser@test.com")
    )
    usuario = result.scalar_one_or_none()
    
    assert usuario is not None
    assert usuario.email == "superuser@test.com"
    assert usuario.rol == RolUsuario.SUPERUSUARIO


@pytest.mark.asyncio
async def test_filtrar_por_rol(db_session: AsyncSession):
    """Test filtrar usuarios por rol"""
    # Crear varios usuarios con diferentes roles
    usuarios = [
        Usuario(
            email=f"user{i}@test.com",
            password_hash="hash",
            nombres=f"Usuario{i}",
            apellidos="Test",
            rol=RolUsuario.OPERARIO if i % 2 == 0 else RolUsuario.GERENTE,
            activo=True
        )
        for i in range(5)
    ]
    
    for usuario in usuarios:
        db_session.add(usuario)
    await db_session.commit()
    
    # Buscar solo operarios
    result = await db_session.execute(
        select(Usuario).where(Usuario.rol == RolUsuario.OPERARIO)
    )
    operarios = result.scalars().all()
    
    assert len(operarios) == 3  # 0, 2, 4
    assert all(u.rol == RolUsuario.OPERARIO for u in operarios)


@pytest.mark.asyncio
async def test_usuario_activo_inactivo(db_session: AsyncSession):
    """Test filtrar usuarios activos/inactivos"""
    usuario_activo = Usuario(
        email="activo@test.com",
        password_hash="hash",
        nombres="Activo",
        apellidos="Test",
        rol=RolUsuario.OPERARIO,
        activo=True
    )
    
    usuario_inactivo = Usuario(
        email="inactivo@test.com",
        password_hash="hash",
        nombres="Inactivo",
        apellidos="Test",
        rol=RolUsuario.OPERARIO,
        activo=False
    )
    
    db_session.add(usuario_activo)
    db_session.add(usuario_inactivo)
    await db_session.commit()
    
    # Buscar solo activos
    result = await db_session.execute(
        select(Usuario).where(Usuario.activo == True)
    )
    activos = result.scalars().all()
    
    assert len(activos) >= 1
    assert all(u.activo for u in activos)
