"""
Repositorio para Empresa
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.empresa import Empresa, AutorizacionEmpresa, TipoAutorizacion
from app.repositories.base import BaseRepository


class EmpresaRepository(BaseRepository[Empresa]):
    """Repositorio específico para Empresa"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Empresa, db)
    
    async def get_by_id(self, id: UUID) -> Optional[Empresa]:
        """
        Obtener empresa por ID con autorizaciones cargadas
        
        Args:
            id: ID de la empresa
            
        Returns:
            Empresa o None si no existe
        """
        result = await self.db.execute(
            select(Empresa)
            .options(
                selectinload(Empresa.autorizaciones).selectinload(AutorizacionEmpresa.tipo_autorizacion)
            )
            .where(Empresa.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        order_by: Optional[str] = None
    ) -> List[Empresa]:
        """
        Obtener todas las empresas con autorizaciones cargadas
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            filters: Filtros opcionales
            order_by: Campo para ordenar
            
        Returns:
            Lista de empresas
        """
        query = select(self.model).options(
            selectinload(Empresa.autorizaciones).selectinload(AutorizacionEmpresa.tipo_autorizacion)
        )
        
        # Aplicar filtros
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        # Aplicar ordenamiento
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())
    
    async def get_by_ruc(self, ruc: str) -> Optional[Empresa]:
        """
        Obtener empresa por RUC
        
        Args:
            ruc: RUC de la empresa
            
        Returns:
            Empresa o None si no existe
        """
        result = await self.db.execute(
            select(Empresa)
            .options(
                selectinload(Empresa.autorizaciones).selectinload(AutorizacionEmpresa.tipo_autorizacion),
                selectinload(Empresa.gerente)
            )
            .where(Empresa.ruc == ruc)
        )
        return result.scalar_one_or_none()
    
    async def ruc_exists(self, ruc: str) -> bool:
        """
        Verificar si existe un RUC
        
        Args:
            ruc: RUC a verificar
            
        Returns:
            True si existe, False si no
        """
        return await self.exists_by_field("ruc", ruc)
    
    async def get_by_gerente(self, gerente_id: UUID) -> Optional[Empresa]:
        """
        Obtener empresa por gerente
        
        Args:
            gerente_id: ID del gerente
            
        Returns:
            Empresa o None si no existe
        """
        result = await self.db.execute(
            select(Empresa)
            .options(
                selectinload(Empresa.autorizaciones).selectinload(AutorizacionEmpresa.tipo_autorizacion)
            )
            .where(Empresa.gerente_id == gerente_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_autorizaciones(self, empresa_id: UUID) -> Optional[Empresa]:
        """
        Obtener empresa con sus autorizaciones cargadas
        
        Args:
            empresa_id: ID de la empresa
            
        Returns:
            Empresa con autorizaciones o None
        """
        result = await self.db.execute(
            select(Empresa)
            .options(
                selectinload(Empresa.autorizaciones).selectinload(AutorizacionEmpresa.tipo_autorizacion)
            )
            .where(Empresa.id == empresa_id)
        )
        return result.scalar_one_or_none()
    
    async def get_empresas_activas(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Empresa]:
        """
        Obtener empresas activas
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de empresas activas
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"activo": True},
            order_by="razon_social"
        )
    
    async def get_empresas_con_autorizacion(
        self,
        tipo_autorizacion_codigo: str
    ) -> List[Empresa]:
        """
        Obtener empresas que tienen un tipo específico de autorización vigente
        
        Args:
            tipo_autorizacion_codigo: Código del tipo de autorización
            
        Returns:
            Lista de empresas
        """
        result = await self.db.execute(
            select(Empresa)
            .join(Empresa.autorizaciones)
            .join(AutorizacionEmpresa.tipo_autorizacion)
            .where(
                TipoAutorizacion.codigo == tipo_autorizacion_codigo,
                AutorizacionEmpresa.vigente == True,
                Empresa.activo == True
            )
            .options(
                selectinload(Empresa.autorizaciones).selectinload(AutorizacionEmpresa.tipo_autorizacion)
            )
        )
        return list(result.scalars().unique().all())
