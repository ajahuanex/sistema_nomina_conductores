"""
Repositorio para Conductor
"""
from typing import Optional, List
from uuid import UUID
from datetime import date, timedelta
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conductor import Conductor, EstadoConductor
from app.repositories.base import BaseRepository


class ConductorRepository(BaseRepository[Conductor]):
    """Repositorio específico para Conductor con búsqueda avanzada"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Conductor, db)
    
    async def get_by_dni(self, dni: str) -> Optional[Conductor]:
        """
        Obtener conductor por DNI
        
        Args:
            dni: DNI del conductor
            
        Returns:
            Conductor o None si no existe
        """
        result = await self.db.execute(
            select(Conductor)
            .options(
                selectinload(Conductor.empresa),
                selectinload(Conductor.habilitaciones),
                selectinload(Conductor.infracciones)
            )
            .where(Conductor.dni == dni)
        )
        return result.scalar_one_or_none()
    
    async def get_by_licencia(self, licencia_numero: str) -> Optional[Conductor]:
        """
        Obtener conductor por número de licencia
        
        Args:
            licencia_numero: Número de licencia
            
        Returns:
            Conductor o None si no existe
        """
        result = await self.db.execute(
            select(Conductor)
            .options(selectinload(Conductor.empresa))
            .where(Conductor.licencia_numero == licencia_numero)
        )
        return result.scalar_one_or_none()
    
    async def dni_exists(self, dni: str) -> bool:
        """
        Verificar si existe un DNI
        
        Args:
            dni: DNI a verificar
            
        Returns:
            True si existe, False si no
        """
        return await self.exists_by_field("dni", dni)
    
    async def licencia_exists(self, licencia_numero: str) -> bool:
        """
        Verificar si existe una licencia
        
        Args:
            licencia_numero: Número de licencia a verificar
            
        Returns:
            True si existe, False si no
        """
        return await self.exists_by_field("licencia_numero", licencia_numero)
    
    async def get_by_empresa(
        self,
        empresa_id: UUID,
        estado: Optional[EstadoConductor] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conductor]:
        """
        Obtener conductores de una empresa
        
        Args:
            empresa_id: ID de la empresa
            estado: Estado del conductor (opcional)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de conductores
        """
        filters = {"empresa_id": empresa_id}
        if estado:
            filters["estado"] = estado.value
        
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="apellidos"
        )
    
    async def get_by_estado(
        self,
        estado: EstadoConductor,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conductor]:
        """
        Obtener conductores por estado
        
        Args:
            estado: Estado del conductor
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de conductores
        """
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters={"estado": estado.value},
            order_by="apellidos"
        )
    
    async def buscar_conductores(
        self,
        texto_busqueda: Optional[str] = None,
        empresa_id: Optional[UUID] = None,
        estado: Optional[EstadoConductor] = None,
        licencia_categoria: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conductor]:
        """
        Búsqueda avanzada de conductores
        
        Args:
            texto_busqueda: Texto para buscar en DNI, nombres, apellidos
            empresa_id: Filtrar por empresa
            estado: Filtrar por estado
            licencia_categoria: Filtrar por categoría de licencia
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de conductores que cumplen los criterios
        """
        query = select(Conductor).options(selectinload(Conductor.empresa))
        
        conditions = []
        
        # Búsqueda por texto
        if texto_busqueda:
            texto = f"%{texto_busqueda}%"
            conditions.append(
                or_(
                    Conductor.dni.ilike(texto),
                    Conductor.nombres.ilike(texto),
                    Conductor.apellidos.ilike(texto),
                    Conductor.licencia_numero.ilike(texto)
                )
            )
        
        # Filtros adicionales
        if empresa_id:
            conditions.append(Conductor.empresa_id == empresa_id)
        
        if estado:
            conditions.append(Conductor.estado == estado)
        
        if licencia_categoria:
            conditions.append(Conductor.licencia_categoria == licencia_categoria)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Conductor.apellidos).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_conductores_con_licencia_por_vencer(
        self,
        dias_anticipacion: int = 30
    ) -> List[Conductor]:
        """
        Obtener conductores cuya licencia está por vencer
        
        Args:
            dias_anticipacion: Días de anticipación para alertar
            
        Returns:
            Lista de conductores con licencia próxima a vencer
        """
        fecha_limite = date.today() + timedelta(days=dias_anticipacion)
        
        result = await self.db.execute(
            select(Conductor)
            .options(selectinload(Conductor.empresa))
            .where(
                Conductor.licencia_vencimiento <= fecha_limite,
                Conductor.licencia_vencimiento >= date.today(),
                Conductor.estado == EstadoConductor.HABILITADO
            )
            .order_by(Conductor.licencia_vencimiento)
        )
        return list(result.scalars().all())
    
    async def get_conductores_con_certificado_por_vencer(
        self,
        dias_anticipacion: int = 30
    ) -> List[Conductor]:
        """
        Obtener conductores cuyo certificado médico está por vencer
        
        Args:
            dias_anticipacion: Días de anticipación para alertar
            
        Returns:
            Lista de conductores con certificado próximo a vencer
        """
        fecha_limite = date.today() + timedelta(days=dias_anticipacion)
        
        result = await self.db.execute(
            select(Conductor)
            .options(selectinload(Conductor.empresa))
            .where(
                Conductor.certificado_medico_vencimiento.isnot(None),
                Conductor.certificado_medico_vencimiento <= fecha_limite,
                Conductor.certificado_medico_vencimiento >= date.today(),
                Conductor.estado == EstadoConductor.HABILITADO
            )
            .order_by(Conductor.certificado_medico_vencimiento)
        )
        return list(result.scalars().all())
    
    async def get_conductores_habilitados_por_empresa(
        self,
        empresa_id: UUID
    ) -> List[Conductor]:
        """
        Obtener conductores habilitados de una empresa
        
        Args:
            empresa_id: ID de la empresa
            
        Returns:
            Lista de conductores habilitados
        """
        return await self.get_by_empresa(
            empresa_id=empresa_id,
            estado=EstadoConductor.HABILITADO
        )
    
    async def count_by_estado(self, estado: EstadoConductor) -> int:
        """
        Contar conductores por estado
        
        Args:
            estado: Estado del conductor
            
        Returns:
            Número de conductores en ese estado
        """
        return await self.count(filters={"estado": estado.value})
    
    async def count_by_empresa(self, empresa_id: UUID) -> int:
        """
        Contar conductores de una empresa
        
        Args:
            empresa_id: ID de la empresa
            
        Returns:
            Número de conductores de la empresa
        """
        return await self.count(filters={"empresa_id": empresa_id})
