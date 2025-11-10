"""
Tests para UsuarioRepository
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.usuario_repository import UsuarioRepository
from app.models.user import RolUsuario


@pytest.mark.asyncio
class TestUsuarioRepository:
    """Tests para UsuarioRepository"""
    
    async def test_get_by_email(self, db_session: AsyncSession):
        """Test obtener usuario por email"""
        repo = UsuarioRepository(db_session)
        
        # Crear usuario
        await repo.create({
            "email": "test@example.com",
            "password_hash": "hashed",
            "nombres": "Test",
            "apellidos": "User",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Obtener por email
        user = await repo.get_by_email("test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"
        assert user.nombres == "Test"
    
    async def test_get_by_email_not_found(self, db_session: AsyncSession):
        """Test obtener usuario por email que no existe"""
        repo = UsuarioRepository(db_session)
        
        user = await repo.get_by_email("nonexistent@example.com")
        
        assert user is None
    
    async def test_email_exists(self, db_session: AsyncSession):
        """Test verificar si existe email"""
        repo = UsuarioRepository(db_session)
        
        # Crear usuario
        await repo.create({
            "email": "exists@example.com",
            "password_hash": "hashed",
            "nombres": "Exists",
            "apellidos": "User",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Verificar que existe
        exists = await repo.email_exists("exists@example.com")
        assert exists is True
        
        # Verificar que no existe
        not_exists = await repo.email_exists("notexists@example.com")
        assert not_exists is False
    
    async def test_get_by_rol(self, db_session: AsyncSession):
        """Test obtener usuarios por rol"""
        repo = UsuarioRepository(db_session)
        
        # Crear usuarios con diferentes roles
        await repo.create({
            "email": "director1@example.com",
            "password_hash": "hashed",
            "nombres": "Director",
            "apellidos": "One",
            "rol": "director",
            "activo": True
        })
        
        await repo.create({
            "email": "operario1@example.com",
            "password_hash": "hashed",
            "nombres": "Operario",
            "apellidos": "One",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Obtener directores
        directores = await repo.get_by_rol("director")
        
        assert len(directores) >= 1
        assert all(user.rol.value == "director" for user in directores)
    
    async def test_get_gerentes_sin_empresa(self, db_session: AsyncSession):
        """Test obtener gerentes sin empresa asignada"""
        repo = UsuarioRepository(db_session)
        
        # Crear gerente sin empresa
        await repo.create({
            "email": "gerente@example.com",
            "password_hash": "hashed",
            "nombres": "Gerente",
            "apellidos": "Test",
            "rol": "gerente",
            "activo": True,
            "empresa_id": None
        })
        await db_session.commit()
        
        # Obtener gerentes sin empresa
        gerentes = await repo.get_gerentes_sin_empresa()
        
        assert len(gerentes) >= 1
        assert all(user.rol.value == "gerente" for user in gerentes)
        assert all(user.empresa_id is None for user in gerentes)
