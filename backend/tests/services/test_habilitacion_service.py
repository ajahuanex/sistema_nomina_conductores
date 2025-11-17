"""
Tests para HabilitacionService
"""
import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4
from app.services.habilitacion_service import HabilitacionService
from app.models.habilitacion import EstadoHabilitacion, EstadoPago, Pago
from app.models.conductor import EstadoConductor
from app.core.exceptions import RecursoNoEncontrado, ValidacionError


@pytest.mark.asyncio
class TestHabilitacionService:
    """Tests para HabilitacionService"""
    
    async def test_crear_solicitud_exitosa(self, db_session, conductor_factory):
        """Test crear solicitud de habilitación exitosamente"""
        # Arrange
        conductor = await conductor_factory()
        service = HabilitacionService(db_session)
        
        # Act
        habilitacion = await service.crear_solicitud(conductor.id)
        
        # Assert
        assert habilitacion.conductor_id == conductor.id
        assert habilitacion.estado == EstadoHabilitacion.PENDIENTE
        assert habilitacion.codigo_habilitacion is not None
        assert habilitacion.codigo_habilitacion.startswith("HAB-")
        assert habilitacion.fecha_solicitud is not None
        
        # Verificar que el conductor cambió a estado PENDIENTE
        await db_session.refresh(conductor)
        assert conductor.estado == EstadoConductor.PENDIENTE
    
    async def test_crear_solicitud_conductor_no_existe(self, db_session):
        """Test crear solicitud con conductor inexistente"""
        # Arrange
        service = HabilitacionService(db_session)
        conductor_id_falso = uuid4()
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado) as exc_info:
            await service.crear_solicitud(conductor_id_falso)
        
        assert "Conductor" in str(exc_info.value)
    
    async def test_crear_solicitud_conductor_con_habilitacion_activa(
        self,
        db_session,
        conductor_factory,
        habilitacion_factory
    ):
        """Test crear solicitud cuando conductor ya tiene habilitación activa"""
        # Arrange
        conductor = await conductor_factory()
        await habilitacion_factory(
            conductor_id=conductor.id,
            estado=EstadoHabilitacion.PENDIENTE
        )
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.crear_solicitud(conductor.id)
        
        assert "ya tiene una habilitación" in str(exc_info.value).lower()
    
    async def test_obtener_solicitudes_pendientes(
        self,
        db_session,
        habilitacion_factory
    ):
        """Test obtener solicitudes pendientes"""
        # Arrange
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.EN_REVISION)
        service = HabilitacionService(db_session)
        
        # Act
        pendientes = await service.obtener_solicitudes_pendientes()
        
        # Assert
        assert len(pendientes) == 2
        assert all(h.estado == EstadoHabilitacion.PENDIENTE for h in pendientes)
    
    async def test_revisar_solicitud_exitosa(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test revisar solicitud exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.PENDIENTE
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act
        resultado = await service.revisar_solicitud(
            habilitacion.id,
            usuario.id,
            "Revisando documentos"
        )
        
        # Assert
        assert resultado.estado == EstadoHabilitacion.EN_REVISION
        assert resultado.revisado_por == usuario.id
        assert resultado.fecha_revision is not None
        assert resultado.observaciones == "Revisando documentos"
    
    async def test_revisar_solicitud_estado_invalido(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test revisar solicitud en estado inválido"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.APROBADO
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.revisar_solicitud(habilitacion.id, usuario.id)
        
        assert "PENDIENTE" in str(exc_info.value)
    
    async def test_aprobar_solicitud_exitosa(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test aprobar solicitud exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.EN_REVISION
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act
        resultado = await service.aprobar_solicitud(
            habilitacion.id,
            usuario.id,
            "Documentos válidos"
        )
        
        # Assert
        assert resultado.estado == EstadoHabilitacion.APROBADO
        assert resultado.aprobado_por == usuario.id
        assert resultado.fecha_aprobacion is not None
        assert "Documentos válidos" in resultado.observaciones
    
    async def test_aprobar_solicitud_licencia_vencida(
        self,
        db_session,
        conductor_factory,
        habilitacion_factory,
        usuario_factory
    ):
        """Test aprobar solicitud con licencia vencida"""
        # Arrange
        # Crear conductor con licencia válida primero
        conductor = await conductor_factory()
        
        # Luego actualizar la licencia a vencida directamente en la BD usando update
        from app.models.conductor import Conductor
        from sqlalchemy import update
        
        stmt = update(Conductor).where(Conductor.id == conductor.id).values(
            licencia_vencimiento=date.today() - timedelta(days=1)
        )
        await db_session.execute(stmt)
        await db_session.commit()
        
        habilitacion = await habilitacion_factory(
            conductor_id=conductor.id,
            estado=EstadoHabilitacion.EN_REVISION
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.aprobar_solicitud(habilitacion.id, usuario.id)
        
        assert "licencia" in str(exc_info.value).lower()
        assert "vencida" in str(exc_info.value).lower()
    
    async def test_observar_solicitud_exitosa(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test observar solicitud exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.EN_REVISION
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act
        resultado = await service.observar_solicitud(
            habilitacion.id,
            "Falta certificado médico actualizado",
            usuario.id
        )
        
        # Assert
        assert resultado.estado == EstadoHabilitacion.OBSERVADO
        assert "certificado médico" in resultado.observaciones
        
        # Verificar que el conductor cambió a OBSERVADO
        from app.models.conductor import Conductor
        conductor = await db_session.get(Conductor, habilitacion.conductor_id)
        assert conductor.estado == EstadoConductor.OBSERVADO
    
    async def test_habilitar_conductor_exitoso(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory,
        pago_factory
    ):
        """Test habilitar conductor exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.APROBADO
        )
        await pago_factory(
            habilitacion_id=habilitacion.id,
            estado=EstadoPago.CONFIRMADO
        )
        usuario = await usuario_factory()
        vigencia = date.today() + timedelta(days=365)
        service = HabilitacionService(db_session)
        
        # Act
        resultado = await service.habilitar_conductor(
            habilitacion.id,
            usuario.id,
            vigencia,
            "Habilitado por 1 año"
        )
        
        # Assert
        assert resultado.estado == EstadoHabilitacion.HABILITADO
        assert resultado.habilitado_por == usuario.id
        assert resultado.fecha_habilitacion is not None
        assert resultado.vigencia_hasta == vigencia
        
        # Verificar que el conductor cambió a HABILITADO
        from app.models.conductor import Conductor
        conductor = await db_session.get(Conductor, habilitacion.conductor_id)
        assert conductor.estado == EstadoConductor.HABILITADO
    
    async def test_habilitar_conductor_sin_pago(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test habilitar conductor sin pago confirmado"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.APROBADO
        )
        usuario = await usuario_factory()
        vigencia = date.today() + timedelta(days=365)
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.habilitar_conductor(
                habilitacion.id,
                usuario.id,
                vigencia
            )
        
        assert "pago" in str(exc_info.value).lower()
    
    async def test_habilitar_conductor_fecha_pasada(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory,
        pago_factory
    ):
        """Test habilitar conductor con fecha de vigencia pasada"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.APROBADO
        )
        await pago_factory(
            habilitacion_id=habilitacion.id,
            estado=EstadoPago.CONFIRMADO
        )
        usuario = await usuario_factory()
        vigencia = date.today() - timedelta(days=1)
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.habilitar_conductor(
                habilitacion.id,
                usuario.id,
                vigencia
            )
        
        assert "vigencia" in str(exc_info.value).lower()
        assert "futura" in str(exc_info.value).lower()
    
    async def test_suspender_habilitacion_exitosa(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test suspender habilitación exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act
        resultado = await service.suspender_habilitacion(
            habilitacion.id,
            "Suspendido por infracción grave",
            usuario.id
        )
        
        # Assert
        assert "SUSPENDIDO" in resultado.observaciones
        assert "infracción grave" in resultado.observaciones
        
        # Verificar que el conductor cambió a SUSPENDIDO
        from app.models.conductor import Conductor
        conductor = await db_session.get(Conductor, habilitacion.conductor_id)
        assert conductor.estado == EstadoConductor.SUSPENDIDO
    
    async def test_suspender_habilitacion_no_habilitada(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test suspender habilitación que no está habilitada"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.PENDIENTE
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.suspender_habilitacion(
                habilitacion.id,
                "Motivo",
                usuario.id
            )
        
        assert "HABILITADAS" in str(exc_info.value)
    
    async def test_revocar_habilitacion_exitosa(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory
    ):
        """Test revocar habilitación exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO
        )
        usuario = await usuario_factory()
        service = HabilitacionService(db_session)
        
        # Act
        resultado = await service.revocar_habilitacion(
            habilitacion.id,
            "Revocado por decisión administrativa",
            usuario.id
        )
        
        # Assert
        assert resultado.estado == EstadoHabilitacion.RECHAZADO
        assert "REVOCADO" in resultado.observaciones
        assert "decisión administrativa" in resultado.observaciones
        
        # Verificar que el conductor cambió a REVOCADO
        from app.models.conductor import Conductor
        conductor = await db_session.get(Conductor, habilitacion.conductor_id)
        assert conductor.estado == EstadoConductor.REVOCADO
    
    async def test_verificar_vigencia_habilitacion_vigente(
        self,
        db_session,
        habilitacion_factory
    ):
        """Test verificar vigencia de habilitación vigente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        service = HabilitacionService(db_session)
        
        # Act
        es_vigente = await service.verificar_vigencia(habilitacion.conductor_id)
        
        # Assert
        assert es_vigente is True
    
    async def test_verificar_vigencia_habilitacion_vencida(
        self,
        db_session,
        habilitacion_factory
    ):
        """Test verificar vigencia de habilitación vencida"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            vigencia_hasta=date.today() - timedelta(days=1)
        )
        service = HabilitacionService(db_session)
        
        # Act
        es_vigente = await service.verificar_vigencia(habilitacion.conductor_id)
        
        # Assert
        assert es_vigente is False
    
    async def test_verificar_vigencia_sin_habilitacion(
        self,
        db_session,
        conductor_factory
    ):
        """Test verificar vigencia de conductor sin habilitación"""
        # Arrange
        conductor = await conductor_factory()
        service = HabilitacionService(db_session)
        
        # Act
        es_vigente = await service.verificar_vigencia(conductor.id)
        
        # Assert
        assert es_vigente is False
    
    async def test_obtener_habilitaciones_con_filtro_estado(
        self,
        db_session,
        habilitacion_factory
    ):
        """Test obtener habilitaciones filtradas por estado"""
        # Arrange
        await habilitacion_factory(estado=EstadoHabilitacion.PENDIENTE)
        await habilitacion_factory(estado=EstadoHabilitacion.APROBADO)
        await habilitacion_factory(estado=EstadoHabilitacion.APROBADO)
        service = HabilitacionService(db_session)
        
        # Act
        aprobadas = await service.obtener_habilitaciones(
            estado=EstadoHabilitacion.APROBADO
        )
        
        # Assert
        assert len(aprobadas) == 2
        assert all(h.estado == EstadoHabilitacion.APROBADO for h in aprobadas)
    
    async def test_codigo_habilitacion_es_unico(
        self,
        db_session,
        conductor_factory
    ):
        """Test que los códigos de habilitación son únicos"""
        # Arrange
        conductor1 = await conductor_factory()
        conductor2 = await conductor_factory()
        service = HabilitacionService(db_session)
        
        # Act
        hab1 = await service.crear_solicitud(conductor1.id)
        hab2 = await service.crear_solicitud(conductor2.id)
        
        # Assert
        assert hab1.codigo_habilitacion != hab2.codigo_habilitacion
        assert hab1.codigo_habilitacion.startswith("HAB-")
        assert hab2.codigo_habilitacion.startswith("HAB-")


    async def test_generar_certificado_exitoso(
        self,
        db_session,
        habilitacion_factory,
        usuario_factory,
        pago_factory
    ):
        """Test generar certificado de habilitación exitosamente"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.HABILITADO,
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        
        # Asignar usuario que habilitó
        usuario = await usuario_factory()
        habilitacion.habilitado_por = usuario.id
        await db_session.commit()
        
        service = HabilitacionService(db_session)
        
        # Act
        pdf_bytes = await service.generar_certificado(habilitacion.id)
        
        # Assert
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Verificar que es un PDF válido
        assert pdf_bytes[:4] == b'%PDF'
    
    async def test_generar_certificado_habilitacion_no_existe(
        self,
        db_session
    ):
        """Test generar certificado de habilitación inexistente"""
        # Arrange
        service = HabilitacionService(db_session)
        habilitacion_id_falso = uuid4()
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado) as exc_info:
            await service.generar_certificado(habilitacion_id_falso)
        
        assert "Habilitacion" in str(exc_info.value)
    
    async def test_generar_certificado_estado_invalido(
        self,
        db_session,
        habilitacion_factory
    ):
        """Test generar certificado de habilitación no habilitada"""
        # Arrange
        habilitacion = await habilitacion_factory(
            estado=EstadoHabilitacion.PENDIENTE
        )
        service = HabilitacionService(db_session)
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc_info:
            await service.generar_certificado(habilitacion.id)
        
        assert "HABILITADAS" in str(exc_info.value)
        assert "estado" in str(exc_info.value).lower()
    
    async def test_generar_certificado_con_datos_completos(
        self,
        db_session,
        conductor_factory,
        empresa_factory,
        habilitacion_factory,
        usuario_factory
    ):
        """Test generar certificado con todos los datos del conductor y empresa"""
        # Arrange
        empresa = await empresa_factory(
            razon_social="Transportes Test SAC",
            ruc="20123456789"
        )
        conductor = await conductor_factory(
            empresa_id=empresa.id,
            nombres="Juan Carlos",
            apellidos="Pérez García",
            dni="12345678",
            licencia_numero="Q12345678",
            licencia_categoria="A-IIIb"
        )
        habilitacion = await habilitacion_factory(
            conductor_id=conductor.id,
            estado=EstadoHabilitacion.HABILITADO,
            codigo_habilitacion="HAB-20240101120000-ABC123",
            fecha_habilitacion=datetime.utcnow(),
            vigencia_hasta=date.today() + timedelta(days=365)
        )
        
        usuario = await usuario_factory(
            nombres="Director",
            apellidos="DRTC Puno"
        )
        habilitacion.habilitado_por = usuario.id
        await db_session.commit()
        
        service = HabilitacionService(db_session)
        
        # Act
        pdf_bytes = await service.generar_certificado(habilitacion.id)
        
        # Assert
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000  # PDF debe tener contenido sustancial
        assert pdf_bytes[:4] == b'%PDF'
