"""
Repositorio para Habilitacion
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.habilitacion import Habilitacion, EstadoHabilitacion, Pago
from app.repositories.base import BaseRepository


class HabilitacionRepository(BaseRepository[Habilitacion]):
    """Repositorio específico para Habilitacion con filtros por estado"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Habilitacion, db)
    
    async def get_by_id_with_relations(self, id: UUID) -> Optional[Habilitacion]:
        """
        Obtener habilitación por ID con relaciones cargadas
        
        Args:
            id: UUID de la habilitación
            
        Returns:
            Habilitacion con relaciones o None si no existe
        """
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor).selectinload(Conductor.empresa),
                selectinload(Habilitacion.pago),
                selectinload(Habilitacion.revisor),
                selectinload(Habilitacion.aprobador),
                selectinload(Habilitacion.habilitador)
            )
            .where(Habilitacion.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_codigo(self, codigo_habilitacion: str) -> Optional[Habilitacion]:
        """
        Obtener habilitación por código
        
        Args:
            codigo_habilitacion: Código único de habilitación
            
        Returns:
            Habilitacion o None si no existe
        """
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor),
                selectinload(Habilitacion.pago)
            )
            .where(Habilitacion.codigo_habilitacion == codigo_habilitacion)
        )
        return result.scalar_one_or_none()
    
    async def get_by_conductor(
        self,
        conductor_id: UUID,
        estado: Optional[EstadoHabilitacion] = None
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones de un conductor
        
        Args:
            conductor_id: ID del conductor
            estado: Estado de la habilitación (opcional)
            
        Returns:
            Lista de habilitaciones
        """
        filters = {"conductor_id": conductor_id}
        if estado:
            filters["estado"] = estado.value
        
        return await self.get_all(
            filters=filters,
            order_by="fecha_solicitud",
            order_desc=True
        )
    
    async def get_by_estado(
        self,
        estado: EstadoHabilitacion,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones por estado
        
        Args:
            estado: Estado de la habilitación
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones
        """
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor).selectinload(Conductor.empresa),
                selectinload(Habilitacion.pago)
            )
            .where(Habilitacion.estado == estado)
            .order_by(Habilitacion.fecha_solicitud)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_pendientes(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones pendientes de revisión
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones pendientes
        """
        return await self.get_by_estado(
            estado=EstadoHabilitacion.PENDIENTE,
            skip=skip,
            limit=limit
        )
    
    async def get_en_revision(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones en revisión
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones en revisión
        """
        return await self.get_by_estado(
            estado=EstadoHabilitacion.EN_REVISION,
            skip=skip,
            limit=limit
        )
    
    async def get_aprobadas_sin_pago(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones aprobadas pero sin pago confirmado
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones aprobadas sin pago
        """
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor).selectinload(Conductor.empresa),
                selectinload(Habilitacion.pago)
            )
            .outerjoin(Habilitacion.pago)
            .where(
                Habilitacion.estado == EstadoHabilitacion.APROBADO,
                or_(
                    Pago.id.is_(None),
                    Pago.estado != EstadoPago.CONFIRMADO
                )
            )
            .order_by(Habilitacion.fecha_aprobacion)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_habilitadas_vigentes(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones vigentes
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones vigentes
        """
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor).selectinload(Conductor.empresa)
            )
            .where(
                Habilitacion.estado == EstadoHabilitacion.HABILITADO,
                or_(
                    Habilitacion.vigencia_hasta.is_(None),
                    Habilitacion.vigencia_hasta >= date.today()
                )
            )
            .order_by(Habilitacion.fecha_habilitacion.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_proximas_a_vencer(
        self,
        dias_anticipacion: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones próximas a vencer
        
        Args:
            dias_anticipacion: Días de anticipación para alertar
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones próximas a vencer
        """
        from datetime import timedelta
        fecha_limite = date.today() + timedelta(days=dias_anticipacion)
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor).selectinload(Conductor.empresa)
            )
            .where(
                Habilitacion.estado == EstadoHabilitacion.HABILITADO,
                Habilitacion.vigencia_hasta.isnot(None),
                Habilitacion.vigencia_hasta <= fecha_limite,
                Habilitacion.vigencia_hasta >= date.today()
            )
            .order_by(Habilitacion.vigencia_hasta)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_ultima_habilitacion_conductor(
        self,
        conductor_id: UUID
    ) -> Optional[Habilitacion]:
        """
        Obtener la última habilitación de un conductor
        
        Args:
            conductor_id: ID del conductor
            
        Returns:
            Última habilitación o None
        """
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.conductor_id == conductor_id)
            .order_by(Habilitacion.fecha_solicitud.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def count_by_estado(self, estado: EstadoHabilitacion) -> int:
        """
        Contar habilitaciones por estado
        
        Args:
            estado: Estado de la habilitación
            
        Returns:
            Número de habilitaciones en ese estado
        """
        return await self.count(filters={"estado": estado.value})
    
    async def codigo_exists(self, codigo_habilitacion: str) -> bool:
        """
        Verificar si existe un código de habilitación
        
        Args:
            codigo_habilitacion: Código a verificar
            
        Returns:
            True si existe, False si no
        """
        return await self.exists_by_field("codigo_habilitacion", codigo_habilitacion)


# Importar modelos necesarios para las queries
from app.models.conductor import Conductor
from app.models.habilitacion import EstadoPago
from sqlalchemy import or_
