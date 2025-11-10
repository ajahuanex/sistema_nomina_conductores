"""
Repositorio para Usuario
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """Repositorio específico para Usuario"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Usuario, db)
    
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """
        Obtener usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario o None si no existe
        """
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        """
        Verificar si existe un email
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False si no
        """
        return await self.exists_by_field("email", email)
    
    async def get_by_rol(self, rol: str, activo: bool = True) -> list[Usuario]:
        """
        Obtener usuarios por rol
        
        Args:
            rol: Rol del usuario
            activo: Si True, solo usuarios activos
            
        Returns:
            Lista de usuarios
        """
        filters = {"rol": rol}
        if activo:
            filters["activo"] = True
        
        return await self.get_all(filters=filters)
    
    async def get_gerentes_sin_empresa(self) -> list[Usuario]:
        """
        Obtener gerentes que no tienen empresa asignada
        
        Returns:
            Lista de gerentes sin empresa
        """
        result = await self.db.execute(
            select(Usuario).where(
                Usuario.rol == "gerente",
                Usuario.empresa_id.is_(None),
                Usuario.activo == True
            )
        )
        return list(result.scalars().all())
