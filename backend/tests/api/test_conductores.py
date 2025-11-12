"""
Tests de integración para endpoints de conductores
"""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient
from app.models.user import RolUsuario
from app.models.conductor import EstadoConductor


@pytest.mark.asyncio
class TestConductoresEndpoints:
    """Tests para endpoints de conductores"""
    
    async def test_crear_conductor_como_gerente(
        self,
        client: AsyncClient,
        db_session,
        usuario_gerente,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test crear conductor como gerente"""
        # Crear empresa y asignar gerente
        tipo_auth = await tipo_autorizacion_factory(codigo="MERCANCIAS")
        empresa = await empresa_factory.create_with_autorizacion(tipo_auth, gerente_id=usuario_gerente.id)
        
        # Crear token para gerente
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(usuario_gerente.id),
            "email": usuario_gerente.email,
            "rol": usuario_gerente.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        conductor_data = {
            "dni": "12345678",
            "nombres": "Juan Carlos",
            "apellidos": "Pérez García",
            "fecha_nacimiento": "1990-05-15",
            "direccion": "Av. Principal 123, Puno",
            "telefono": "987654321",
            "email": "juan.perez@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": "2020-01-01",
            "licencia_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "empresa_id": str(empresa.id)
        }
        
        response = await client.post(
            "/api/v1/conductores",
            json=conductor_data,
            headers=headers
        )
        
        if response.status_code != 201:
            print(f"Error response: {response.json()}")
        
        assert response.status_code == 201
        data = response.json()
        assert data["dni"] == "12345678"
        assert data["estado"] == "pendiente"
    
    async def test_crear_conductor_gerente_otra_empresa_falla(
        self,
        client: AsyncClient,
        db_session,
        usuario_gerente,
        empresa_factory,
        tipo_autorizacion_factory
    ):
        """Test gerente no puede crear conductor para otra empresa"""
        # Crear empresa del gerente
        tipo_auth = await tipo_autorizacion_factory(codigo="MERCANCIAS")
        empresa_gerente = await empresa_factory.create_with_autorizacion(tipo_auth, gerente_id=usuario_gerente.id)
        
        # Crear otra empresa
        empresa_otra = await empresa_factory.create_with_autorizacion(tipo_auth)
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(usuario_gerente.id),
            "email": usuario_gerente.email,
            "rol": usuario_gerente.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        conductor_data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": "1990-05-15",
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": "2020-01-01",
            "licencia_vencimiento": (date.today() + timedelta(days=365)).isoformat(),
            "empresa_id": str(empresa_otra.id)  # Otra empresa
        }
        
        response = await client.post(
            "/api/v1/conductores",
            json=conductor_data,
            headers=headers
        )
        
        assert response.status_code == 403
    
    async def test_listar_conductores_como_director(
        self,
        client: AsyncClient,
        db_session,
        director_usuario,
        conductor_factory
    ):
        """Test listar conductores como director"""
        # Crear algunos conductores
        await conductor_factory(dni="11111111")
        await conductor_factory(dni="22222222")
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            "/api/v1/conductores",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 2
    
    async def test_listar_conductores_como_gerente_solo_su_empresa(
        self,
        client: AsyncClient,
        db_session,
        usuario_gerente,
        empresa_factory,
        conductor_factory
    ):
        """Test gerente solo ve conductores de su empresa"""
        # Crear empresa del gerente
        empresa_gerente = await empresa_factory(gerente_id=usuario_gerente.id)
        
        # Crear conductores de su empresa
        await conductor_factory(empresa_id=empresa_gerente.id, dni="11111111")
        await conductor_factory(empresa_id=empresa_gerente.id, dni="22222222")
        
        # Crear conductor de otra empresa
        await conductor_factory(dni="33333333")
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(usuario_gerente.id),
            "email": usuario_gerente.email,
            "rol": usuario_gerente.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            "/api/v1/conductores",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Solo debe ver los 2 conductores de su empresa
        assert len(data["items"]) == 2
        assert all(c["empresa_id"] == str(empresa_gerente.id) for c in data["items"])
    
    async def test_obtener_conductor_por_id(
        self,
        client: AsyncClient,
        db_session,
        director_usuario,
        conductor_factory
    ):
        """Test obtener conductor por ID"""
        conductor = await conductor_factory(dni="12345678")
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            f"/api/v1/conductores/{conductor.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["dni"] == "12345678"
    
    async def test_obtener_conductor_por_dni(
        self,
        client: AsyncClient,
        db_session,
        director_usuario,
        conductor_factory
    ):
        """Test obtener conductor por DNI"""
        conductor = await conductor_factory(dni="12345678")
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            "/api/v1/conductores/dni/12345678",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["dni"] == "12345678"
    
    async def test_actualizar_conductor(
        self,
        client: AsyncClient,
        db_session,
        director_usuario,
        conductor_factory
    ):
        """Test actualizar conductor"""
        conductor = await conductor_factory()
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {
            "telefono": "999888777",
            "email": "nuevo@example.com"
        }
        
        response = await client.put(
            f"/api/v1/conductores/{conductor.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["telefono"] == "999888777"
        assert data["email"] == "nuevo@example.com"
    
    async def test_cambiar_estado_conductor(
        self,
        client: AsyncClient,
        db_session,
        director_usuario,
        conductor_factory
    ):
        """Test cambiar estado de conductor"""
        conductor = await conductor_factory(estado=EstadoConductor.PENDIENTE)
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        estado_data = {
            "estado": "habilitado",
            "observacion": "Conductor habilitado correctamente"
        }
        
        response = await client.put(
            f"/api/v1/conductores/{conductor.id}/estado",
            json=estado_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "habilitado"
    
    async def test_eliminar_conductor(
        self,
        client: AsyncClient,
        db_session,
        superusuario_usuario,
        conductor_factory
    ):
        """Test eliminar conductor"""
        conductor = await conductor_factory(estado=EstadoConductor.PENDIENTE)
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(superusuario_usuario.id),
            "email": superusuario_usuario.email,
            "rol": superusuario_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.delete(
            f"/api/v1/conductores/{conductor.id}",
            headers=headers
        )
        
        assert response.status_code == 204
    
    async def test_validar_categoria_licencia(
        self,
        client: AsyncClient,
        db_session,
        director_usuario
    ):
        """Test validar categoría de licencia"""
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        validacion_data = {
            "licencia_categoria": "A-IIIb",
            "tipo_autorizacion_codigo": "MERCANCIAS"
        }
        
        response = await client.post(
            "/api/v1/conductores/validar-categoria",
            json=validacion_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valido"] is True
        assert "A-IIIb" in data["categorias_requeridas"]
    
    async def test_buscar_conductores_por_estado(
        self,
        client: AsyncClient,
        db_session,
        director_usuario,
        conductor_factory
    ):
        """Test buscar conductores por estado"""
        await conductor_factory(estado=EstadoConductor.HABILITADO)
        await conductor_factory(estado=EstadoConductor.PENDIENTE)
        
        from app.core.security import create_access_token
        token = create_access_token({
            "sub": str(director_usuario.id),
            "email": director_usuario.email,
            "rol": director_usuario.rol.value
        })
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.get(
            "/api/v1/conductores?estado=habilitado",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(c["estado"] == "habilitado" for c in data["items"])
