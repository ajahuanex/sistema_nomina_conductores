"""
Tests para EmpresaService
"""
import pytest
from uuid import uuid4
from datetime import date, timedelta
from app.services.empresa_service import EmpresaService
from app.schemas.empresa import (
    EmpresaCreate,
    EmpresaUpdate,
    AutorizacionEmpresaCreate
)
from app.models.empresa import Empresa, TipoAutorizacion, AutorizacionEmpresa
from app.core.exceptions import (
    RecursoNoEncontrado,
    ValidacionError
)


@pytest.mark.asyncio
class TestEmpresaService:
    """Tests para el servicio de empresas"""
    
    async def test_registrar_empresa_exitoso(self, db_session, tipo_autorizacion_factory):
        """Test: Registrar una empresa exitosamente"""
        # Arrange
        tipo_auth = await tipo_autorizacion_factory()
        service = EmpresaService(db_session)
        
        empresa_data = EmpresaCreate(
            ruc="20123456789",
            razon_social="Transportes Test SAC",
            direccion="Av. Test 123",
            telefono="051-123456",
            email="test@transportes.com",
            gerente_id=None,
            activo=True,
            autorizaciones=[]
        )
        
        # Act
        empresa = await service.registrar_empresa(empresa_data)
        
        # Assert
        assert empresa is not None
        assert empresa.ruc == "20123456789"
        assert empresa.razon_social == "Transportes Test SAC"
        assert empresa.activo is True
    
    async def test_registrar_empresa_con_autorizaciones(self, db_session, tipo_autorizacion_factory):
        """Test: Registrar una empresa con autorizaciones"""
        # Arrange
        tipo_auth = await tipo_autorizacion_factory()
        service = EmpresaService(db_session)
        
        autorizacion_data = AutorizacionEmpresaCreate(
            tipo_autorizacion_id=str(tipo_auth.id),
            numero_resolucion="RD-2024-001",
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            vigente=True
        )
        
        empresa_data = EmpresaCreate(
            ruc="20123456789",
            razon_social="Transportes Test SAC",
            direccion="Av. Test 123",
            telefono="051-123456",
            email="test@transportes.com",
            gerente_id=None,
            activo=True,
            autorizaciones=[autorizacion_data]
        )
        
        # Act
        empresa = await service.registrar_empresa(empresa_data)
        
        # Assert
        assert empresa is not None
        assert len(empresa.autorizaciones) == 1
        assert empresa.autorizaciones[0].numero_resolucion == "RD-2024-001"
    
    async def test_registrar_empresa_ruc_duplicado(self, db_session, empresa_factory):
        """Test: No se puede registrar una empresa con RUC duplicado"""
        # Arrange
        empresa_existente = await empresa_factory(ruc="20123456789")
        service = EmpresaService(db_session)
        
        empresa_data = EmpresaCreate(
            ruc="20123456789",
            razon_social="Otra Empresa SAC",
            direccion="Av. Test 456",
            telefono="051-654321",
            email="otra@transportes.com",
            gerente_id=None,
            activo=True,
            autorizaciones=[]
        )
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.registrar_empresa(empresa_data)
        
        assert "ya está registrado" in str(exc.value.message).lower()
    
    async def test_registrar_empresa_ruc_invalido(self, db_session):
        """Test: No se puede registrar una empresa con RUC inválido"""
        # Arrange
        from pydantic import ValidationError as PydanticValidationError
        service = EmpresaService(db_session)
        
        # Act & Assert - Pydantic valida antes de llegar al servicio
        with pytest.raises(PydanticValidationError) as exc:
            empresa_data = EmpresaCreate(
                ruc="123",  # RUC inválido (menos de 11 dígitos)
                razon_social="Transportes Test SAC",
                direccion="Av. Test 123",
                telefono="051-123456",
                email="test@transportes.com",
                gerente_id=None,
                activo=True,
                autorizaciones=[]
            )
        
        assert "at least 11 characters" in str(exc.value).lower()
    
    async def test_agregar_autorizacion_exitoso(self, db_session, empresa_factory, tipo_autorizacion_factory):
        """Test: Agregar una autorización a una empresa"""
        # Arrange
        empresa = await empresa_factory()
        tipo_auth = await tipo_autorizacion_factory()
        service = EmpresaService(db_session)
        
        autorizacion_data = AutorizacionEmpresaCreate(
            tipo_autorizacion_id=str(tipo_auth.id),
            numero_resolucion="RD-2024-002",
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            vigente=True
        )
        
        # Act
        autorizacion = await service.agregar_autorizacion(
            str(empresa.id),
            autorizacion_data
        )
        
        # Assert
        assert autorizacion is not None
        assert autorizacion.empresa_id == empresa.id
        assert autorizacion.numero_resolucion == "RD-2024-002"
    
    async def test_agregar_autorizacion_empresa_no_existe(self, db_session, tipo_autorizacion_factory):
        """Test: No se puede agregar autorización a empresa inexistente"""
        # Arrange
        tipo_auth = await tipo_autorizacion_factory()
        service = EmpresaService(db_session)
        
        autorizacion_data = AutorizacionEmpresaCreate(
            tipo_autorizacion_id=str(tipo_auth.id),
            numero_resolucion="RD-2024-003",
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            vigente=True
        )
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado):
            await service.agregar_autorizacion(
                str(uuid4()),
                autorizacion_data
            )
    
    async def test_agregar_autorizacion_tipo_no_existe(self, db_session, empresa_factory):
        """Test: No se puede agregar autorización con tipo inexistente"""
        # Arrange
        empresa = await empresa_factory()
        service = EmpresaService(db_session)
        
        autorizacion_data = AutorizacionEmpresaCreate(
            tipo_autorizacion_id=str(uuid4()),  # Tipo que no existe
            numero_resolucion="RD-2024-004",
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            vigente=True
        )
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado):
            await service.agregar_autorizacion(
                str(empresa.id),
                autorizacion_data
            )
    
    async def test_agregar_autorizacion_numero_resolucion_duplicado(
        self,
        db_session,
        empresa_factory,
        tipo_autorizacion_factory,
        autorizacion_empresa_factory
    ):
        """Test: No se puede agregar autorización con número de resolución duplicado"""
        # Arrange
        empresa = await empresa_factory()
        tipo_auth = await tipo_autorizacion_factory()
        
        # Crear una autorización existente
        await autorizacion_empresa_factory(
            empresa_id=empresa.id,
            tipo_autorizacion_id=tipo_auth.id,
            numero_resolucion="RD-2024-005"
        )
        
        service = EmpresaService(db_session)
        
        autorizacion_data = AutorizacionEmpresaCreate(
            tipo_autorizacion_id=str(tipo_auth.id),
            numero_resolucion="RD-2024-005",  # Duplicado
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            vigente=True
        )
        
        # Act & Assert
        with pytest.raises(ValidacionError) as exc:
            await service.agregar_autorizacion(
                str(empresa.id),
                autorizacion_data
            )
        
        assert "ya existe" in str(exc.value.message).lower()
    
    async def test_obtener_empresa_exitoso(self, db_session, empresa_factory):
        """Test: Obtener una empresa por ID"""
        # Arrange
        empresa = await empresa_factory()
        service = EmpresaService(db_session)
        
        # Act
        empresa_obtenida = await service.obtener_empresa(str(empresa.id))
        
        # Assert
        assert empresa_obtenida is not None
        assert empresa_obtenida.id == empresa.id
        assert empresa_obtenida.ruc == empresa.ruc
    
    async def test_obtener_empresa_no_existe(self, db_session):
        """Test: Error al obtener empresa inexistente"""
        # Arrange
        service = EmpresaService(db_session)
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado):
            await service.obtener_empresa(str(uuid4()))
    
    async def test_obtener_empresa_por_ruc(self, db_session, empresa_factory):
        """Test: Obtener una empresa por RUC"""
        # Arrange
        empresa = await empresa_factory(ruc="20987654321")
        service = EmpresaService(db_session)
        
        # Act
        empresa_obtenida = await service.obtener_empresa_por_ruc("20987654321")
        
        # Assert
        assert empresa_obtenida is not None
        assert empresa_obtenida.id == empresa.id
        assert empresa_obtenida.ruc == "20987654321"
    
    async def test_actualizar_empresa_exitoso(self, db_session, empresa_factory):
        """Test: Actualizar una empresa"""
        # Arrange
        empresa = await empresa_factory()
        service = EmpresaService(db_session)
        
        update_data = EmpresaUpdate(
            razon_social="Transportes Actualizado SAC",
            direccion="Nueva Dirección 789"
        )
        
        # Act
        empresa_actualizada = await service.actualizar_empresa(
            str(empresa.id),
            update_data
        )
        
        # Assert
        assert empresa_actualizada.razon_social == "Transportes Actualizado SAC"
        assert empresa_actualizada.direccion == "Nueva Dirección 789"
        assert empresa_actualizada.ruc == empresa.ruc  # No cambió
    
    async def test_actualizar_empresa_no_existe(self, db_session):
        """Test: Error al actualizar empresa inexistente"""
        # Arrange
        service = EmpresaService(db_session)
        
        update_data = EmpresaUpdate(
            razon_social="Transportes Test SAC"
        )
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado):
            await service.actualizar_empresa(str(uuid4()), update_data)
    
    async def test_obtener_conductores_empresa(self, db_session, empresa_factory, conductor_factory):
        """Test: Obtener conductores de una empresa"""
        # Arrange
        empresa = await empresa_factory()
        conductor1 = await conductor_factory(empresa_id=empresa.id)
        conductor2 = await conductor_factory(empresa_id=empresa.id)
        
        service = EmpresaService(db_session)
        
        # Act
        conductores = await service.obtener_conductores_empresa(str(empresa.id))
        
        # Assert
        assert len(conductores) == 2
        assert all(c.empresa_id == empresa.id for c in conductores)
    
    async def test_obtener_conductores_empresa_no_existe(self, db_session):
        """Test: Error al obtener conductores de empresa inexistente"""
        # Arrange
        service = EmpresaService(db_session)
        
        # Act & Assert
        with pytest.raises(RecursoNoEncontrado):
            await service.obtener_conductores_empresa(str(uuid4()))
    
    async def test_contar_empresas(self, db_session, empresa_factory):
        """Test: Contar empresas"""
        # Arrange
        await empresa_factory()
        await empresa_factory()
        await empresa_factory(activo=False)
        
        service = EmpresaService(db_session)
        
        # Act
        total = await service.contar_empresas()
        total_activas = await service.contar_empresas(filtros={'activo': True})
        
        # Assert
        assert total == 3
        assert total_activas == 2
    
    async def test_contar_conductores_empresa(self, db_session, empresa_factory, conductor_factory):
        """Test: Contar conductores de una empresa"""
        # Arrange
        empresa = await empresa_factory()
        await conductor_factory(empresa_id=empresa.id)
        await conductor_factory(empresa_id=empresa.id)
        await conductor_factory(empresa_id=empresa.id)
        
        service = EmpresaService(db_session)
        
        # Act
        total = await service.contar_conductores_empresa(str(empresa.id))
        
        # Assert
        assert total == 3
