"""
Tests para ConductorService
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4
from app.services.conductor_service import ConductorService
from app.schemas.conductor import ConductorCreate, ConductorUpdate, ConductorBusqueda
from app.models.conductor import EstadoConductor
from app.core.exceptions import (
    RecursoNoEncontrado,
    ValidacionError,
    ConflictoError
)


@pytest.mark.asyncio
class TestConductorService:
    """Tests para ConductorService"""
    
    async def test_registrar_conductor_exitoso(
        self,
        db_session,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test registrar conductor con datos válidos"""
        # Crear empresa con autorización
        tipo_auth = await tipo_autorizacion_factory(codigo="MERCANCIAS")
        empresa = await empresa_factory.create_with_autorizacion(tipo_auth)
        
        service = ConductorService(db_session)
        
        conductor_data = ConductorCreate(
            dni="12345678",
            nombres="Juan Carlos",
            apellidos="Pérez García",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Av. Principal 123, Puno",
            telefono="987654321",
            email="juan.perez@example.com",
            licencia_numero="Q12345678",
            licencia_categoria="A-IIIb",
            licencia_emision=date(2020, 1, 1),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=empresa.id
        )
        
        conductor = await service.registrar_conductor(
            conductor_data=conductor_data,
            usuario_id=uuid4()
        )
        
        assert conductor.id is not None
        assert conductor.dni == "12345678"
        assert conductor.estado == EstadoConductor.PENDIENTE
        assert conductor.empresa_id == empresa.id
    
    async def test_registrar_conductor_empresa_no_existe(self, db_session):
        """Test registrar conductor con empresa inexistente"""
        service = ConductorService(db_session)
        
        conductor_data = ConductorCreate(
            dni="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Av. Principal 123",
            telefono="987654321",
            email="juan@example.com",
            licencia_numero="Q12345678",
            licencia_categoria="A-IIIb",
            licencia_emision=date(2020, 1, 1),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=uuid4()
        )
        
        with pytest.raises(RecursoNoEncontrado) as exc_info:
            await service.registrar_conductor(
                conductor_data=conductor_data,
                usuario_id=uuid4()
            )
        
        assert "Empresa" in str(exc_info.value)
    
    async def test_registrar_conductor_dni_duplicado(
        self,
        db_session,
        conductor_factory
    ):
        """Test registrar conductor con DNI duplicado"""
        conductor_existente = await conductor_factory(dni="12345678")
        
        service = ConductorService(db_session)
        
        conductor_data = ConductorCreate(
            dni="12345678",  # DNI duplicado
            nombres="Otro",
            apellidos="Conductor",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Av. Principal 123",
            telefono="987654321",
            email="otro@example.com",
            licencia_numero="Q99999999",
            licencia_categoria="A-IIIb",
            licencia_emision=date(2020, 1, 1),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=conductor_existente.empresa_id
        )
        
        with pytest.raises(ConflictoError) as exc_info:
            await service.registrar_conductor(
                conductor_data=conductor_data,
                usuario_id=uuid4()
            )
        
        assert "DNI" in str(exc_info.value)
    
    async def test_registrar_conductor_licencia_duplicada(
        self,
        db_session,
        conductor_factory
    ):
        """Test registrar conductor con licencia duplicada"""
        conductor_existente = await conductor_factory(licencia_numero="Q12345678")
        
        service = ConductorService(db_session)
        
        conductor_data = ConductorCreate(
            dni="99999999",
            nombres="Otro",
            apellidos="Conductor",
            fecha_nacimiento=date(1990, 5, 15),
            direccion="Av. Principal 123",
            telefono="987654321",
            email="otro@example.com",
            licencia_numero="Q12345678",  # Licencia duplicada
            licencia_categoria="A-IIIb",
            licencia_emision=date(2020, 1, 1),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=conductor_existente.empresa_id
        )
        
        with pytest.raises(ConflictoError) as exc_info:
            await service.registrar_conductor(
                conductor_data=conductor_data,
                usuario_id=uuid4()
            )
        
        assert "licencia" in str(exc_info.value)
    
    async def test_validar_categoria_licencia_mercancias(
        self,
        db_session,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test validación de categoría para transporte de mercancías"""
        tipo_auth = await tipo_autorizacion_factory(codigo="MERCANCIAS")
        empresa = await empresa_factory.create_with_autorizacion(tipo_auth)
        
        service = ConductorService(db_session)
        
        # Categoría válida
        assert await service.validar_categoria_licencia("A-IIIb", empresa.id) is True
        assert await service.validar_categoria_licencia("A-IIIc", empresa.id) is True
        
        # Categoría inválida
        assert await service.validar_categoria_licencia("A-IIa", empresa.id) is False
        assert await service.validar_categoria_licencia("A-I", empresa.id) is False
    
    async def test_validar_categoria_licencia_turismo(
        self,
        db_session,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test validación de categoría para transporte de turismo"""
        tipo_auth = await tipo_autorizacion_factory(codigo="TURISMO")
        empresa = await empresa_factory.create_with_autorizacion(tipo_auth)
        
        service = ConductorService(db_session)
        
        # Categorías válidas
        assert await service.validar_categoria_licencia("A-IIb", empresa.id) is True
        assert await service.validar_categoria_licencia("A-IIIa", empresa.id) is True
        assert await service.validar_categoria_licencia("A-IIIb", empresa.id) is True
        
        # Categoría inválida
        assert await service.validar_categoria_licencia("A-I", empresa.id) is False
    
    async def test_actualizar_conductor(
        self,
        db_session,
        conductor_factory
    ):
        """Test actualizar datos de conductor"""
        conductor = await conductor_factory()
        
        service = ConductorService(db_session)
        
        update_data = ConductorUpdate(
            telefono="999888777",
            email="nuevo@example.com",
            direccion="Nueva dirección 456"
        )
        
        conductor_actualizado = await service.actualizar_conductor(
            conductor_id=conductor.id,
            conductor_data=update_data,
            usuario_id=uuid4()
        )
        
        assert conductor_actualizado.telefono == "999888777"
        assert conductor_actualizado.email == "nuevo@example.com"
        assert conductor_actualizado.direccion == "Nueva dirección 456"
    
    async def test_cambiar_estado_conductor(
        self,
        db_session,
        conductor_factory
    ):
        """Test cambiar estado de conductor"""
        conductor = await conductor_factory(estado=EstadoConductor.PENDIENTE)
        
        service = ConductorService(db_session)
        
        conductor_actualizado = await service.cambiar_estado_conductor(
            conductor_id=conductor.id,
            nuevo_estado=EstadoConductor.HABILITADO,
            observacion="Conductor habilitado correctamente",
            usuario_id=uuid4()
        )
        
        assert conductor_actualizado.estado == EstadoConductor.HABILITADO
        assert "habilitado correctamente" in conductor_actualizado.observaciones
    
    async def test_cambiar_estado_transicion_invalida(
        self,
        db_session,
        conductor_factory
    ):
        """Test cambiar estado con transición inválida"""
        conductor = await conductor_factory(estado=EstadoConductor.REVOCADO)
        
        service = ConductorService(db_session)
        
        # No se puede cambiar desde REVOCADO
        with pytest.raises(ValidacionError) as exc_info:
            await service.cambiar_estado_conductor(
                conductor_id=conductor.id,
                nuevo_estado=EstadoConductor.HABILITADO,
                usuario_id=uuid4()
            )
        
        assert "No se puede cambiar de estado" in str(exc_info.value)
    
    async def test_buscar_conductores_por_dni(
        self,
        db_session,
        conductor_factory
    ):
        """Test buscar conductores por DNI"""
        conductor = await conductor_factory(dni="12345678")
        
        service = ConductorService(db_session)
        
        busqueda = ConductorBusqueda(dni="12345678")
        resultado = await service.buscar_conductores(busqueda)
        
        assert resultado["total"] >= 1
        assert any(c.dni == "12345678" for c in resultado["items"])
    
    async def test_buscar_conductores_por_nombre(
        self,
        db_session,
        conductor_factory
    ):
        """Test buscar conductores por nombre"""
        conductor = await conductor_factory(
            nombres="Juan Carlos",
            apellidos="Pérez García"
        )
        
        service = ConductorService(db_session)
        
        busqueda = ConductorBusqueda(nombres="Juan")
        resultado = await service.buscar_conductores(busqueda)
        
        assert resultado["total"] >= 1
        assert any("Juan" in c.nombres for c in resultado["items"])
    
    async def test_buscar_conductores_por_empresa(
        self,
        db_session,
        conductor_factory,
        empresa_factory
    ):
        """Test buscar conductores por empresa"""
        empresa = await empresa_factory()
        conductor1 = await conductor_factory(empresa_id=empresa.id)
        conductor2 = await conductor_factory(empresa_id=empresa.id)
        
        service = ConductorService(db_session)
        
        busqueda = ConductorBusqueda(empresa_id=empresa.id)
        resultado = await service.buscar_conductores(busqueda)
        
        assert resultado["total"] >= 2
        assert all(c.empresa_id == empresa.id for c in resultado["items"])
    
    async def test_buscar_conductores_por_estado(
        self,
        db_session,
        conductor_factory
    ):
        """Test buscar conductores por estado"""
        conductor1 = await conductor_factory(estado=EstadoConductor.HABILITADO)
        conductor2 = await conductor_factory(estado=EstadoConductor.PENDIENTE)
        
        service = ConductorService(db_session)
        
        busqueda = ConductorBusqueda(estado="habilitado")
        resultado = await service.buscar_conductores(busqueda)
        
        assert all(c.estado == EstadoConductor.HABILITADO for c in resultado["items"])
    
    async def test_obtener_conductor_por_id(
        self,
        db_session,
        conductor_factory
    ):
        """Test obtener conductor por ID"""
        conductor = await conductor_factory()
        
        service = ConductorService(db_session)
        
        conductor_obtenido = await service.obtener_conductor_por_id(conductor.id)
        
        assert conductor_obtenido.id == conductor.id
        assert conductor_obtenido.dni == conductor.dni
    
    async def test_obtener_conductor_por_dni(
        self,
        db_session,
        conductor_factory
    ):
        """Test obtener conductor por DNI"""
        conductor = await conductor_factory(dni="12345678")
        
        service = ConductorService(db_session)
        
        conductor_obtenido = await service.obtener_conductor_por_dni("12345678")
        
        assert conductor_obtenido.id == conductor.id
        assert conductor_obtenido.dni == "12345678"
    
    async def test_eliminar_conductor_pendiente(
        self,
        db_session,
        conductor_factory
    ):
        """Test eliminar conductor en estado pendiente"""
        conductor = await conductor_factory(estado=EstadoConductor.PENDIENTE)
        
        service = ConductorService(db_session)
        
        await service.eliminar_conductor(
            conductor_id=conductor.id,
            usuario_id=uuid4()
        )
        
        # Verificar que fue eliminado
        with pytest.raises(RecursoNoEncontrado):
            await service.obtener_conductor_por_id(conductor.id)
    
    async def test_eliminar_conductor_habilitado_falla(
        self,
        db_session,
        conductor_factory
    ):
        """Test no se puede eliminar conductor habilitado"""
        conductor = await conductor_factory(estado=EstadoConductor.HABILITADO)
        
        service = ConductorService(db_session)
        
        with pytest.raises(ValidacionError) as exc_info:
            await service.eliminar_conductor(
                conductor_id=conductor.id,
                usuario_id=uuid4()
            )
        
        assert "habilitado" in str(exc_info.value).lower()
    
    async def test_obtener_requisitos_categoria(self, db_session):
        """Test obtener requisitos de categoría por tipo de autorización"""
        service = ConductorService(db_session)
        
        requisitos_mercancias = await service.obtener_requisitos_categoria("MERCANCIAS")
        assert "A-IIIb" in requisitos_mercancias
        assert "A-IIIc" in requisitos_mercancias
        
        requisitos_turismo = await service.obtener_requisitos_categoria("TURISMO")
        assert "A-IIb" in requisitos_turismo
        assert "A-IIIa" in requisitos_turismo
