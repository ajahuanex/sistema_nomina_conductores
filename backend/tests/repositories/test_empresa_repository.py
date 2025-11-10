"""
Tests para EmpresaRepository
"""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.usuario_repository import UsuarioRepository


@pytest.mark.asyncio
class TestEmpresaRepository:
    """Tests para EmpresaRepository"""
    
    async def test_get_by_ruc(self, db_session: AsyncSession):
        """Test obtener empresa por RUC"""
        repo = EmpresaRepository(db_session)
        
        # Crear empresa
        await repo.create({
            "ruc": "20123456789",
            "razon_social": "Test SAC",
            "direccion": "Av. Test 123",
            "telefono": "987654321",
            "email": "test@empresa.com",
            "activo": True
        })
        await db_session.commit()
        
        # Obtener por RUC
        empresa = await repo.get_by_ruc("20123456789")
        
        assert empresa is not None
        assert empresa.ruc == "20123456789"
        assert empresa.razon_social == "Test SAC"
    
    async def test_ruc_exists(self, db_session: AsyncSession):
        """Test verificar si existe RUC"""
        repo = EmpresaRepository(db_session)
        
        # Crear empresa
        await repo.create({
            "ruc": "20987654321",
            "razon_social": "Exists SAC",
            "direccion": "Av. Exists 456",
            "telefono": "987654321",
            "email": "exists@empresa.com",
            "activo": True
        })
        await db_session.commit()
        
        # Verificar que existe
        exists = await repo.ruc_exists("20987654321")
        assert exists is True
        
        # Verificar que no existe
        not_exists = await repo.ruc_exists("20000000000")
        assert not_exists is False
    
    async def test_get_by_gerente(self, db_session: AsyncSession):
        """Test obtener empresa por gerente"""
        user_repo = UsuarioRepository(db_session)
        empresa_repo = EmpresaRepository(db_session)
        
        # Crear gerente
        gerente = await user_repo.create({
            "email": "gerente@test.com",
            "password_hash": "hashed",
            "nombres": "Gerente",
            "apellidos": "Test",
            "rol": "gerente",
            "activo": True
        })
        await db_session.flush()
        
        # Crear empresa con gerente
        await empresa_repo.create({
            "ruc": "20111111111",
            "razon_social": "Empresa con Gerente SAC",
            "direccion": "Av. Gerente 789",
            "telefono": "987654321",
            "email": "empresa@test.com",
            "gerente_id": gerente.id,
            "activo": True
        })
        await db_session.commit()
        
        # Obtener empresa por gerente
        empresa = await empresa_repo.get_by_gerente(gerente.id)
        
        assert empresa is not None
        assert empresa.gerente_id == gerente.id
    
    async def test_get_empresas_activas(self, db_session: AsyncSession):
        """Test obtener empresas activas"""
        repo = EmpresaRepository(db_session)
        
        # Crear empresa activa
        await repo.create({
            "ruc": "20222222222",
            "razon_social": "Activa SAC",
            "direccion": "Av. Activa 123",
            "telefono": "987654321",
            "email": "activa@empresa.com",
            "activo": True
        })
        
        # Crear empresa inactiva
        await repo.create({
            "ruc": "20333333333",
            "razon_social": "Inactiva SAC",
            "direccion": "Av. Inactiva 456",
            "telefono": "987654321",
            "email": "inactiva@empresa.com",
            "activo": False
        })
        await db_session.commit()
        
        # Obtener solo activas
        empresas = await repo.get_empresas_activas()
        
        assert len(empresas) >= 1
        assert all(empresa.activo for empresa in empresas)
