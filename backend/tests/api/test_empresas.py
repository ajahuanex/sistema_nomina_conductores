"""
Tests de integración para endpoints de empresas
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from app.models.user import RolUsuario


@pytest.mark.asyncio
class TestEmpresasEndpoints:
    """Tests para endpoints de empresas"""
    
    async def test_listar_empresas_como_director(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory
    ):
        """Test: Director puede listar empresas"""
        # Arrange
        await empresa_factory()
        await empresa_factory()
        
        # Act
        response = await client.get(
            "/api/v1/empresas",
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2
    
    async def test_listar_empresas_sin_autenticacion(self, client: AsyncClient):
        """Test: No se puede listar empresas sin autenticación"""
        # Act
        response = await client.get("/api/v1/empresas")
        
        # Assert
        assert response.status_code == 401
    
    async def test_crear_empresa_como_director(
        self,
        client: AsyncClient,
        director_token: str,
        tipo_autorizacion_factory
    ):
        """Test: Director puede crear empresa"""
        # Arrange
        tipo_auth = await tipo_autorizacion_factory()
        
        empresa_data = {
            "ruc": "20123456789",
            "razon_social": "Transportes Test SAC",
            "direccion": "Av. Test 123",
            "telefono": "051-123456",
            "email": "test@transportes.com",
            "gerente_id": None,
            "activo": True,
            "autorizaciones": [
                {
                    "tipo_autorizacion_id": str(tipo_auth.id),
                    "numero_resolucion": "RD-2024-001",
                    "fecha_emision": date.today().isoformat(),
                    "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
                    "vigente": True
                }
            ]
        }
        
        # Act
        response = await client.post(
            "/api/v1/empresas",
            json=empresa_data,
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["ruc"] == "20123456789"
        assert data["razon_social"] == "Transportes Test SAC"
        assert len(data["autorizaciones"]) == 1
    
    async def test_crear_empresa_como_operario_denegado(
        self,
        client: AsyncClient,
        operario_token: str
    ):
        """Test: Operario no puede crear empresa"""
        # Arrange
        empresa_data = {
            "ruc": "20123456789",
            "razon_social": "Transportes Test SAC",
            "direccion": "Av. Test 123",
            "telefono": "051-123456",
            "email": "test@transportes.com",
            "gerente_id": None,
            "activo": True,
            "autorizaciones": []
        }
        
        # Act
        response = await client.post(
            "/api/v1/empresas",
            json=empresa_data,
            headers={"Authorization": f"Bearer {operario_token}"}
        )
        
        # Assert
        assert response.status_code == 403
    
    async def test_crear_empresa_ruc_duplicado(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory
    ):
        """Test: No se puede crear empresa con RUC duplicado"""
        # Arrange
        empresa_existente = await empresa_factory(ruc="20123456789")
        
        empresa_data = {
            "ruc": "20123456789",
            "razon_social": "Otra Empresa SAC",
            "direccion": "Av. Test 456",
            "telefono": "051-654321",
            "email": "otra@transportes.com",
            "gerente_id": None,
            "activo": True,
            "autorizaciones": []
        }
        
        # Act
        response = await client.post(
            "/api/v1/empresas",
            json=empresa_data,
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "ya está registrado" in data["detail"]["message"].lower()
    
    async def test_obtener_empresa_por_id(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory
    ):
        """Test: Obtener empresa por ID"""
        # Arrange
        empresa = await empresa_factory()
        
        # Act
        response = await client.get(
            f"/api/v1/empresas/{empresa.id}",
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(empresa.id)
        assert data["ruc"] == empresa.ruc
    
    async def test_obtener_empresa_no_existe(
        self,
        client: AsyncClient,
        director_token: str
    ):
        """Test: Error al obtener empresa inexistente"""
        # Arrange
        from uuid import uuid4
        empresa_id = str(uuid4())
        
        # Act
        response = await client.get(
            f"/api/v1/empresas/{empresa_id}",
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 404
    
    async def test_actualizar_empresa(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory
    ):
        """Test: Actualizar empresa"""
        # Arrange
        empresa = await empresa_factory()
        
        update_data = {
            "razon_social": "Transportes Actualizado SAC",
            "direccion": "Nueva Dirección 789"
        }
        
        # Act
        response = await client.put(
            f"/api/v1/empresas/{empresa.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["razon_social"] == "Transportes Actualizado SAC"
        assert data["direccion"] == "Nueva Dirección 789"
    
    async def test_actualizar_empresa_como_operario_denegado(
        self,
        client: AsyncClient,
        operario_token: str,
        empresa_factory
    ):
        """Test: Operario no puede actualizar empresa"""
        # Arrange
        empresa = await empresa_factory()
        
        update_data = {
            "razon_social": "Transportes Actualizado SAC"
        }
        
        # Act
        response = await client.put(
            f"/api/v1/empresas/{empresa.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {operario_token}"}
        )
        
        # Assert
        assert response.status_code == 403
    
    async def test_obtener_conductores_empresa(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory,
        conductor_factory
    ):
        """Test: Obtener conductores de una empresa"""
        # Arrange
        empresa = await empresa_factory()
        await conductor_factory(empresa_id=empresa.id)
        await conductor_factory(empresa_id=empresa.id)
        
        # Act
        response = await client.get(
            f"/api/v1/empresas/{empresa.id}/conductores",
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    async def test_agregar_autorizacion_a_empresa(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test: Agregar autorización a empresa"""
        # Arrange
        empresa = await empresa_factory()
        tipo_auth = await tipo_autorizacion_factory()
        
        autorizacion_data = {
            "tipo_autorizacion_id": str(tipo_auth.id),
            "numero_resolucion": "RD-2024-002",
            "fecha_emision": date.today().isoformat(),
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "vigente": True
        }
        
        # Act
        response = await client.post(
            f"/api/v1/empresas/{empresa.id}/autorizaciones",
            json=autorizacion_data,
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["numero_resolucion"] == "RD-2024-002"
        assert data["empresa_id"] == str(empresa.id)
    
    async def test_agregar_autorizacion_como_operario_denegado(
        self,
        client: AsyncClient,
        operario_token: str,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test: Operario no puede agregar autorización"""
        # Arrange
        empresa = await empresa_factory()
        tipo_auth = await tipo_autorizacion_factory()
        
        autorizacion_data = {
            "tipo_autorizacion_id": str(tipo_auth.id),
            "numero_resolucion": "RD-2024-003",
            "fecha_emision": date.today().isoformat(),
            "fecha_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "vigente": True
        }
        
        # Act
        response = await client.post(
            f"/api/v1/empresas/{empresa.id}/autorizaciones",
            json=autorizacion_data,
            headers={"Authorization": f"Bearer {operario_token}"}
        )
        
        # Assert
        assert response.status_code == 403
    
    async def test_listar_empresas_con_paginacion(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory
    ):
        """Test: Listar empresas con paginación"""
        # Arrange
        for _ in range(5):
            await empresa_factory()
        
        # Act
        response = await client.get(
            "/api/v1/empresas?skip=0&limit=2",
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5
        assert data["page"] == 1
        assert data["page_size"] == 2
    
    async def test_listar_empresas_con_filtro_activo(
        self,
        client: AsyncClient,
        director_token: str,
        empresa_factory
    ):
        """Test: Listar empresas filtradas por estado activo"""
        # Arrange
        await empresa_factory(activo=True)
        await empresa_factory(activo=True)
        await empresa_factory(activo=False)
        
        # Act
        response = await client.get(
            "/api/v1/empresas?activo=true",
            headers={"Authorization": f"Bearer {director_token}"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(item["activo"] for item in data["items"])
