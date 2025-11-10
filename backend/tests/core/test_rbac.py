"""
Tests para el sistema RBAC (Control de Acceso Basado en Roles)
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.core.rbac import (
    require_roles,
    require_admin,
    require_superuser,
    verify_empresa_access,
    verify_conductor_access,
    can_modify_user,
    can_create_user_with_role,
    can_habilitar_conductor,
    can_revisar_solicitud,
    can_access_configuracion,
    can_access_auditoria,
    filter_empresas_by_access,
    PermissionDenied
)
from app.models.user import Usuario, RolUsuario


# Fixtures para usuarios de diferentes roles
@pytest.fixture
def superusuario():
    """Usuario con rol Superusuario"""
    user = Usuario(
        id=uuid4(),
        email="super@test.com",
        password_hash="hashed",
        nombres="Super",
        apellidos="Usuario",
        rol=RolUsuario.SUPERUSUARIO,
        activo=True,
        empresa_id=None
    )
    return user


@pytest.fixture
def director():
    """Usuario con rol Director"""
    user = Usuario(
        id=uuid4(),
        email="director@test.com",
        password_hash="hashed",
        nombres="Director",
        apellidos="Test",
        rol=RolUsuario.DIRECTOR,
        activo=True,
        empresa_id=None
    )
    return user


@pytest.fixture
def subdirector():
    """Usuario con rol Subdirector"""
    user = Usuario(
        id=uuid4(),
        email="subdirector@test.com",
        password_hash="hashed",
        nombres="Subdirector",
        apellidos="Test",
        rol=RolUsuario.SUBDIRECTOR,
        activo=True,
        empresa_id=None
    )
    return user


@pytest.fixture
def operario():
    """Usuario con rol Operario"""
    user = Usuario(
        id=uuid4(),
        email="operario@test.com",
        password_hash="hashed",
        nombres="Operario",
        apellidos="Test",
        rol=RolUsuario.OPERARIO,
        activo=True,
        empresa_id=None
    )
    return user


@pytest.fixture
def gerente():
    """Usuario con rol Gerente"""
    empresa_id = uuid4()
    user = Usuario(
        id=uuid4(),
        email="gerente@test.com",
        password_hash="hashed",
        nombres="Gerente",
        apellidos="Test",
        rol=RolUsuario.GERENTE,
        activo=True,
        empresa_id=empresa_id
    )
    return user


@pytest.fixture
def otro_gerente():
    """Otro usuario con rol Gerente (diferente empresa)"""
    empresa_id = uuid4()
    user = Usuario(
        id=uuid4(),
        email="gerente2@test.com",
        password_hash="hashed",
        nombres="Gerente",
        apellidos="Dos",
        rol=RolUsuario.GERENTE,
        activo=True,
        empresa_id=empresa_id
    )
    return user


# Tests para verify_empresa_access
@pytest.mark.asyncio
async def test_superusuario_accede_cualquier_empresa(superusuario):
    """Superusuario debe tener acceso a cualquier empresa"""
    empresa_id = uuid4()
    db = AsyncMock()
    
    result = await verify_empresa_access(empresa_id, superusuario, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_director_accede_cualquier_empresa(director):
    """Director debe tener acceso a cualquier empresa"""
    empresa_id = uuid4()
    db = AsyncMock()
    
    result = await verify_empresa_access(empresa_id, director, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_subdirector_accede_cualquier_empresa(subdirector):
    """Subdirector debe tener acceso a cualquier empresa"""
    empresa_id = uuid4()
    db = AsyncMock()
    
    result = await verify_empresa_access(empresa_id, subdirector, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_operario_accede_cualquier_empresa(operario):
    """Operario debe tener acceso a cualquier empresa"""
    empresa_id = uuid4()
    db = AsyncMock()
    
    result = await verify_empresa_access(empresa_id, operario, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_gerente_accede_solo_su_empresa(gerente):
    """Gerente solo debe tener acceso a su propia empresa"""
    db = AsyncMock()
    
    # Acceso a su propia empresa
    result = await verify_empresa_access(gerente.empresa_id, gerente, db)
    assert result is True
    
    # No acceso a otra empresa
    otra_empresa_id = uuid4()
    result = await verify_empresa_access(otra_empresa_id, gerente, db)
    assert result is False


# Tests para verify_conductor_access
@pytest.mark.asyncio
async def test_superusuario_accede_cualquier_conductor(superusuario):
    """Superusuario debe tener acceso a cualquier conductor"""
    conductor_id = uuid4()
    db = AsyncMock()
    
    result = await verify_conductor_access(conductor_id, superusuario, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_director_accede_cualquier_conductor(director):
    """Director debe tener acceso a cualquier conductor"""
    conductor_id = uuid4()
    db = AsyncMock()
    
    result = await verify_conductor_access(conductor_id, director, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_operario_accede_cualquier_conductor(operario):
    """Operario debe tener acceso a cualquier conductor"""
    conductor_id = uuid4()
    db = AsyncMock()
    
    result = await verify_conductor_access(conductor_id, operario, db)
    
    assert result is True


@pytest.mark.asyncio
async def test_gerente_accede_solo_conductores_su_empresa(gerente):
    """Gerente solo debe tener acceso a conductores de su empresa"""
    from app.models.conductor import Conductor, EstadoConductor
    from datetime import date, timedelta
    
    conductor_id = uuid4()
    db = AsyncMock()
    
    # Mock conductor de su empresa con licencia vigente
    fecha_vencimiento = date.today() + timedelta(days=365)
    conductor_su_empresa = Conductor(
        id=conductor_id,
        dni="12345678",
        nombres="Juan",
        apellidos="Pérez",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Av. Test 123",
        telefono="987654321",
        email="juan@test.com",
        licencia_numero="L12345678",
        licencia_categoria="A-IIIb",
        licencia_emision=date(2020, 1, 1),
        licencia_vencimiento=fecha_vencimiento,
        empresa_id=gerente.empresa_id,
        estado=EstadoConductor.PENDIENTE
    )
    
    # Configurar mock para retornar el conductor
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = conductor_su_empresa
    db.execute.return_value = mock_result
    
    result = await verify_conductor_access(conductor_id, gerente, db)
    assert result is True


@pytest.mark.asyncio
async def test_gerente_no_accede_conductores_otra_empresa(gerente):
    """Gerente no debe tener acceso a conductores de otra empresa"""
    from app.models.conductor import Conductor, EstadoConductor
    from datetime import date, timedelta
    
    conductor_id = uuid4()
    otra_empresa_id = uuid4()
    db = AsyncMock()
    
    # Mock conductor de otra empresa con licencia vigente
    fecha_vencimiento = date.today() + timedelta(days=365)
    conductor_otra_empresa = Conductor(
        id=conductor_id,
        dni="87654321",
        nombres="María",
        apellidos="García",
        fecha_nacimiento=date(1992, 5, 15),
        direccion="Jr. Test 456",
        telefono="987654322",
        email="maria@test.com",
        licencia_numero="L87654321",
        licencia_categoria="A-IIIb",
        licencia_emision=date(2021, 1, 1),
        licencia_vencimiento=fecha_vencimiento,
        empresa_id=otra_empresa_id,
        estado=EstadoConductor.PENDIENTE
    )
    
    # Configurar mock para retornar el conductor
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = conductor_otra_empresa
    db.execute.return_value = mock_result
    
    result = await verify_conductor_access(conductor_id, gerente, db)
    assert result is False


@pytest.mark.asyncio
async def test_gerente_no_accede_conductor_inexistente(gerente):
    """Gerente no debe tener acceso a conductor que no existe"""
    conductor_id = uuid4()
    db = AsyncMock()
    
    # Configurar mock para retornar None (conductor no existe)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    
    result = await verify_conductor_access(conductor_id, gerente, db)
    assert result is False


# Tests para can_modify_user
def test_superusuario_puede_modificar_cualquier_usuario(superusuario, director, gerente):
    """Superusuario puede modificar cualquier usuario"""
    assert can_modify_user(superusuario, director) is True
    assert can_modify_user(superusuario, gerente) is True
    assert can_modify_user(superusuario, superusuario) is True


def test_director_puede_modificar_subdirector_operario_gerente(director, subdirector, operario, gerente, superusuario):
    """Director puede modificar Subdirectores, Operarios y Gerentes"""
    assert can_modify_user(director, subdirector) is True
    assert can_modify_user(director, operario) is True
    assert can_modify_user(director, gerente) is True
    assert can_modify_user(director, superusuario) is False
    assert can_modify_user(director, director) is False


def test_subdirector_puede_modificar_operario_gerente(subdirector, operario, gerente, director):
    """Subdirector puede modificar Operarios y Gerentes"""
    assert can_modify_user(subdirector, operario) is True
    assert can_modify_user(subdirector, gerente) is True
    assert can_modify_user(subdirector, director) is False
    assert can_modify_user(subdirector, subdirector) is False


def test_operario_no_puede_modificar_usuarios(operario, gerente):
    """Operario no puede modificar usuarios"""
    assert can_modify_user(operario, gerente) is False
    assert can_modify_user(operario, operario) is False


def test_gerente_no_puede_modificar_usuarios(gerente, otro_gerente):
    """Gerente no puede modificar usuarios"""
    assert can_modify_user(gerente, otro_gerente) is False
    assert can_modify_user(gerente, gerente) is False


# Tests para can_create_user_with_role
def test_superusuario_puede_crear_cualquier_rol(superusuario):
    """Superusuario puede crear usuarios con cualquier rol"""
    assert can_create_user_with_role(superusuario, RolUsuario.SUPERUSUARIO) is True
    assert can_create_user_with_role(superusuario, RolUsuario.DIRECTOR) is True
    assert can_create_user_with_role(superusuario, RolUsuario.SUBDIRECTOR) is True
    assert can_create_user_with_role(superusuario, RolUsuario.OPERARIO) is True
    assert can_create_user_with_role(superusuario, RolUsuario.GERENTE) is True


def test_director_puede_crear_subdirector_operario_gerente(director):
    """Director puede crear Subdirectores, Operarios y Gerentes"""
    assert can_create_user_with_role(director, RolUsuario.SUBDIRECTOR) is True
    assert can_create_user_with_role(director, RolUsuario.OPERARIO) is True
    assert can_create_user_with_role(director, RolUsuario.GERENTE) is True
    assert can_create_user_with_role(director, RolUsuario.SUPERUSUARIO) is False
    assert can_create_user_with_role(director, RolUsuario.DIRECTOR) is False


def test_subdirector_puede_crear_operario_gerente(subdirector):
    """Subdirector puede crear Operarios y Gerentes"""
    assert can_create_user_with_role(subdirector, RolUsuario.OPERARIO) is True
    assert can_create_user_with_role(subdirector, RolUsuario.GERENTE) is True
    assert can_create_user_with_role(subdirector, RolUsuario.DIRECTOR) is False
    assert can_create_user_with_role(subdirector, RolUsuario.SUBDIRECTOR) is False


def test_operario_no_puede_crear_usuarios(operario):
    """Operario no puede crear usuarios"""
    assert can_create_user_with_role(operario, RolUsuario.GERENTE) is False
    assert can_create_user_with_role(operario, RolUsuario.OPERARIO) is False


def test_gerente_no_puede_crear_usuarios(gerente):
    """Gerente no puede crear usuarios"""
    assert can_create_user_with_role(gerente, RolUsuario.GERENTE) is False


# Tests para can_habilitar_conductor
def test_superusuario_puede_habilitar(superusuario):
    """Superusuario puede habilitar conductores"""
    assert can_habilitar_conductor(superusuario) is True


def test_director_puede_habilitar(director):
    """Director puede habilitar conductores"""
    assert can_habilitar_conductor(director) is True


def test_subdirector_puede_habilitar(subdirector):
    """Subdirector puede habilitar conductores"""
    assert can_habilitar_conductor(subdirector) is True


def test_operario_no_puede_habilitar(operario):
    """Operario NO puede habilitar conductores (solo revisar)"""
    assert can_habilitar_conductor(operario) is False


def test_gerente_no_puede_habilitar(gerente):
    """Gerente NO puede habilitar conductores"""
    assert can_habilitar_conductor(gerente) is False


# Tests para can_revisar_solicitud
def test_superusuario_puede_revisar(superusuario):
    """Superusuario puede revisar solicitudes"""
    assert can_revisar_solicitud(superusuario) is True


def test_director_puede_revisar(director):
    """Director puede revisar solicitudes"""
    assert can_revisar_solicitud(director) is True


def test_subdirector_puede_revisar(subdirector):
    """Subdirector puede revisar solicitudes"""
    assert can_revisar_solicitud(subdirector) is True


def test_operario_puede_revisar(operario):
    """Operario puede revisar solicitudes"""
    assert can_revisar_solicitud(operario) is True


def test_gerente_no_puede_revisar(gerente):
    """Gerente NO puede revisar solicitudes"""
    assert can_revisar_solicitud(gerente) is False


# Tests para can_access_configuracion
def test_superusuario_accede_configuracion(superusuario):
    """Superusuario puede acceder a configuración"""
    assert can_access_configuracion(superusuario) is True


def test_director_accede_configuracion(director):
    """Director puede acceder a configuración"""
    assert can_access_configuracion(director) is True


def test_subdirector_no_accede_configuracion(subdirector):
    """Subdirector NO puede acceder a configuración"""
    assert can_access_configuracion(subdirector) is False


def test_operario_no_accede_configuracion(operario):
    """Operario NO puede acceder a configuración"""
    assert can_access_configuracion(operario) is False


def test_gerente_no_accede_configuracion(gerente):
    """Gerente NO puede acceder a configuración"""
    assert can_access_configuracion(gerente) is False


# Tests para can_access_auditoria
def test_superusuario_accede_auditoria(superusuario):
    """Superusuario puede acceder a auditoría"""
    assert can_access_auditoria(superusuario) is True


def test_director_accede_auditoria(director):
    """Director puede acceder a auditoría"""
    assert can_access_auditoria(director) is True


def test_subdirector_no_accede_auditoria(subdirector):
    """Subdirector NO puede acceder a auditoría completa"""
    assert can_access_auditoria(subdirector) is False


def test_operario_no_accede_auditoria(operario):
    """Operario NO puede acceder a auditoría"""
    assert can_access_auditoria(operario) is False


def test_gerente_no_accede_auditoria(gerente):
    """Gerente NO puede acceder a auditoría"""
    assert can_access_auditoria(gerente) is False


# Tests para filter_empresas_by_access
@pytest.mark.asyncio
async def test_superusuario_sin_filtro_empresas(superusuario):
    """Superusuario no debe tener filtro de empresas"""
    db = AsyncMock()
    result = await filter_empresas_by_access(superusuario, db)
    assert result is None


@pytest.mark.asyncio
async def test_director_sin_filtro_empresas(director):
    """Director no debe tener filtro de empresas"""
    db = AsyncMock()
    result = await filter_empresas_by_access(director, db)
    assert result is None


@pytest.mark.asyncio
async def test_operario_sin_filtro_empresas(operario):
    """Operario no debe tener filtro de empresas"""
    db = AsyncMock()
    result = await filter_empresas_by_access(operario, db)
    assert result is None


@pytest.mark.asyncio
async def test_gerente_con_filtro_su_empresa(gerente):
    """Gerente debe tener filtro de su empresa"""
    db = AsyncMock()
    result = await filter_empresas_by_access(gerente, db)
    assert result == gerente.empresa_id


# Tests para PermissionDenied
def test_permission_denied_exception():
    """PermissionDenied debe ser una HTTPException con status 403"""
    exc = PermissionDenied()
    assert exc.status_code == 403
    assert "permisos" in exc.detail.lower()


def test_permission_denied_custom_message():
    """PermissionDenied debe aceptar mensaje personalizado"""
    custom_message = "No puede acceder a este recurso"
    exc = PermissionDenied(detail=custom_message)
    assert exc.detail == custom_message
