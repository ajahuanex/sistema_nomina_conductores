"""
Repositorio para Infraccion
"""
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.infraccion import Infraccion, TipoInfraccion, GravedadInfraccion, EstadoInfraccion
from app.repositories.base import BaseRepository


class InfraccionRepository(BaseRepository[Infraccion]):
    """Repositorio específico para Infraccion con consultas de historial"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Infraccion, db)
    
    async def get_by_conductor(
        self,
        conductor_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Infraccion]:
        """
        Obtener historial de infracciones de un conductor
        
        Args:
            conductor_id: ID del conductor
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de infracciones ordenadas por fecha descendente
        """
        result = await self.db.execute(
            select(Infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor)
            )
            .where(Infraccion.conductor_id == conductor_id)
            .order_by(Infraccion.fecha_infraccion.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_numero_acta(self, numero_acta: str) -> Optional[Infraccion]:
        """
        Obtener infracción por número de acta
        
        Args:
            numero_acta: Número de acta
            
        Returns:
            Infraccion o None si no existe
        """
        result = await self.db.execute(
            select(Infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor)
            )
            .where(Infraccion.numero_acta == numero_acta)
        )
        return result.scalar_one_or_none()
    
    async def get_by_gravedad(
        self,
        gravedad: GravedadInfraccion,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Infraccion]:
        """
        Obtener infracciones por gravedad
        
        Args:
            gravedad: Gravedad de la infracción
            fecha_desde: Fecha inicial (opcional)
            fecha_hasta: Fecha final (opcional)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de infracciones
        """
        query = (
            select(Infraccion)
            .join(Infraccion.tipo_infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor)
            )
            .where(TipoInfraccion.gravedad == gravedad)
        )
        
        if fecha_desde:
            query = query.where(Infraccion.fecha_infraccion >= fecha_desde)
        
        if fecha_hasta:
            query = query.where(Infraccion.fecha_infraccion <= fecha_hasta)
        
        query = query.order_by(Infraccion.fecha_infraccion.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_estado(
        self,
        estado: EstadoInfraccion,
        skip: int = 0,
        limit: int = 100
    ) -> List[Infraccion]:
        """
        Obtener infracciones por estado
        
        Args:
            estado: Estado de la infracción
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de infracciones
        """
        result = await self.db.execute(
            select(Infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor)
            )
            .where(Infraccion.estado == estado)
            .order_by(Infraccion.fecha_infraccion.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_infracciones_graves_conductor(
        self,
        conductor_id: UUID,
        fecha_desde: Optional[date] = None
    ) -> List[Infraccion]:
        """
        Obtener infracciones graves y muy graves de un conductor
        
        Args:
            conductor_id: ID del conductor
            fecha_desde: Fecha inicial para filtrar (opcional)
            
        Returns:
            Lista de infracciones graves
        """
        query = (
            select(Infraccion)
            .join(Infraccion.tipo_infraccion)
            .options(selectinload(Infraccion.tipo_infraccion))
            .where(
                Infraccion.conductor_id == conductor_id,
                TipoInfraccion.gravedad.in_([
                    GravedadInfraccion.GRAVE,
                    GravedadInfraccion.MUY_GRAVE
                ])
            )
        )
        
        if fecha_desde:
            query = query.where(Infraccion.fecha_infraccion >= fecha_desde)
        
        query = query.order_by(Infraccion.fecha_infraccion.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_infracciones_por_periodo(
        self,
        fecha_desde: date,
        fecha_hasta: date,
        conductor_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Infraccion]:
        """
        Obtener infracciones en un período de tiempo
        
        Args:
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final
            conductor_id: ID del conductor (opcional)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de infracciones en el período
        """
        query = (
            select(Infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor)
            )
            .where(
                Infraccion.fecha_infraccion >= fecha_desde,
                Infraccion.fecha_infraccion <= fecha_hasta
            )
        )
        
        if conductor_id:
            query = query.where(Infraccion.conductor_id == conductor_id)
        
        query = query.order_by(Infraccion.fecha_infraccion.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_conductor(
        self,
        conductor_id: UUID,
        gravedad: Optional[GravedadInfraccion] = None
    ) -> int:
        """
        Contar infracciones de un conductor
        
        Args:
            conductor_id: ID del conductor
            gravedad: Gravedad de la infracción (opcional)
            
        Returns:
            Número de infracciones
        """
        query = (
            select(func.count())
            .select_from(Infraccion)
            .where(Infraccion.conductor_id == conductor_id)
        )
        
        if gravedad:
            query = (
                query
                .join(Infraccion.tipo_infraccion)
                .where(TipoInfraccion.gravedad == gravedad)
            )
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def get_estadisticas_conductor(
        self,
        conductor_id: UUID
    ) -> dict:
        """
        Obtener estadísticas de infracciones de un conductor
        
        Args:
            conductor_id: ID del conductor
            
        Returns:
            Diccionario con estadísticas
        """
        # Contar por gravedad
        total = await self.count_by_conductor(conductor_id)
        leves = await self.count_by_conductor(conductor_id, GravedadInfraccion.LEVE)
        graves = await self.count_by_conductor(conductor_id, GravedadInfraccion.GRAVE)
        muy_graves = await self.count_by_conductor(conductor_id, GravedadInfraccion.MUY_GRAVE)
        
        # Obtener última infracción
        infracciones = await self.get_by_conductor(conductor_id, limit=1)
        ultima_infraccion = infracciones[0] if infracciones else None
        
        return {
            "total": total,
            "leves": leves,
            "graves": graves,
            "muy_graves": muy_graves,
            "ultima_infraccion_fecha": ultima_infraccion.fecha_infraccion if ultima_infraccion else None,
            "ultima_infraccion_tipo": ultima_infraccion.tipo_infraccion.descripcion if ultima_infraccion else None
        }
    
    async def get_infracciones_recientes(
        self,
        dias: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Infraccion]:
        """
        Obtener infracciones recientes
        
        Args:
            dias: Número de días hacia atrás
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de infracciones recientes
        """
        from datetime import timedelta
        fecha_desde = date.today() - timedelta(days=dias)
        
        result = await self.db.execute(
            select(Infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor).selectinload(Conductor.empresa)
            )
            .where(Infraccion.fecha_infraccion >= fecha_desde)
            .order_by(Infraccion.fecha_infraccion.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_por_entidad_fiscalizadora(
        self,
        entidad: str,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Infraccion]:
        """
        Obtener infracciones por entidad fiscalizadora
        
        Args:
            entidad: Nombre de la entidad fiscalizadora
            fecha_desde: Fecha inicial (opcional)
            fecha_hasta: Fecha final (opcional)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de infracciones
        """
        query = (
            select(Infraccion)
            .options(
                selectinload(Infraccion.tipo_infraccion),
                selectinload(Infraccion.conductor)
            )
            .where(Infraccion.entidad_fiscalizadora.ilike(f"%{entidad}%"))
        )
        
        if fecha_desde:
            query = query.where(Infraccion.fecha_infraccion >= fecha_desde)
        
        if fecha_hasta:
            query = query.where(Infraccion.fecha_infraccion <= fecha_hasta)
        
        query = query.order_by(Infraccion.fecha_infraccion.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())


# Importar modelo Conductor para las queries
from app.models.conductor import Conductor
