"""
Tests para BaseRepository
"""
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.user import Usuario


@pytest.mark.asyncio
class TestBaseRepository:
    """Tests para operaciones CRUD del BaseRepository"""
    
    async def test_create(self, db_session: AsyncSession):
        """Test crear registro"""
        repo = BaseRepository(Usuario, db_session)
        
        user_data = {
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "nombres": "Test",
            "apellidos": "User",
            "rol": "operario",
            "activo": True
        }
        
        user = await repo.create(user_data)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.nombres == "Test"
        assert user.apellidos == "User"
        assert user.rol.value == "operario"
        assert user.activo is True
    
    async def test_get_by_id(self, db_session: AsyncSession):
        """Test obtener registro por ID"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuario
        user_data = {
            "email": "test2@example.com",
            "password_hash": "hashed_password",
            "nombres": "Test2",
            "apellidos": "User2",
            "rol": "operario",
            "activo": True
        }
        created_user = await repo.create(user_data)
        await db_session.commit()
        
        # Obtener por ID
        found_user = await repo.get_by_id(created_user.id)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test2@example.com"
    
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        """Test obtener registro que no existe"""
        repo = BaseRepository(Usuario, db_session)
        
        non_existent_id = uuid4()
        found_user = await repo.get_by_id(non_existent_id)
        
        assert found_user is None
    
    async def test_get_all(self, db_session: AsyncSession):
        """Test obtener todos los registros"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear varios usuarios
        for i in range(5):
            user_data = {
                "email": f"user{i}@example.com",
                "password_hash": "hashed_password",
                "nombres": f"User{i}",
                "apellidos": f"Test{i}",
                "rol": "operario",
                "activo": True
            }
            await repo.create(user_data)
        await db_session.commit()
        
        # Obtener todos
        users = await repo.get_all()
        
        assert len(users) >= 5
    
    async def test_get_all_with_pagination(self, db_session: AsyncSession):
        """Test paginación"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear varios usuarios
        for i in range(10):
            user_data = {
                "email": f"paginated{i}@example.com",
                "password_hash": "hashed_password",
                "nombres": f"Paginated{i}",
                "apellidos": f"User{i}",
                "rol": "operario",
                "activo": True
            }
            await repo.create(user_data)
        await db_session.commit()
        
        # Primera página
        page1 = await repo.get_all(skip=0, limit=5)
        assert len(page1) == 5
        
        # Segunda página
        page2 = await repo.get_all(skip=5, limit=5)
        assert len(page2) == 5
        
        # No deben tener elementos en común
        page1_ids = {user.id for user in page1}
        page2_ids = {user.id for user in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    async def test_get_all_with_filters(self, db_session: AsyncSession):
        """Test filtrado"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuarios con diferentes roles
        await repo.create({
            "email": "director@example.com",
            "password_hash": "hashed",
            "nombres": "Director",
            "apellidos": "Test",
            "rol": "director",
            "activo": True
        })
        
        await repo.create({
            "email": "operario@example.com",
            "password_hash": "hashed",
            "nombres": "Operario",
            "apellidos": "Test",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Filtrar por rol
        directors = await repo.get_all(filters={"rol": "director"})
        
        assert len(directors) >= 1
        assert all(user.rol.value == "director" for user in directors)
    
    async def test_get_all_with_like_filter(self, db_session: AsyncSession):
        """Test filtrado con LIKE"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuarios
        await repo.create({
            "email": "john.doe@example.com",
            "password_hash": "hashed",
            "nombres": "John",
            "apellidos": "Doe",
            "rol": "operario",
            "activo": True
        })
        
        await repo.create({
            "email": "jane.smith@example.com",
            "password_hash": "hashed",
            "nombres": "Jane",
            "apellidos": "Smith",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Buscar con LIKE
        johns = await repo.get_all(filters={"nombres": {"like": "John"}})
        
        assert len(johns) >= 1
        assert any("John" in user.nombres for user in johns)
    
    async def test_get_all_with_ordering(self, db_session: AsyncSession):
        """Test ordenamiento"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuarios
        await repo.create({
            "email": "zebra@example.com",
            "password_hash": "hashed",
            "nombres": "Zebra",
            "apellidos": "Last",
            "rol": "operario",
            "activo": True
        })
        
        await repo.create({
            "email": "alpha@example.com",
            "password_hash": "hashed",
            "nombres": "Alpha",
            "apellidos": "First",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Ordenar ascendente
        users_asc = await repo.get_all(order_by="nombres", order_desc=False)
        assert users_asc[0].nombres <= users_asc[-1].nombres
        
        # Ordenar descendente
        users_desc = await repo.get_all(order_by="nombres", order_desc=True)
        assert users_desc[0].nombres >= users_desc[-1].nombres
    
    async def test_update(self, db_session: AsyncSession):
        """Test actualizar registro"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuario
        user = await repo.create({
            "email": "update@example.com",
            "password_hash": "hashed",
            "nombres": "Original",
            "apellidos": "Name",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Actualizar
        updated_user = await repo.update(user.id, {"nombres": "Updated"})
        await db_session.commit()
        
        assert updated_user is not None
        assert updated_user.nombres == "Updated"
        assert updated_user.apellidos == "Name"  # No cambió
    
    async def test_update_not_found(self, db_session: AsyncSession):
        """Test actualizar registro que no existe"""
        repo = BaseRepository(Usuario, db_session)
        
        non_existent_id = uuid4()
        result = await repo.update(non_existent_id, {"nombres": "Test"})
        
        assert result is None
    
    async def test_delete(self, db_session: AsyncSession):
        """Test eliminar registro"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuario
        user = await repo.create({
            "email": "delete@example.com",
            "password_hash": "hashed",
            "nombres": "Delete",
            "apellidos": "Me",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Eliminar
        result = await repo.delete(user.id)
        await db_session.commit()
        
        assert result is True
        
        # Verificar que no existe
        found = await repo.get_by_id(user.id)
        assert found is None
    
    async def test_delete_not_found(self, db_session: AsyncSession):
        """Test eliminar registro que no existe"""
        repo = BaseRepository(Usuario, db_session)
        
        non_existent_id = uuid4()
        result = await repo.delete(non_existent_id)
        
        assert result is False
    
    async def test_exists(self, db_session: AsyncSession):
        """Test verificar existencia"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuario
        user = await repo.create({
            "email": "exists@example.com",
            "password_hash": "hashed",
            "nombres": "Exists",
            "apellidos": "Test",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Verificar que existe
        exists = await repo.exists(user.id)
        assert exists is True
        
        # Verificar que no existe
        non_existent_id = uuid4()
        not_exists = await repo.exists(non_existent_id)
        assert not_exists is False
    
    async def test_count(self, db_session: AsyncSession):
        """Test contar registros"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuarios
        for i in range(3):
            await repo.create({
                "email": f"count{i}@example.com",
                "password_hash": "hashed",
                "nombres": f"Count{i}",
                "apellidos": "Test",
                "rol": "operario",
                "activo": True
            })
        await db_session.commit()
        
        # Contar todos
        total = await repo.count()
        assert total >= 3
        
        # Contar con filtro
        operarios = await repo.count(filters={"rol": "operario"})
        assert operarios >= 3
    
    async def test_exists_by_field(self, db_session: AsyncSession):
        """Test verificar existencia por campo"""
        repo = BaseRepository(Usuario, db_session)
        
        # Crear usuario
        await repo.create({
            "email": "unique@example.com",
            "password_hash": "hashed",
            "nombres": "Unique",
            "apellidos": "Test",
            "rol": "operario",
            "activo": True
        })
        await db_session.commit()
        
        # Verificar que existe por email
        exists = await repo.exists_by_field("email", "unique@example.com")
        assert exists is True
        
        # Verificar que no existe
        not_exists = await repo.exists_by_field("email", "nonexistent@example.com")
        assert not_exists is False
