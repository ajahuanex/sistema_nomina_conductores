"""
Tests para modelo de Conductor
"""
import pytest
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa, TipoAutorizacion, AutorizacionEmpresa


@pytest.fixture
async def empresa_con_autorizacion(db_session: AsyncSession) -> Empresa:
    """Fixture para empresa con autorización de mercancías"""
    empresa = Empresa(
        ruc="20123456789",
        razon_social="Transportes Test SAC",
        direccion="Av. Test 123",
        telefono="987654321",
        email="test@test.com",
        activo=True
    )
    db_session.add(empresa)
    
    tipo_auth = TipoAutorizacion(
        codigo="MERCANCIAS",
        nombre="Transporte de Mercancías",
        descripcion="Test"
    )
    db_session.add(tipo_auth)
    await db_session.commit()
    
    autorizacion = AutorizacionEmpresa(
        empresa_id=empresa.id,
        tipo_autorizacion_id=tipo_auth.id,
        numero_resolucion="RD-001-2024",
        fecha_emision=date.today(),
        vigente=True
    )
    db_session.add(autorizacion)
    await db_session.commit()
    await db_session.refresh(empresa)
    
    return empresa


@pytest.fixture
async def conductor_test(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
) -> Conductor:
    """Fixture para conductor de prueba"""
    conductor = Conductor(
        dni="12345678",
        nombres="Juan Carlos",
        apellidos="Pérez López",
        fecha_nacimiento=date(1990, 5, 15),
        direccion="Jr. Lima 123, Puno",
        telefono="987654321",
        email="juan.perez@email.com",
        licencia_numero="Q12345678",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today() - timedelta(days=365),
        licencia_vencimiento=date.today() + timedelta(days=365),
        certificado_medico_numero="CM-2024-001",
        certificado_medico_vencimiento=date.today() + timedelta(days=180),
        empresa_id=empresa_con_autorizacion.id,
        estado=EstadoConductor.PENDIENTE
    )
    db_session.add(conductor)
    await db_session.commit()
    await db_session.refresh(conductor)
    return conductor


# Tests de creación y validación básica

@pytest.mark.asyncio
async def test_crear_conductor(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
):
    """Test crear conductor básico"""
    conductor = Conductor(
        dni="87654321",
        nombres="María",
        apellidos="García",
        fecha_nacimiento=date(1985, 3, 20),
        direccion="Av. Principal 456",
        telefono="951234567",
        email="maria.garcia@email.com",
        licencia_numero="Q87654321",
        licencia_categoria="A-IIb",
        licencia_emision=date.today() - timedelta(days=200),
        licencia_vencimiento=date.today() + timedelta(days=500),
        empresa_id=empresa_con_autorizacion.id
    )
    
    db_session.add(conductor)
    await db_session.commit()
    await db_session.refresh(conductor)
    
    assert conductor.id is not None
    assert conductor.dni == "87654321"
    assert conductor.nombre_completo == "María García"
    assert conductor.estado == EstadoConductor.PENDIENTE
    assert conductor.created_at is not None


# Tests de validación de DNI

@pytest.mark.asyncio
async def test_validar_dni_8_digitos(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
):
    """Test que DNI debe tener 8 dígitos"""
    conductor = Conductor(
        dni="123",  # DNI inválido
        nombres="Test",
        apellidos="Test",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        licencia_numero="Q11111111",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=empresa_con_autorizacion.id
    )
    
    with pytest.raises(ValueError, match="DNI debe tener exactamente 8 dígitos"):
        db_session.add(conductor)
        await db_session.flush()


@pytest.mark.asyncio
async def test_validar_dni_solo_numeros(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
):
    """Test que DNI debe contener solo números"""
    conductor = Conductor(
        dni="1234567A",  # DNI con letra
        nombres="Test",
        apellidos="Test",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        licencia_numero="Q22222222",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=empresa_con_autorizacion.id
    )
    
    with pytest.raises(ValueError, match="DNI debe tener exactamente 8 dígitos"):
        db_session.add(conductor)
        await db_session.flush()


@pytest.mark.asyncio
async def test_dni_unico(db_session: AsyncSession, conductor_test: Conductor):
    """Test que DNI debe ser único"""
    conductor_duplicado = Conductor(
        dni="12345678",  # DNI duplicado
        nombres="Otro",
        apellidos="Conductor",
        fecha_nacimiento=date(1992, 1, 1),
        direccion="Otra dirección",
        telefono="999999999",
        email="otro@test.com",
        licencia_numero="Q99999999",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=conductor_test.empresa_id
    )
    
    db_session.add(conductor_duplicado)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


# Tests de validación de licencia

@pytest.mark.asyncio
async def test_validar_categoria_licencia(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
):
    """Test validación de categoría de licencia"""
    conductor = Conductor(
        dni="11111111",
        nombres="Test",
        apellidos="Test",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        licencia_numero="Q33333333",
        licencia_categoria="INVALIDA",  # Categoría inválida
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=empresa_con_autorizacion.id
    )
    
    with pytest.raises(ValueError, match="Categoría de licencia inválida"):
        db_session.add(conductor)
        await db_session.flush()


@pytest.mark.asyncio
async def test_licencia_no_vencida(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
):
    """Test que licencia no debe estar vencida"""
    conductor = Conductor(
        dni="22222222",
        nombres="Test",
        apellidos="Test",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        licencia_numero="Q44444444",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today() - timedelta(days=400),
        licencia_vencimiento=date.today() - timedelta(days=1),  # Vencida
        empresa_id=empresa_con_autorizacion.id
    )
    
    with pytest.raises(ValueError, match="La licencia de conducir está vencida"):
        db_session.add(conductor)
        await db_session.flush()


@pytest.mark.asyncio
async def test_licencia_numero_unico(
    db_session: AsyncSession,
    conductor_test: Conductor
):
    """Test que número de licencia debe ser único"""
    conductor_duplicado = Conductor(
        dni="33333333",
        nombres="Otro",
        apellidos="Conductor",
        fecha_nacimiento=date(1992, 1, 1),
        direccion="Otra dirección",
        telefono="999999999",
        email="otro2@test.com",
        licencia_numero="Q12345678",  # Licencia duplicada
        licencia_categoria="A-IIIb",
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=conductor_test.empresa_id
    )
    
    db_session.add(conductor_duplicado)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


# Tests de propiedades

@pytest.mark.asyncio
async def test_nombre_completo(conductor_test: Conductor):
    """Test propiedad nombre_completo"""
    assert conductor_test.nombre_completo == "Juan Carlos Pérez López"


@pytest.mark.asyncio
async def test_licencia_vigente(conductor_test: Conductor):
    """Test propiedad licencia_vigente"""
    assert conductor_test.licencia_vigente is True
    
    # Cambiar a licencia vencida
    conductor_test.licencia_vencimiento = date.today() - timedelta(days=1)
    assert conductor_test.licencia_vigente is False


@pytest.mark.asyncio
async def test_certificado_medico_vigente(conductor_test: Conductor):
    """Test propiedad certificado_medico_vigente"""
    assert conductor_test.certificado_medico_vigente is True
    
    # Cambiar a certificado vencido
    conductor_test.certificado_medico_vencimiento = date.today() - timedelta(days=1)
    assert conductor_test.certificado_medico_vigente is False
    
    # Sin certificado
    conductor_test.certificado_medico_vencimiento = None
    assert conductor_test.certificado_medico_vigente is False


@pytest.mark.asyncio
async def test_edad(conductor_test: Conductor):
    """Test cálculo de edad"""
    # Conductor nacido en 1990
    edad_esperada = date.today().year - 1990
    if (date.today().month, date.today().day) < (5, 15):
        edad_esperada -= 1
    
    assert conductor_test.edad == edad_esperada


@pytest.mark.asyncio
async def test_puede_operar(conductor_test: Conductor):
    """Test propiedad puede_operar"""
    # Inicialmente pendiente, no puede operar
    assert conductor_test.puede_operar is False
    
    # Habilitar conductor
    conductor_test.estado = EstadoConductor.HABILITADO
    assert conductor_test.puede_operar is True
    
    # Licencia vencida
    conductor_test.licencia_vencimiento = date.today() - timedelta(days=1)
    assert conductor_test.puede_operar is False
    
    # Restaurar licencia, vencer certificado
    conductor_test.licencia_vencimiento = date.today() + timedelta(days=365)
    conductor_test.certificado_medico_vencimiento = date.today() - timedelta(days=1)
    assert conductor_test.puede_operar is False


# Tests de métodos

@pytest.mark.asyncio
async def test_validar_categoria_para_tipo_autorizacion(conductor_test: Conductor):
    """Test validación de categoría para tipo de autorización"""
    # Conductor con A-IIIb puede transportar mercancías
    assert conductor_test.validar_categoria_para_tipo_autorizacion("MERCANCIAS") is True
    
    # Conductor con A-IIIb puede hacer turismo
    assert conductor_test.validar_categoria_para_tipo_autorizacion("TURISMO") is True
    
    # Cambiar a categoría menor
    conductor_test.licencia_categoria = "A-I"
    assert conductor_test.validar_categoria_para_tipo_autorizacion("MERCANCIAS") is False


@pytest.mark.asyncio
async def test_dias_hasta_vencimiento_licencia(conductor_test: Conductor):
    """Test cálculo de días hasta vencimiento de licencia"""
    dias = conductor_test.dias_hasta_vencimiento_licencia()
    assert dias > 0
    assert dias <= 365


@pytest.mark.asyncio
async def test_dias_hasta_vencimiento_certificado(conductor_test: Conductor):
    """Test cálculo de días hasta vencimiento de certificado"""
    dias = conductor_test.dias_hasta_vencimiento_certificado()
    assert dias > 0
    assert dias <= 180


@pytest.mark.asyncio
async def test_requiere_renovacion_documentos(conductor_test: Conductor):
    """Test verificación de renovación de documentos"""
    # Documentos vigentes por mucho tiempo
    alertas = conductor_test.requiere_renovacion_documentos(dias_anticipacion=30)
    assert alertas['licencia'] is False
    assert alertas['certificado_medico'] is False
    
    # Licencia próxima a vencer
    conductor_test.licencia_vencimiento = date.today() + timedelta(days=20)
    alertas = conductor_test.requiere_renovacion_documentos(dias_anticipacion=30)
    assert alertas['licencia'] is True
    
    # Certificado próximo a vencer
    conductor_test.certificado_medico_vencimiento = date.today() + timedelta(days=15)
    alertas = conductor_test.requiere_renovacion_documentos(dias_anticipacion=30)
    assert alertas['certificado_medico'] is True


@pytest.mark.asyncio
async def test_cambiar_estado(conductor_test: Conductor):
    """Test cambio de estado del conductor"""
    assert conductor_test.estado == EstadoConductor.PENDIENTE
    assert conductor_test.observaciones is None
    
    # Cambiar a habilitado
    conductor_test.cambiar_estado(
        EstadoConductor.HABILITADO,
        "Documentos verificados y aprobados"
    )
    
    assert conductor_test.estado == EstadoConductor.HABILITADO
    assert "Documentos verificados" in conductor_test.observaciones
    
    # Cambiar a suspendido
    conductor_test.cambiar_estado(
        EstadoConductor.SUSPENDIDO,
        "Infracción grave detectada"
    )
    
    assert conductor_test.estado == EstadoConductor.SUSPENDIDO
    assert "Infracción grave" in conductor_test.observaciones


# Tests de búsqueda y filtrado

@pytest.mark.asyncio
async def test_buscar_por_dni(db_session: AsyncSession, conductor_test: Conductor):
    """Test buscar conductor por DNI"""
    result = await db_session.execute(
        select(Conductor).where(Conductor.dni == "12345678")
    )
    conductor = result.scalar_one_or_none()
    
    assert conductor is not None
    assert conductor.dni == "12345678"
    assert conductor.id == conductor_test.id


@pytest.mark.asyncio
async def test_buscar_por_licencia(db_session: AsyncSession, conductor_test: Conductor):
    """Test buscar conductor por número de licencia"""
    result = await db_session.execute(
        select(Conductor).where(Conductor.licencia_numero == "Q12345678")
    )
    conductor = result.scalar_one_or_none()
    
    assert conductor is not None
    assert conductor.licencia_numero == "Q12345678"


@pytest.mark.asyncio
async def test_filtrar_por_estado(db_session: AsyncSession):
    """Test filtrar conductores por estado"""
    # Crear conductores con diferentes estados
    empresa = Empresa(
        ruc="20999999999",
        razon_social="Test",
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        activo=True
    )
    db_session.add(empresa)
    await db_session.commit()
    
    conductores = []
    for i, estado in enumerate([EstadoConductor.PENDIENTE, EstadoConductor.HABILITADO, EstadoConductor.SUSPENDIDO]):
        conductor = Conductor(
            dni=f"4444444{i}",
            nombres=f"Conductor{i}",
            apellidos="Test",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Test",
            telefono="999999999",
            email=f"test{i}@test.com",
            licencia_numero=f"Q5555555{i}",
            licencia_categoria="A-IIIb",
            licencia_emision=date.today(),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=empresa.id,
            estado=estado
        )
        conductores.append(conductor)
        db_session.add(conductor)
    
    await db_session.commit()
    
    # Buscar solo habilitados
    result = await db_session.execute(
        select(Conductor).where(Conductor.estado == EstadoConductor.HABILITADO)
    )
    habilitados = result.scalars().all()
    
    assert len(habilitados) >= 1
    assert all(c.estado == EstadoConductor.HABILITADO for c in habilitados)


@pytest.mark.asyncio
async def test_filtrar_por_empresa(
    db_session: AsyncSession,
    conductor_test: Conductor,
    empresa_con_autorizacion: Empresa
):
    """Test filtrar conductores por empresa"""
    result = await db_session.execute(
        select(Conductor).where(Conductor.empresa_id == empresa_con_autorizacion.id)
    )
    conductores = result.scalars().all()
    
    assert len(conductores) >= 1
    assert all(c.empresa_id == empresa_con_autorizacion.id for c in conductores)


@pytest.mark.asyncio
async def test_validar_email(
    db_session: AsyncSession,
    empresa_con_autorizacion: Empresa
):
    """Test validación básica de email"""
    conductor = Conductor(
        dni="55555555",
        nombres="Test",
        apellidos="Test",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="email_invalido",  # Sin @
        licencia_numero="Q66666666",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=empresa_con_autorizacion.id
    )
    
    with pytest.raises(ValueError, match="Email inválido"):
        db_session.add(conductor)
        await db_session.flush()
