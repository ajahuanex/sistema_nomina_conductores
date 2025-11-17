"""
Tests para PagoService
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from app.services.pago_service import PagoService
from app.models.habilitacion import EstadoPago, EstadoHabilitacion
from app.schemas.pago import PagoCreate
from app.core.exceptions import RecursoNoEncontrado, ValidacionError


@pytest.mark.asyncio
class TestPagoService:
    """Tests para PagoService"""
    
    async def test_calcular_monto_tupa_exitoso(self, db_session, concepto_tupa_factory):
        """Test calcular monto TUPA con concepto vigente"""
        # Arrange
        concepto = await concepto_tupa_factory.create(
            codigo="HAB-CONDUCTOR",
            monto=Decimal("50.00"),
            vigencia_desde=date.today() - timedelta(days=30),
            vigencia_hasta=None,
            activo=True
        )
        service = PagoService(db_session)
        
        # Act
        monto = await service.calcular_monto_tupa("HAB-CONDUCTOR")
        
        # Assert
        assert monto == Decimal("50.00")
    
    async def test_calcular_monto_tupa_concepto_no_vigente(self, db_session, concepto_tupa_factory):
        """Test calcular monto TUPA con concepto no vigente"""
        # Arrange
        await concepto_tupa_factory.create(
            codigo="HAB-CONDUCTOR",
            monto=Decimal("50.00"),
            vigencia_desde=date.today() + timedelta(days=30),
            vigencia_hasta=None,
            activo=True
        )
        service = PagoService(db_session)
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado) as exc:
            await service.calcular_monto_tupa("HAB-CONDUCTOR")
        
        assert "ConceptoTUPA" in str(exc.value)
    
    async def test_generar_orden_pago_exitoso(
        self,
        db_session,
        habilitacion_factory,
        conductor_factory,
        empresa_factory,
        concepto_tupa_factory
    ):
        """Test generar orden de pago exitosamente"""
        # Arrange
        empresa = await empresa_factory.create()
        conductor = await conductor_factory.create(empresa_id=empresa.id)
        habilitacion = await habilitacion_factory.create(
            conductor_id=conductor.id,
            estado=EstadoHabilitacion.APROBADO
        )
        concepto = await concepto_tupa_factory.create(
            codigo="HAB-CONDUCTOR",
            monto=Decimal("50.00"),
            vigencia_desde=date.today(),
            activo=True
        )
        service = PagoService(db_session)
        
        # Act
        orden = await service.generar_orden_pago(habilitacion.id)
        
        # Assert
        assert orden.habilitacion_id == str(habilitacion.id)
        assert orden.codigo_habilitacion == habilitacion.codigo_habilitacion
        assert orden.conductor_dni == conductor.dni
        assert orden.empresa_ruc == empresa.ruc
        assert orden.monto_total == Decimal("50.00")
        assert "OP-" in orden.codigo_orden
    
    async def test_generar_orden_pago_habilitacion_no_existe(self, db_session):
        """Test generar orden de pago con habilitación inexistente"""
        # Arrange
        service = PagoService(db_session)
        habilitacion_id = uuid4()
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado) as exc:
            await service.generar_orden_pago(habilitacion_id)
        
        assert "Habilitacion" in str(exc.value)
    
    async def test_generar_orden_pago_ya_existe_pago(
        self,
        db_session,
        habilitacion_factory,
        conductor_factory,
        empresa_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test generar orden de pago cuando ya existe un pago"""
        # Arrange
        empresa = await empresa_factory.create()
        conductor = await conductor_factory.create(empresa_id=empresa.id)
        habilitacion = await habilitacion_factory.create(conductor_id=conductor.id)
        concepto = await concepto_tupa_factory.create(codigo="HAB-CONDUCTOR")
        await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id
        )
        service = PagoService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.generar_orden_pago(habilitacion.id)
        
        assert "Ya existe un pago" in str(exc.value)
    
    async def test_registrar_pago_exitoso(
        self,
        db_session,
        habilitacion_factory,
        conductor_factory,
        empresa_factory,
        concepto_tupa_factory,
        usuario_factory
    ):
        """Test registrar pago exitosamente"""
        # Arrange
        empresa = await empresa_factory.create()
        conductor = await conductor_factory.create(empresa_id=empresa.id)
        habilitacion = await habilitacion_factory.create(conductor_id=conductor.id)
        concepto = await concepto_tupa_factory.create(
            codigo="HAB-CONDUCTOR",
            monto=Decimal("50.00")
        )
        usuario = await usuario_factory.create()
        
        pago_data = PagoCreate(
            habilitacion_id=str(habilitacion.id),
            concepto_tupa_id=str(concepto.id),
            numero_recibo="REC-001",
            monto=Decimal("50.00"),
            fecha_pago=date.today(),
            entidad_bancaria="Banco de la Nación"
        )
        service = PagoService(db_session)
        
        # Act
        pago = await service.registrar_pago(pago_data, usuario.id)
        
        # Assert
        assert pago.numero_recibo == "REC-001"
        assert pago.monto == Decimal("50.00")
        assert pago.estado == EstadoPago.PENDIENTE
        assert pago.registrado_por == str(usuario.id)
    
    async def test_registrar_pago_monto_incorrecto(
        self,
        db_session,
        habilitacion_factory,
        conductor_factory,
        empresa_factory,
        concepto_tupa_factory,
        usuario_factory
    ):
        """Test registrar pago con monto incorrecto"""
        # Arrange
        empresa = await empresa_factory.create()
        conductor = await conductor_factory.create(empresa_id=empresa.id)
        habilitacion = await habilitacion_factory.create(conductor_id=conductor.id)
        concepto = await concepto_tupa_factory.create(
            codigo="HAB-CONDUCTOR",
            monto=Decimal("50.00")
        )
        usuario = await usuario_factory.create()
        
        pago_data = PagoCreate(
            habilitacion_id=str(habilitacion.id),
            concepto_tupa_id=str(concepto.id),
            numero_recibo="REC-001",
            monto=Decimal("30.00"),  # Monto incorrecto
            fecha_pago=date.today(),
            entidad_bancaria="Banco de la Nación"
        )
        service = PagoService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.registrar_pago(pago_data, usuario.id)
        
        assert "monto" in str(exc.value).lower()
    
    async def test_registrar_pago_recibo_duplicado(
        self,
        db_session,
        habilitacion_factory,
        conductor_factory,
        empresa_factory,
        concepto_tupa_factory,
        pago_factory,
        usuario_factory
    ):
        """Test registrar pago con número de recibo duplicado"""
        # Arrange
        empresa = await empresa_factory.create()
        conductor1 = await conductor_factory.create(empresa_id=empresa.id)
        conductor2 = await conductor_factory.create(empresa_id=empresa.id)
        habilitacion1 = await habilitacion_factory.create(conductor_id=conductor1.id)
        habilitacion2 = await habilitacion_factory.create(conductor_id=conductor2.id)
        concepto = await concepto_tupa_factory.create(monto=Decimal("50.00"))
        usuario = await usuario_factory.create()
        
        # Crear primer pago
        await pago_factory.create(
            habilitacion_id=habilitacion1.id,
            concepto_tupa_id=concepto.id,
            numero_recibo="REC-001"
        )
        
        # Intentar crear segundo pago con mismo recibo
        pago_data = PagoCreate(
            habilitacion_id=str(habilitacion2.id),
            concepto_tupa_id=str(concepto.id),
            numero_recibo="REC-001",
            monto=Decimal("50.00"),
            fecha_pago=date.today(),
            entidad_bancaria="Banco de la Nación"
        )
        service = PagoService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.registrar_pago(pago_data, usuario.id)
        
        assert "recibo" in str(exc.value).lower()
    
    async def test_verificar_pago_confirmado_true(
        self,
        db_session,
        conductor_factory,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test verificar pago confirmado retorna True"""
        # Arrange
        conductor = await conductor_factory.create()
        habilitacion = await habilitacion_factory.create(conductor_id=conductor.id)
        concepto = await concepto_tupa_factory.create()
        await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.CONFIRMADO
        )
        service = PagoService(db_session)
        
        # Act
        confirmado = await service.verificar_pago_confirmado(habilitacion.id)
        
        # Assert
        assert confirmado is True
    
    async def test_verificar_pago_confirmado_false(
        self,
        db_session,
        conductor_factory,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test verificar pago confirmado retorna False"""
        # Arrange
        conductor = await conductor_factory.create()
        habilitacion = await habilitacion_factory.create(conductor_id=conductor.id)
        concepto = await concepto_tupa_factory.create()
        await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.PENDIENTE
        )
        service = PagoService(db_session)
        
        # Act
        confirmado = await service.verificar_pago_confirmado(habilitacion.id)
        
        # Assert
        assert confirmado is False
    
    async def test_confirmar_pago_exitoso(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory,
        usuario_factory
    ):
        """Test confirmar pago exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.PENDIENTE
        )
        usuario = await usuario_factory.create()
        service = PagoService(db_session)
        
        # Act
        pago_confirmado = await service.confirmar_pago(pago.id, usuario.id)
        
        # Assert
        assert pago_confirmado.estado == EstadoPago.CONFIRMADO
        assert pago_confirmado.confirmado_por == str(usuario.id)
        assert pago_confirmado.fecha_confirmacion is not None
    
    async def test_confirmar_pago_ya_confirmado(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory,
        usuario_factory
    ):
        """Test confirmar pago que ya está confirmado"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.CONFIRMADO
        )
        usuario = await usuario_factory.create()
        service = PagoService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.confirmar_pago(pago.id, usuario.id)
        
        assert "estado" in str(exc.value).lower()
    
    async def test_rechazar_pago_exitoso(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory,
        usuario_factory
    ):
        """Test rechazar pago exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id,
            estado=EstadoPago.PENDIENTE
        )
        usuario = await usuario_factory.create()
        service = PagoService(db_session)
        
        # Act
        pago_rechazado = await service.rechazar_pago(
            pago.id,
            "Monto incorrecto",
            usuario.id
        )
        
        # Assert
        assert pago_rechazado.estado == EstadoPago.RECHAZADO
        assert "Monto incorrecto" in pago_rechazado.observaciones
    
    async def test_generar_reporte_ingresos(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test generar reporte de ingresos"""
        # Arrange
        concepto = await concepto_tupa_factory.create(monto=Decimal("50.00"))
        
        # Crear varios pagos
        for i in range(3):
            habilitacion = await habilitacion_factory.create()
            await pago_factory.create(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto.id,
                estado=EstadoPago.CONFIRMADO,
                monto=Decimal("50.00"),
                fecha_pago=date.today()
            )
        
        for i in range(2):
            habilitacion = await habilitacion_factory.create()
            await pago_factory.create(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto.id,
                estado=EstadoPago.PENDIENTE,
                monto=Decimal("50.00"),
                fecha_pago=date.today()
            )
        
        service = PagoService(db_session)
        
        # Act
        reporte = await service.generar_reporte_ingresos(
            fecha_inicio=date.today() - timedelta(days=1),
            fecha_fin=date.today()
        )
        
        # Assert
        assert reporte.total_pagos == 5
        assert reporte.total_confirmados == 3
        assert reporte.total_pendientes == 2
        assert reporte.monto_confirmado == Decimal("150.00")
        assert reporte.monto_pendiente == Decimal("100.00")
    
    async def test_generar_reporte_ingresos_fechas_invalidas(self, db_session):
        """Test generar reporte con fechas inválidas"""
        # Arrange
        service = PagoService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.generar_reporte_ingresos(
                fecha_inicio=date.today(),
                fecha_fin=date.today() - timedelta(days=1)
            )
        
        assert "fecha" in str(exc.value).lower()
    
    async def test_get_pago_by_id(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test obtener pago por ID"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id
        )
        service = PagoService(db_session)
        
        # Act
        pago_obtenido = await service.get_pago_by_id(pago.id)
        
        # Assert
        assert pago_obtenido.id == str(pago.id)
        assert pago_obtenido.concepto_tupa is not None
    
    async def test_get_pago_by_habilitacion(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test obtener pago por habilitación"""
        # Arrange
        habilitacion = await habilitacion_factory.create()
        concepto = await concepto_tupa_factory.create()
        pago = await pago_factory.create(
            habilitacion_id=habilitacion.id,
            concepto_tupa_id=concepto.id
        )
        service = PagoService(db_session)
        
        # Act
        pago_obtenido = await service.get_pago_by_habilitacion(habilitacion.id)
        
        # Assert
        assert pago_obtenido is not None
        assert pago_obtenido.habilitacion_id == str(habilitacion.id)
    
    async def test_get_pagos_con_filtros(
        self,
        db_session,
        habilitacion_factory,
        concepto_tupa_factory,
        pago_factory
    ):
        """Test obtener pagos con filtros"""
        # Arrange
        concepto = await concepto_tupa_factory.create()
        
        # Crear pagos confirmados
        for i in range(3):
            habilitacion = await habilitacion_factory.create()
            await pago_factory.create(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto.id,
                estado=EstadoPago.CONFIRMADO
            )
        
        # Crear pagos pendientes
        for i in range(2):
            habilitacion = await habilitacion_factory.create()
            await pago_factory.create(
                habilitacion_id=habilitacion.id,
                concepto_tupa_id=concepto.id,
                estado=EstadoPago.PENDIENTE
            )
        
        service = PagoService(db_session)
        
        # Act
        pagos_confirmados = await service.get_pagos(estado=EstadoPago.CONFIRMADO)
        pagos_pendientes = await service.get_pagos(estado=EstadoPago.PENDIENTE)
        
        # Assert
        assert len(pagos_confirmados) == 3
        assert len(pagos_pendientes) == 2
