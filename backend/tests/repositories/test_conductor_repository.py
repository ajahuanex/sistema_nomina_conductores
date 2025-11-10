"""
Tests para ConductorRepository
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.conductor_repository import ConductorRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.models.conductor import EstadoConductor


@pytest.mark.asyncio
class TestConductorRepository:
    """Tests para ConductorRepository"""
    
    async def test_get_by_dni(self, db_session: AsyncSession):
        """Test obtener conductor por DNI"""
        empresa_repo = EmpresaRepository(db_session)
        conductor_repo = ConductorRepository(db_session)
        
        # Crear empresa
        empresa = await empresa_repo.create({
            "ruc": "20444444444",
            "razon_social": "Empresa Test SAC",
            "direccion": "Av. Test 123",
            "telefono": "987654321",
            "email": "test@empresa.com",
            "activo": True
        })
        await db_session.flush()
        
        # Crear conductor
        await conductor_repo.create({
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 1, 1),
            "direccion": "Jr. Test 456",
            "telefono": "987654321",
            "email": "juan@test.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa.id,
            "estado": "pendiente"
        })
        await db_session.commit()
        
        # Obtener por DNI
        conductor = await conductor_repo.get_by_dni("12345678")
        
        assert conductor is not None
        assert conductor.dni == "12345678"
        assert conductor.nombres == "Juan"
    
    async def test_dni_exists(self, db_session: AsyncSession):
        """Test verificar si existe DNI"""
        empresa_repo = EmpresaRepository(db_session)
        conductor_repo = ConductorRepository(db_session)
        
        # Crear empresa
        empresa = await empresa_repo.create({
            "ruc": "20555555555",
            "razon_social": "Empresa Test 2 SAC",
            "direccion": "Av. Test 789",
            "telefono": "987654321",
            "email": "test2@empresa.com",
            "activo": True
        })
        await db_session.flush()
        
        # Crear conductor
        await conductor_repo.create({
            "dni": "87654321",
            "nombres": "María",
            "apellidos": "García",
            "fecha_nacimiento": date(1992, 5, 15),
            "direccion": "Jr. Test 789",
            "telefono": "987654321",
            "email": "maria@test.com",
            "licencia_numero": "Q87654321",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2021, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa.id,
            "estado": "pendiente"
        })
        await db_session.commit()
        
        # Verificar que existe
        exists = await conductor_repo.dni_exists("87654321")
        assert exists is True
        
        # Verificar que no existe
        not_exists = await conductor_repo.dni_exists("00000000")
        assert not_exists is False
    
    async def test_get_by_estado(self, db_session: AsyncSession):
        """Test obtener conductores por estado"""
        empresa_repo = EmpresaRepository(db_session)
        conductor_repo = ConductorRepository(db_session)
        
        # Crear empresa
        empresa = await empresa_repo.create({
            "ruc": "20666666666",
            "razon_social": "Empresa Test 3 SAC",
            "direccion": "Av. Test 999",
            "telefono": "987654321",
            "email": "test3@empresa.com",
            "activo": True
        })
        await db_session.flush()
        
        # Crear conductor habilitado
        await conductor_repo.create({
            "dni": "11111111",
            "nombres": "Pedro",
            "apellidos": "López",
            "fecha_nacimiento": date(1988, 3, 20),
            "direccion": "Jr. Test 111",
            "telefono": "987654321",
            "email": "pedro@test.com",
            "licencia_numero": "Q11111111",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2019, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa.id,
            "estado": "habilitado"
        })
        await db_session.commit()
        
        # Obtener habilitados
        habilitados = await conductor_repo.get_by_estado(EstadoConductor.HABILITADO)
        
        assert len(habilitados) >= 1
        assert all(c.estado == EstadoConductor.HABILITADO for c in habilitados)
    
    async def test_buscar_conductores(self, db_session: AsyncSession):
        """Test búsqueda avanzada de conductores"""
        empresa_repo = EmpresaRepository(db_session)
        conductor_repo = ConductorRepository(db_session)
        
        # Crear empresa
        empresa = await empresa_repo.create({
            "ruc": "20777777777",
            "razon_social": "Empresa Test 4 SAC",
            "direccion": "Av. Test 888",
            "telefono": "987654321",
            "email": "test4@empresa.com",
            "activo": True
        })
        await db_session.flush()
        
        # Crear conductor
        await conductor_repo.create({
            "dni": "22222222",
            "nombres": "Carlos",
            "apellidos": "Rodríguez",
            "fecha_nacimiento": date(1985, 7, 10),
            "direccion": "Jr. Test 222",
            "telefono": "987654321",
            "email": "carlos@test.com",
            "licencia_numero": "Q22222222",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2018, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa.id,
            "estado": "pendiente"
        })
        await db_session.commit()
        
        # Buscar por nombre
        resultados = await conductor_repo.buscar_conductores(texto_busqueda="Carlos")
        
        assert len(resultados) >= 1
        assert any("Carlos" in c.nombres for c in resultados)
