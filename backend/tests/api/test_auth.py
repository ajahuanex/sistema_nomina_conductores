"""
Tests de integración para endpoints de autenticación
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Usuario, RolUsuario
from app.core.security import hash_password, create_access_token, create_refresh_token


@pytest.mark.asyncio
class TestLogin:
    """Tests para el endpoint de login"""
    
    async def test_login_successful(self, client: AsyncClient, test_user: Usuario):
        """Test de login exitoso con credenciales válidas"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_with_invalid_email(self, client: AsyncClient):
        """Test de login con email inexistente"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "noexiste@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]
    
    async def test_login_with_invalid_password(self, client: AsyncClient, test_user: Usuario):
        """Test de login con contraseña incorrecta"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Email o contraseña incorrectos" in response.json()["detail"]
    
    async def test_login_with_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test de login con usuario inactivo"""
        # Crear usuario inactivo
        inactive_user = Usuario(
            email="inactive@example.com",
            password_hash=hash_password("password123"),
            nombres="Usuario",
            apellidos="Inactivo",
            rol=RolUsuario.OPERARIO,
            activo=False
        )
        db_session.add(inactive_user)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 403
        assert "Usuario inactivo" in response.json()["detail"]
    
    async def test_login_with_invalid_email_format(self, client: AsyncClient):
        """Test de login con formato de email inválido"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    async def test_login_with_short_password(self, client: AsyncClient):
        """Test de login con contraseña muy corta"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestRefreshToken:
    """Tests para el endpoint de refresh token"""
    
    async def test_refresh_token_successful(self, client: AsyncClient, test_user: Usuario):
        """Test de refresh token exitoso"""
        # Crear un refresh token válido
        refresh_token = create_refresh_token({
            "sub": str(test_user.id),
            "email": test_user.email
        })
        
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_with_invalid_token(self, client: AsyncClient):
        """Test de refresh token con token inválido"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "inválido" in response.json()["detail"].lower()
    
    async def test_refresh_token_with_access_token(self, client: AsyncClient, test_user: Usuario):
        """Test de refresh token usando un access token (debe fallar)"""
        # Crear un access token en lugar de refresh token
        access_token = create_access_token({
            "sub": str(test_user.id),
            "email": test_user.email,
            "rol": test_user.rol.value
        })
        
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token}
        )
        
        assert response.status_code == 401
    
    async def test_refresh_token_with_inactive_user(self, client: AsyncClient, db_session: AsyncSession):
        """Test de refresh token con usuario inactivo"""
        # Crear usuario inactivo
        inactive_user = Usuario(
            email="inactive2@example.com",
            password_hash=hash_password("password123"),
            nombres="Usuario",
            apellidos="Inactivo",
            rol=RolUsuario.OPERARIO,
            activo=False
        )
        db_session.add(inactive_user)
        await db_session.commit()
        await db_session.refresh(inactive_user)
        
        # Crear refresh token para usuario inactivo
        refresh_token = create_refresh_token({
            "sub": str(inactive_user.id),
            "email": inactive_user.email
        })
        
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 403
        assert "Usuario inactivo" in response.json()["detail"]


@pytest.mark.asyncio
class TestLogout:
    """Tests para el endpoint de logout"""
    
    async def test_logout_successful(self, client: AsyncClient, auth_headers: dict):
        """Test de logout exitoso"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "exitosamente" in response.json()["message"].lower()
    
    async def test_logout_without_authentication(self, client: AsyncClient):
        """Test de logout sin autenticación"""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == 403  # No credentials provided
    
    async def test_logout_with_invalid_token(self, client: AsyncClient):
        """Test de logout con token inválido"""
        response = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Tests para el endpoint /me"""
    
    async def test_get_current_user_successful(self, client: AsyncClient, auth_headers: dict, test_user: Usuario):
        """Test de obtener usuario actual exitoso"""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["nombres"] == test_user.nombres
        assert data["apellidos"] == test_user.apellidos
        assert data["rol"] == test_user.rol.value
        assert data["activo"] is True
    
    async def test_get_current_user_without_authentication(self, client: AsyncClient):
        """Test de obtener usuario actual sin autenticación"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
    
    async def test_get_current_user_with_invalid_token(self, client: AsyncClient):
        """Test de obtener usuario actual con token inválido"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    async def test_get_current_user_with_gerente_includes_empresa_id(
        self, 
        client: AsyncClient, 
        db_session: AsyncSession
    ):
        """Test que un gerente incluye empresa_id en la respuesta"""
        from uuid import uuid4
        
        # Crear un gerente con empresa_id
        empresa_id = uuid4()
        gerente = Usuario(
            email="gerente@example.com",
            password_hash=hash_password("password123"),
            nombres="Gerente",
            apellidos="Test",
            rol=RolUsuario.GERENTE,
            empresa_id=empresa_id,
            activo=True
        )
        db_session.add(gerente)
        await db_session.commit()
        await db_session.refresh(gerente)
        
        # Crear token para el gerente
        access_token = create_access_token({
            "sub": str(gerente.id),
            "email": gerente.email,
            "rol": gerente.rol.value,
            "empresa_id": str(empresa_id)
        })
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["empresa_id"] == str(empresa_id)
        assert data["rol"].upper() == "GERENTE"


@pytest.mark.asyncio
class TestRateLimiting:
    """Tests para rate limiting en login"""
    
    async def test_login_rate_limit(self, client: AsyncClient):
        """Test que el rate limiting funciona en login"""
        # Intentar login más veces que el límite (5 por minuto)
        for i in range(6):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": f"test{i}@example.com",
                    "password": "password123"
                }
            )
            
            if i < 5:
                # Las primeras 5 solicitudes deben pasar (aunque fallen por credenciales)
                assert response.status_code in [401, 422]
            else:
                # La sexta solicitud debe ser bloqueada por rate limit
                assert response.status_code == 429
