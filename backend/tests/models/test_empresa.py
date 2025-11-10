"""
Tests para modelos de Empresa y Autorizaciones
"""
import pytest
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.empresa import Empresa, TipoAutorizacion, AutorizacionEmpresa
from app.models.user import Usuario, RolUsuario


@pytest.fixture
async def tipo_autorizacion_mercancias(db_session: AsyncSession) -> TipoAutorizacion:
    """Fixture para tipo de autorización de mercancías"""
    tipo = TipoAutorizacion(
        codigo="MERCANCIAS",
        nombre="Transporte de Mercancías",
        descripcion="Autorización para transporte de carga y mercancías",
        requisitos_especiales={"licencia_minima": "A-IIIb"}
    )
    db_session.add(tipo)
    await db_session.commit()
    await db_session.refresh(tipo)
    return tipo


@pytest.fixture
async def tipo_autorizacion_turismo(db_session: AsyncSession) -> TipoAutorizacion:
    """Fixture para tipo de autorización de turismo"""
    tipo = TipoAutorizacion(
        codigo="TURISMO",
        nombre="Transporte de Turismo",
        descripcion="Autorización para transporte turístico de pasajeros",
        requisitos_especiales={"licencia_minima": "A-IIb"}
    )
    db_session.add(tipo)
    await db_session.commit()
    await db_session.refresh(tipo)
    return tipo


@pytest.fixture
async def empresa_test(
    db_session: AsyncSession,
    usuario_gerente: Usuario
) -> Empresa:
    """Fixture para empresa de prueba"""
    empresa = Empresa(
        ruc="20123456789",
        razon_social="Transportes Test SAC",
        direccion="Av. Test 123, Puno",
        telefono="987654321",
        email="contacto@transportestest.com",
        gerente_id=usuario_gerente.id,
        activo=True
    )
    db_session.add(empresa)
    await db_session.commit()
    await db_session.refresh(empresa)
    return empresa


# Tests para TipoAutorizacion

@pytest.mark.asyncio
async def test_crear_tipo_autorizacion(db_session: AsyncSession):
    """Test crear tipo de autorización"""
    tipo = TipoAutorizacion(
        codigo="TRABAJADORES",
        nombre="Transporte de Trabajadores",
        descripcion="Autorización para transporte de personal",
        requisitos_especiales={"seguro_obligatorio": True}
    )
    
    db_session.add(tipo)
    await db_session.commit()
    await db_session.refresh(tipo)
    
    assert tipo.id is not None
    assert tipo.codigo == "TRABAJADORES"
    assert tipo.nombre == "Transporte de Trabajadores"
    assert tipo.requisitos_especiales["seguro_obligatorio"] is True
    assert tipo.created_at is not None


@pytest.mark.asyncio
async def test_tipo_autorizacion_codigo_unico(
    db_session: AsyncSession,
    tipo_autorizacion_mercancias: TipoAutorizacion
):
    """Test que el código de tipo de autorización debe ser único"""
    tipo_duplicado = TipoAutorizacion(
        codigo="MERCANCIAS",  # Código duplicado
        nombre="Otro nombre",
        descripcion="Otra descripción"
    )
    
    db_session.add(tipo_duplicado)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


# Tests para Empresa

@pytest.mark.asyncio
async def test_crear_empresa(db_session: AsyncSession, usuario_gerente: Usuario):
    """Test crear empresa básica"""
    empresa = Empresa(
        ruc="20987654321",
        razon_social="Transportes Puno SAC",
        direccion="Jr. Lima 456, Puno",
        telefono="051234567",
        email="info@transportespuno.com",
        gerente_id=usuario_gerente.id,
        activo=True
    )
    
    db_session.add(empresa)
    await db_session.commit()
    await db_session.refresh(empresa)
    
    assert empresa.id is not None
    assert empresa.ruc == "20987654321"
    assert empresa.razon_social == "Transportes Puno SAC"
    assert empresa.gerente_id == usuario_gerente.id
    assert empresa.activo is True
    assert empresa.created_at is not None


@pytest.mark.asyncio
async def test_empresa_ruc_unico(db_session: AsyncSession, empresa_test: Empresa):
    """Test que el RUC debe ser único"""
    empresa_duplicada = Empresa(
        ruc="20123456789",  # RUC duplicado
        razon_social="Otra Empresa SAC",
        direccion="Otra dirección",
        telefono="999999999",
        email="otro@email.com",
        activo=True
    )
    
    db_session.add(empresa_duplicada)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_empresa_validar_ruc(empresa_test: Empresa):
    """Test validación de RUC"""
    assert empresa_test.validar_ruc() is True
    
    # RUC inválido (menos de 11 dígitos)
    empresa_test.ruc = "123456"
    assert empresa_test.validar_ruc() is False
    
    # RUC inválido (contiene letras)
    empresa_test.ruc = "2012345678A"
    assert empresa_test.validar_ruc() is False


@pytest.mark.asyncio
async def test_empresa_relacion_gerente(
    db_session: AsyncSession,
    empresa_test: Empresa,
    usuario_gerente: Usuario
):
    """Test relación entre empresa y gerente"""
    await db_session.refresh(empresa_test, ["gerente"])
    
    assert empresa_test.gerente is not None
    assert empresa_test.gerente.id == usuario_gerente.id
    assert empresa_test.gerente.rol == RolUsuario.GERENTE


# Tests para AutorizacionEmpresa

@pytest.mark.asyncio
async def test_crear_autorizacion_empresa(
    db_session: AsyncSession,
    empresa_test: Empresa,
    tipo_autorizacion_mercancias: TipoAutorizacion
):
    """Test crear autorización de empresa"""
    autorizacion = AutorizacionEmpresa(
        empresa_id=empresa_test.id,
        tipo_autorizacion_id=tipo_autorizacion_mercancias.id,
        numero_resolucion="RD-001-2024-DRTC-PUNO",
        fecha_emision=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=365),
        vigente=True
    )
    
    db_session.add(autorizacion)
    await db_session.commit()
    await db_session.refresh(autorizacion)
    
    assert autorizacion.id is not None
    assert autorizacion.empresa_id == empresa_test.id
    assert autorizacion.tipo_autorizacion_id == tipo_autorizacion_mercancias.id
    assert autorizacion.vigente is True


@pytest.mark.asyncio
async def test_autorizacion_numero_resolucion_unico(
    db_session: AsyncSession,
    empresa_test: Empresa,
    tipo_autorizacion_mercancias: TipoAutorizacion
):
    """Test que el número de resolución debe ser único"""
    autorizacion1 = AutorizacionEmpresa(
        empresa_id=empresa_test.id,
        tipo_autorizacion_id=tipo_autorizacion_mercancias.id,
        numero_resolucion="RD-002-2024-DRTC-PUNO",
        fecha_emision=date.today(),
        vigente=True
    )
    
    db_session.add(autorizacion1)
    await db_session.commit()
    
    # Crear segunda empresa para evitar conflicto de empresa-tipo
    empresa2 = Empresa(
        ruc="20111111111",
        razon_social="Otra Empresa",
        direccion="Otra dirección",
        telefono="999999999",
        email="otra@email.com",
        activo=True
    )
    db_session.add(empresa2)
    await db_session.commit()
    
    autorizacion2 = AutorizacionEmpresa(
        empresa_id=empresa2.id,
        tipo_autorizacion_id=tipo_autorizacion_mercancias.id,
        numero_resolucion="RD-002-2024-DRTC-PUNO",  # Número duplicado
        fecha_emision=date.today(),
        vigente=True
    )
    
    db_session.add(autorizacion2)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_autorizacion_esta_vencida(db_session: AsyncSession):
    """Test verificar si autorización está vencida"""
    empresa = Empresa(
        ruc="20222222222",
        razon_social="Test Empresa",
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        activo=True
    )
    db_session.add(empresa)
    
    tipo = TipoAutorizacion(
        codigo="TEST",
        nombre="Test",
        descripcion="Test"
    )
    db_session.add(tipo)
    await db_session.commit()
    
    # Autorización vencida
    autorizacion_vencida = AutorizacionEmpresa(
        empresa_id=empresa.id,
        tipo_autorizacion_id=tipo.id,
        numero_resolucion="RD-VENCIDA-2024",
        fecha_emision=date.today() - timedelta(days=400),
        fecha_vencimiento=date.today() - timedelta(days=1),
        vigente=True
    )
    
    assert autorizacion_vencida.esta_vencida is True
    
    # Autorización vigente
    autorizacion_vigente = AutorizacionEmpresa(
        empresa_id=empresa.id,
        tipo_autorizacion_id=tipo.id,
        numero_resolucion="RD-VIGENTE-2024",
        fecha_emision=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=365),
        vigente=True
    )
    
    assert autorizacion_vigente.esta_vencida is False
    
    # Autorización sin vencimiento
    autorizacion_sin_vencimiento = AutorizacionEmpresa(
        empresa_id=empresa.id,
        tipo_autorizacion_id=tipo.id,
        numero_resolucion="RD-SINVENC-2024",
        fecha_emision=date.today(),
        fecha_vencimiento=None,
        vigente=True
    )
    
    assert autorizacion_sin_vencimiento.esta_vencida is False


@pytest.mark.asyncio
async def test_autorizacion_actualizar_vigencia(db_session: AsyncSession):
    """Test actualizar vigencia de autorización"""
    empresa = Empresa(
        ruc="20333333333",
        razon_social="Test Empresa",
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        activo=True
    )
    db_session.add(empresa)
    
    tipo = TipoAutorizacion(
        codigo="TEST2",
        nombre="Test",
        descripcion="Test"
    )
    db_session.add(tipo)
    await db_session.commit()
    
    autorizacion = AutorizacionEmpresa(
        empresa_id=empresa.id,
        tipo_autorizacion_id=tipo.id,
        numero_resolucion="RD-UPDATE-2024",
        fecha_emision=date.today() - timedelta(days=400),
        fecha_vencimiento=date.today() - timedelta(days=1),
        vigente=True
    )
    
    db_session.add(autorizacion)
    await db_session.commit()
    
    # Actualizar vigencia
    autorizacion.actualizar_vigencia()
    
    assert autorizacion.vigente is False


@pytest.mark.asyncio
async def test_empresa_tiene_autorizaciones_vigentes(
    db_session: AsyncSession,
    empresa_test: Empresa,
    tipo_autorizacion_mercancias: TipoAutorizacion
):
    """Test verificar si empresa tiene autorizaciones vigentes"""
    # Inicialmente sin autorizaciones
    await db_session.refresh(empresa_test, ["autorizaciones"])
    assert empresa_test.tiene_autorizaciones_vigentes is False
    
    # Agregar autorización vigente
    autorizacion = AutorizacionEmpresa(
        empresa_id=empresa_test.id,
        tipo_autorizacion_id=tipo_autorizacion_mercancias.id,
        numero_resolucion="RD-003-2024-DRTC-PUNO",
        fecha_emision=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=365),
        vigente=True
    )
    
    db_session.add(autorizacion)
    await db_session.commit()
    await db_session.refresh(empresa_test, ["autorizaciones"])
    
    assert empresa_test.tiene_autorizaciones_vigentes is True


@pytest.mark.asyncio
async def test_empresa_tiene_autorizacion_especifica(
    db_session: AsyncSession,
    empresa_test: Empresa,
    tipo_autorizacion_mercancias: TipoAutorizacion,
    tipo_autorizacion_turismo: TipoAutorizacion
):
    """Test verificar si empresa tiene tipo específico de autorización"""
    # Agregar autorización de mercancías
    autorizacion = AutorizacionEmpresa(
        empresa_id=empresa_test.id,
        tipo_autorizacion_id=tipo_autorizacion_mercancias.id,
        numero_resolucion="RD-004-2024-DRTC-PUNO",
        fecha_emision=date.today(),
        vigente=True
    )
    
    db_session.add(autorizacion)
    await db_session.commit()
    await db_session.refresh(empresa_test, ["autorizaciones"])
    
    # Cargar relaciones necesarias
    for auth in empresa_test.autorizaciones:
        await db_session.refresh(auth, ["tipo_autorizacion"])
    
    assert empresa_test.tiene_autorizacion("MERCANCIAS") is True
    assert empresa_test.tiene_autorizacion("TURISMO") is False


@pytest.mark.asyncio
async def test_empresa_multiples_autorizaciones(
    db_session: AsyncSession,
    empresa_test: Empresa,
    tipo_autorizacion_mercancias: TipoAutorizacion,
    tipo_autorizacion_turismo: TipoAutorizacion
):
    """Test empresa con múltiples tipos de autorización"""
    # Agregar autorización de mercancías
    auth1 = AutorizacionEmpresa(
        empresa_id=empresa_test.id,
        tipo_autorizacion_id=tipo_autorizacion_mercancias.id,
        numero_resolucion="RD-005-2024-DRTC-PUNO",
        fecha_emision=date.today(),
        vigente=True
    )
    
    # Agregar autorización de turismo
    auth2 = AutorizacionEmpresa(
        empresa_id=empresa_test.id,
        tipo_autorizacion_id=tipo_autorizacion_turismo.id,
        numero_resolucion="RD-006-2024-DRTC-PUNO",
        fecha_emision=date.today(),
        vigente=True
    )
    
    db_session.add(auth1)
    db_session.add(auth2)
    await db_session.commit()
    await db_session.refresh(empresa_test, ["autorizaciones"])
    
    assert len(empresa_test.autorizaciones) == 2


@pytest.mark.asyncio
async def test_buscar_empresas_activas(db_session: AsyncSession):
    """Test buscar empresas activas"""
    # Crear empresas activas e inactivas
    empresa_activa = Empresa(
        ruc="20444444444",
        razon_social="Empresa Activa",
        direccion="Test",
        telefono="999999999",
        email="activa@test.com",
        activo=True
    )
    
    empresa_inactiva = Empresa(
        ruc="20555555555",
        razon_social="Empresa Inactiva",
        direccion="Test",
        telefono="999999999",
        email="inactiva@test.com",
        activo=False
    )
    
    db_session.add(empresa_activa)
    db_session.add(empresa_inactiva)
    await db_session.commit()
    
    # Buscar solo activas
    result = await db_session.execute(
        select(Empresa).where(Empresa.activo == True)
    )
    empresas_activas = result.scalars().all()
    
    assert len(empresas_activas) >= 1
    assert all(e.activo for e in empresas_activas)
