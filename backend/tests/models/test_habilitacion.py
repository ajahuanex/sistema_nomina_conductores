"""
Tests para modelos de Habilitación y Pago
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habilitacion import (
    Habilitacion, Pago, ConceptoTUPA,
    EstadoHabilitacion, EstadoPago
)
from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa
from app.models.user import Usuario, RolUsuario


@pytest.fixture
async def concepto_tupa_habilitacion(db_session: AsyncSession) -> ConceptoTUPA:
    """Fixture para concepto TUPA de habilitación"""
    concepto = ConceptoTUPA(
        codigo="HAB-CONDUCTOR",
        descripcion="Habilitación de Conductor",
        monto=Decimal("150.00"),
        vigencia_desde=date.today() - timedelta(days=30),
        vigencia_hasta=None,  # Vigente indefinidamente
        activo=True
    )
    db_session.add(concepto)
    await db_session.commit()
    await db_session.refresh(concepto)
    return concepto


@pytest.fixture
async def conductor_para_habilitacion(db_session: AsyncSession) -> Conductor:
    """Fixture para conductor que solicita habilitación"""
    empresa = Empresa(
        ruc="20123456789",
        razon_social="Test SAC",
        direccion="Test",
        telefono="999999999",
        email="test@test.com",
        activo=True
    )
    db_session.add(empresa)
    await db_session.commit()
    
    conductor = Conductor(
        dni="12345678",
        nombres="Juan",
        apellidos="Pérez",
        fecha_nacimiento=date(1990, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="juan@test.com",
        licencia_numero="Q12345678",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today() - timedelta(days=100),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=empresa.id,
        estado=EstadoConductor.PENDIENTE
    )
    db_session.add(conductor)
    await db_session.commit()
    await db_session.refresh(conductor)
    return conductor


@pytest.fixture
async def habilitacion_test(
    db_session: AsyncSession,
    conductor_para_habilitacion: Conductor
) -> Habilitacion:
    """Fixture para habilitación de prueba"""
    habilitacion = Habilitacion(
        conductor_id=conductor_para_habilitacion.id,
        codigo_habilitacion="HAB-20240101-TEST1234",
        estado=EstadoHabilitacion.PENDIENTE
    )
    db_session.add(habilitacion)
    await db_session.commit()
    await db_session.refresh(habilitacion)
    return habilitacion


# Tests para ConceptoTUPA

@pytest.mark.asyncio
async def test_crear_concepto_tupa(db_session: AsyncSession):
    """Test crear concepto TUPA"""
    concepto = ConceptoTUPA(
        codigo="RENOVACION",
        descripcion="Renovación de Habilitación",
        monto=Decimal("100.00"),
        vigencia_desde=date.today(),
        activo=True
    )
    
    db_session.add(concepto)
    await db_session.commit()
    await db_session.refresh(concepto)
    
    assert concepto.id is not None
    assert concepto.codigo == "RENOVACION"
    assert concepto.monto == Decimal("100.00")
    assert concepto.activo is True


@pytest.mark.asyncio
async def test_concepto_tupa_esta_vigente(concepto_tupa_habilitacion: ConceptoTUPA):
    """Test verificar vigencia de concepto TUPA"""
    assert concepto_tupa_habilitacion.esta_vigente is True
    
    # Desactivar
    concepto_tupa_habilitacion.activo = False
    assert concepto_tupa_habilitacion.esta_vigente is False
    
    # Reactivar pero con vigencia futura
    concepto_tupa_habilitacion.activo = True
    concepto_tupa_habilitacion.vigencia_desde = date.today() + timedelta(days=10)
    assert concepto_tupa_habilitacion.esta_vigente is False
    
    # Vigencia vencida
    concepto_tupa_habilitacion.vigencia_desde = date.today() - timedelta(days=100)
    concepto_tupa_habilitacion.vigencia_hasta = date.today() - timedelta(days=1)
    assert concepto_tupa_habilitacion.esta_vigente is False


@pytest.mark.asyncio
async def test_concepto_tupa_codigo_unico(
    db_session: AsyncSession,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test que código de concepto TUPA debe ser único"""
    concepto_duplicado = ConceptoTUPA(
        codigo="HAB-CONDUCTOR",  # Código duplicado
        descripcion="Otro",
        monto=Decimal("200.00"),
        vigencia_desde=date.today(),
        activo=True
    )
    
    db_session.add(concepto_duplicado)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


# Tests para Habilitacion

@pytest.mark.asyncio
async def test_crear_habilitacion(
    db_session: AsyncSession,
    conductor_para_habilitacion: Conductor
):
    """Test crear habilitación"""
    habilitacion = Habilitacion(
        conductor_id=conductor_para_habilitacion.id,
        codigo_habilitacion="HAB-20240101-ABCD1234",
        estado=EstadoHabilitacion.PENDIENTE
    )
    
    db_session.add(habilitacion)
    await db_session.commit()
    await db_session.refresh(habilitacion)
    
    assert habilitacion.id is not None
    assert habilitacion.conductor_id == conductor_para_habilitacion.id
    assert habilitacion.estado == EstadoHabilitacion.PENDIENTE
    assert habilitacion.fecha_solicitud is not None


@pytest.mark.asyncio
async def test_habilitacion_codigo_unico(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion
):
    """Test que código de habilitación debe ser único"""
    habilitacion_duplicada = Habilitacion(
        conductor_id=habilitacion_test.conductor_id,
        codigo_habilitacion="HAB-20240101-TEST1234",  # Código duplicado
        estado=EstadoHabilitacion.PENDIENTE
    )
    
    db_session.add(habilitacion_duplicada)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_habilitacion_esta_vigente(habilitacion_test: Habilitacion):
    """Test verificar vigencia de habilitación"""
    # Pendiente, no vigente
    assert habilitacion_test.esta_vigente is False
    
    # Habilitada sin fecha de vencimiento
    habilitacion_test.estado = EstadoHabilitacion.HABILITADO
    habilitacion_test.vigencia_hasta = None
    assert habilitacion_test.esta_vigente is True
    
    # Habilitada con vigencia futura
    habilitacion_test.vigencia_hasta = date.today() + timedelta(days=365)
    assert habilitacion_test.esta_vigente is True
    
    # Habilitada pero vencida
    habilitacion_test.vigencia_hasta = date.today() - timedelta(days=1)
    assert habilitacion_test.esta_vigente is False


@pytest.mark.asyncio
async def test_habilitacion_pago_confirmado(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test verificar si pago está confirmado"""
    # Sin pago
    await db_session.refresh(habilitacion_test, ["pago"])
    assert habilitacion_test.pago_confirmado is False
    
    # Con pago pendiente
    pago = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-001",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    db_session.add(pago)
    await db_session.commit()
    await db_session.refresh(habilitacion_test, ["pago"])
    
    assert habilitacion_test.pago_confirmado is False
    
    # Con pago confirmado
    pago.estado = EstadoPago.CONFIRMADO
    await db_session.commit()
    await db_session.refresh(habilitacion_test, ["pago"])
    
    assert habilitacion_test.pago_confirmado is True


@pytest.mark.asyncio
async def test_habilitacion_puede_aprobar(habilitacion_test: Habilitacion):
    """Test verificar si habilitación puede ser aprobada"""
    # Pendiente, no puede aprobar
    assert habilitacion_test.puede_aprobar() is False
    
    # En revisión, puede aprobar
    habilitacion_test.estado = EstadoHabilitacion.EN_REVISION
    assert habilitacion_test.puede_aprobar() is True
    
    # Aprobada, no puede aprobar de nuevo
    habilitacion_test.estado = EstadoHabilitacion.APROBADO
    assert habilitacion_test.puede_aprobar() is False


@pytest.mark.asyncio
async def test_habilitacion_puede_habilitar(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test verificar si habilitación puede ser otorgada"""
    # Pendiente, no puede habilitar
    assert habilitacion_test.puede_habilitar() is False
    
    # Aprobada pero sin pago
    habilitacion_test.estado = EstadoHabilitacion.APROBADO
    await db_session.refresh(habilitacion_test, ["pago"])
    assert habilitacion_test.puede_habilitar() is False
    
    # Aprobada con pago confirmado
    pago = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-002",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.CONFIRMADO
    )
    db_session.add(pago)
    await db_session.commit()
    await db_session.refresh(habilitacion_test, ["pago"])
    
    assert habilitacion_test.puede_habilitar() is True


@pytest.mark.asyncio
async def test_habilitacion_generar_codigo(habilitacion_test: Habilitacion):
    """Test generar código de habilitación"""
    codigo = habilitacion_test.generar_codigo_habilitacion()
    
    assert codigo.startswith("HAB-")
    assert len(codigo) > 20
    
    # Con prefijo personalizado
    codigo_custom = habilitacion_test.generar_codigo_habilitacion(prefijo="DRTC")
    assert codigo_custom.startswith("DRTC-")


@pytest.mark.asyncio
async def test_habilitacion_dias_hasta_vencimiento(habilitacion_test: Habilitacion):
    """Test calcular días hasta vencimiento"""
    # Sin vencimiento
    assert habilitacion_test.dias_hasta_vencimiento == 999999
    
    # Con vencimiento
    habilitacion_test.vigencia_hasta = date.today() + timedelta(days=100)
    assert habilitacion_test.dias_hasta_vencimiento == 100


# Tests para Pago

@pytest.mark.asyncio
async def test_crear_pago(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test crear pago"""
    pago = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-003",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    
    db_session.add(pago)
    await db_session.commit()
    await db_session.refresh(pago)
    
    assert pago.id is not None
    assert pago.numero_recibo == "REC-003"
    assert pago.monto == Decimal("150.00")
    assert pago.estado == EstadoPago.PENDIENTE


@pytest.mark.asyncio
async def test_pago_numero_recibo_unico(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test que número de recibo debe ser único"""
    pago1 = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-004",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    db_session.add(pago1)
    await db_session.commit()
    
    # Crear otra habilitación para el segundo pago
    conductor2 = Conductor(
        dni="87654321",
        nombres="María",
        apellidos="García",
        fecha_nacimiento=date(1992, 1, 1),
        direccion="Test",
        telefono="999999999",
        email="maria@test.com",
        licencia_numero="Q87654321",
        licencia_categoria="A-IIIb",
        licencia_emision=date.today(),
        licencia_vencimiento=date.today() + timedelta(days=365),
        empresa_id=habilitacion_test.conductor.empresa_id,
        estado=EstadoConductor.PENDIENTE
    )
    db_session.add(conductor2)
    await db_session.commit()
    
    habilitacion2 = Habilitacion(
        conductor_id=conductor2.id,
        codigo_habilitacion="HAB-20240102-TEST5678",
        estado=EstadoHabilitacion.PENDIENTE
    )
    db_session.add(habilitacion2)
    await db_session.commit()
    
    pago2 = Pago(
        habilitacion_id=habilitacion2.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-004",  # Número duplicado
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    
    db_session.add(pago2)
    
    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_pago_validar_monto(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test validar monto de pago"""
    pago = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-005",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    
    # Monto correcto
    assert pago.validar_monto(Decimal("150.00")) is True
    
    # Monto incorrecto
    assert pago.validar_monto(Decimal("100.00")) is False
    
    # Diferencia mínima aceptable
    assert pago.validar_monto(Decimal("150.005")) is True


@pytest.mark.asyncio
async def test_pago_confirmar(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA,
    usuario_superusuario: Usuario
):
    """Test confirmar pago"""
    pago = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-006",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    
    db_session.add(pago)
    await db_session.commit()
    
    assert pago.estado == EstadoPago.PENDIENTE
    assert pago.fecha_confirmacion is None
    
    # Confirmar pago
    pago.confirmar_pago(usuario_superusuario.id)
    await db_session.commit()
    
    assert pago.estado == EstadoPago.CONFIRMADO
    assert pago.fecha_confirmacion is not None
    assert pago.confirmado_por == usuario_superusuario.id


@pytest.mark.asyncio
async def test_pago_rechazar(
    db_session: AsyncSession,
    habilitacion_test: Habilitacion,
    concepto_tupa_habilitacion: ConceptoTUPA
):
    """Test rechazar pago"""
    pago = Pago(
        habilitacion_id=habilitacion_test.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-007",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE
    )
    
    db_session.add(pago)
    await db_session.commit()
    
    # Rechazar pago
    pago.rechazar_pago("Monto incorrecto")
    await db_session.commit()
    
    assert pago.estado == EstadoPago.RECHAZADO
    assert "Monto incorrecto" in pago.observaciones


# Tests de flujo completo

@pytest.mark.asyncio
async def test_flujo_completo_habilitacion(
    db_session: AsyncSession,
    conductor_para_habilitacion: Conductor,
    concepto_tupa_habilitacion: ConceptoTUPA,
    usuario_superusuario: Usuario
):
    """Test flujo completo de habilitación"""
    # 1. Crear solicitud
    habilitacion = Habilitacion(
        conductor_id=conductor_para_habilitacion.id,
        codigo_habilitacion="HAB-FLUJO-TEST",
        estado=EstadoHabilitacion.PENDIENTE
    )
    db_session.add(habilitacion)
    await db_session.commit()
    
    assert habilitacion.estado == EstadoHabilitacion.PENDIENTE
    
    # 2. Poner en revisión
    habilitacion.estado = EstadoHabilitacion.EN_REVISION
    habilitacion.revisado_por = usuario_superusuario.id
    habilitacion.fecha_revision = datetime.utcnow()
    await db_session.commit()
    
    assert habilitacion.puede_aprobar() is True
    
    # 3. Aprobar
    habilitacion.estado = EstadoHabilitacion.APROBADO
    habilitacion.aprobado_por = usuario_superusuario.id
    habilitacion.fecha_aprobacion = datetime.utcnow()
    await db_session.commit()
    
    # 4. Registrar pago
    pago = Pago(
        habilitacion_id=habilitacion.id,
        concepto_tupa_id=concepto_tupa_habilitacion.id,
        numero_recibo="REC-FLUJO-001",
        monto=Decimal("150.00"),
        fecha_pago=date.today(),
        entidad_bancaria="BCP",
        estado=EstadoPago.PENDIENTE,
        registrado_por=usuario_superusuario.id
    )
    db_session.add(pago)
    await db_session.commit()
    
    # 5. Confirmar pago
    pago.confirmar_pago(usuario_superusuario.id)
    await db_session.commit()
    await db_session.refresh(habilitacion, ["pago"])
    
    assert habilitacion.puede_habilitar() is True
    
    # 6. Habilitar conductor
    habilitacion.estado = EstadoHabilitacion.HABILITADO
    habilitacion.habilitado_por = usuario_superusuario.id
    habilitacion.fecha_habilitacion = datetime.utcnow()
    habilitacion.vigencia_hasta = date.today() + timedelta(days=365)
    await db_session.commit()
    
    assert habilitacion.esta_vigente is True
    assert habilitacion.estado == EstadoHabilitacion.HABILITADO
