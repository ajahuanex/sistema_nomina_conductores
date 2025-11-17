"""
Tests de integración para endpoints de usuarios
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import RolUsuario
from app.services.usuario_service import UsuarioService
from app.schemas.user import UsuarioCreate


@pytest.mark.asyncio
class TestUsuariosEndpoints:
    """Tests para endpoints de usuarios"""
    
    async def test_listar_usuarios_como_superusuario(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        superusuario_token: str
    ):
        """Test listar usuarios como superusuario"""
        headers = {"Authorization": f"Bearer {superusuario_token}"}
        
        response = await client.get("/api/v1/usuarios", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_listar_usuarios_como_director(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        director_token: str
    ):
        """Test listar usuarios como director"""
        headers = {"Authorization": f"Bearer {director_token}"}
        
        response = await client.get("/api/v1/usuarios", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_listar_usuarios_como_operario_debe_fallar(
        self,
        client: AsyncClient,
        operario_token: str
    ):
        """Test listar usuarios como operario debe fallar"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        response = await client.get("/api/v1/usuarios", headers=headers)
        
        assert response.status_code == 403

    
    async def test_crear_usuario_como_superusuario(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        superusuario_token: str
    ):
        """Test crear usuario como superusuario"""
        headers = {"Authorization": f"Bearer {superusuario_token}"}
        
        usuario_data = {
            "email": "nuevo@drtc.gob.pe",
            "nombres": "Nuevo",
            "apellidos": "Usuario",
            "rol": "OPERARIO",
            "password": "SecurePass123!",
            "activo": True
        }
        
        response = await client.post("/api/v1/usuarios", json=usuario_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nuevo@drtc.gob.pe"
        assert data["nombres"] == "Nuevo"
        assert data["rol"] == "OPERARIO"
    
    async def test_crear_usuario_como_director_debe_fallar(
        self,
        client: AsyncClient,
        director_token: str
    ):
        """Test crear usuario como director debe fallar"""
        headers = {"Authorization": f"Bearer {director_token}"}
        
        usuario_data = {
            "email": "nuevo2@drtc.gob.pe",
            "nombres": "Nuevo",
            "apellidos": "Usuario",
            "rol": "OPERARIO",
            "password": "SecurePass123!",
            "activo": True
        }
        
        response = await client.post("/api/v1/usuarios", json=usuario_data, headers=headers)
        
        assert response.status_code == 403
    
    async def test_crear_usuario_email_duplicado(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        superusuario_token: str
    ):
        """Test crear usuario con email duplicado debe fallar"""
        headers = {"Authorization": f"Bearer {superusuario_token}"}
        
        # Crear primer usuario
        service = UsuarioService(db_session)
        usuario_data = UsuarioCreate(
            email="duplicado@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        await service.crear_usuario(usuario_data)
        await db_session.commit()
        
        # Intentar crear segundo usuario con mismo email
        usuario_data_dict = {
            "email": "duplicado@drtc.gob.pe",
            "nombres": "Test2",
            "apellidos": "User2",
            "rol": "OPERARIO",
            "password": "SecurePass123!",
            "activo": True
        }
        
        response = await client.post("/api/v1/usuarios", json=usuario_data_dict, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "email" in str(data["detail"])

    
    async def test_obtener_usuario_propio(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        operario_usuario
    ):
        """Test obtener información del propio usuario"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        response = await client.get(f"/api/v1/usuarios/{operario_usuario.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == operario_usuario.email
    
    async def test_obtener_usuario_otro_como_operario_debe_fallar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        superusuario_usuario
    ):
        """Test obtener otro usuario como operario debe fallar"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        response = await client.get(f"/api/v1/usuarios/{superusuario_usuario.id}", headers=headers)
        
        assert response.status_code == 403
    
    async def test_obtener_usuario_como_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        superusuario_token: str,
        operario_usuario
    ):
        """Test obtener cualquier usuario como admin"""
        headers = {"Authorization": f"Bearer {superusuario_token}"}
        
        response = await client.get(f"/api/v1/usuarios/{operario_usuario.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == operario_usuario.email
    
    async def test_actualizar_usuario_propio(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        operario_usuario
    ):
        """Test actualizar información del propio usuario"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        update_data = {
            "nombres": "Nombre Actualizado",
            "apellidos": "Apellido Actualizado"
        }
        
        response = await client.put(
            f"/api/v1/usuarios/{operario_usuario.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["nombres"] == "Nombre Actualizado"
        assert data["apellidos"] == "Apellido Actualizado"
    
    async def test_actualizar_rol_propio_debe_fallar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        operario_usuario
    ):
        """Test actualizar propio rol debe fallar"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        update_data = {
            "rol": "DIRECTOR"
        }
        
        response = await client.put(
            f"/api/v1/usuarios/{operario_usuario.id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 403

    
    async def test_eliminar_usuario_como_admin(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        superusuario_token: str
    ):
        """Test eliminar usuario como admin"""
        headers = {"Authorization": f"Bearer {superusuario_token}"}
        
        # Crear usuario para eliminar
        service = UsuarioService(db_session)
        usuario_data = UsuarioCreate(
            email="paraeliminar@drtc.gob.pe",
            nombres="Para",
            apellidos="Eliminar",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        usuario = await service.crear_usuario(usuario_data)
        await db_session.commit()
        
        response = await client.delete(f"/api/v1/usuarios/{usuario.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "desactivado" in data["message"].lower()
    
    async def test_eliminar_usuario_como_operario_debe_fallar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        director_usuario
    ):
        """Test eliminar usuario como operario debe fallar"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        response = await client.delete(f"/api/v1/usuarios/{director_usuario.id}", headers=headers)
        
        assert response.status_code == 403
    
    async def test_eliminar_propio_usuario_debe_fallar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        superusuario_token: str,
        superusuario_usuario
    ):
        """Test eliminar propio usuario debe fallar"""
        headers = {"Authorization": f"Bearer {superusuario_token}"}
        
        response = await client.delete(f"/api/v1/usuarios/{superusuario_usuario.id}", headers=headers)
        
        assert response.status_code == 400
    
    async def test_cambiar_password(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        operario_usuario
    ):
        """Test cambiar contraseña"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        password_data = {
            "password_actual": "operario123!",
            "password_nueva": "NewPassword456!",
            "password_confirmacion": "NewPassword456!"
        }
        
        response = await client.post(
            f"/api/v1/usuarios/{operario_usuario.id}/cambiar-password",
            json=password_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "contraseña" in data["message"].lower()
    
    async def test_cambiar_password_otro_usuario_debe_fallar(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        operario_token: str,
        director_usuario
    ):
        """Test cambiar contraseña de otro usuario debe fallar"""
        headers = {"Authorization": f"Bearer {operario_token}"}
        
        password_data = {
            "password_actual": "director123!",
            "password_nueva": "NewPassword456!",
            "password_confirmacion": "NewPassword456!"
        }
        
        response = await client.post(
            f"/api/v1/usuarios/{director_usuario.id}/cambiar-password",
            json=password_data,
            headers=headers
        )
        
        assert response.status_code == 403
