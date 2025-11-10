"""
Tests para configuración de base de datos y Alembic
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.models.base import BaseModel


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test que la conexión a base de datos funciona"""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_base_model_has_required_fields(db_session: AsyncSession):
    """Test que BaseModel tiene los campos requeridos"""
    # Verificar que BaseModel tiene los campos esperados
    assert hasattr(BaseModel, 'id')
    assert hasattr(BaseModel, 'created_at')
    assert hasattr(BaseModel, 'updated_at')


@pytest.mark.asyncio
async def test_base_metadata_exists():
    """Test que Base.metadata está configurado correctamente"""
    assert Base.metadata is not None
    assert hasattr(Base.metadata, 'tables')


@pytest.mark.asyncio
async def test_session_commit_rollback(db_session: AsyncSession):
    """Test que las transacciones funcionan correctamente"""
    # Este test verifica que la sesión puede hacer commit y rollback
    try:
        await db_session.execute(text("SELECT 1"))
        await db_session.commit()
    except Exception as e:
        await db_session.rollback()
        pytest.fail(f"Session commit/rollback failed: {e}")
