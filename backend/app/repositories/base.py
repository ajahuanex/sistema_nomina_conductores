"""
Repositorio base con operaciones CRUD genéricas
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Repositorio base con operaciones CRUD genéricas
    
    Proporciona métodos comunes para:
    - Obtener por ID
    - Obtener todos con paginación
    - Crear
    - Actualizar
    - Eliminar
    - Verificar existencia
    - Filtrado genérico
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Inicializar repositorio
        
        Args:
            model: Clase del modelo SQLAlchemy
            db: Sesión de base de datos asíncrona
        """
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Obtener registro por ID
        
        Args:
            id: UUID del registro
            
        Returns:
            Instancia del modelo o None si no existe
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """
        Obtener todos los registros con paginación y filtros
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            filters: Diccionario de filtros {campo: valor}
            order_by: Campo por el cual ordenar
            order_desc: Si True, ordenar descendente
            
        Returns:
            Lista de instancias del modelo
        """
        query = select(self.model)
        
        # Aplicar filtros
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if isinstance(value, list):
                        conditions.append(column.in_(value))
                    elif isinstance(value, dict):
                        # Soporte para operadores especiales
                        if 'like' in value:
                            conditions.append(column.ilike(f"%{value['like']}%"))
                        elif 'gt' in value:
                            conditions.append(column > value['gt'])
                        elif 'gte' in value:
                            conditions.append(column >= value['gte'])
                        elif 'lt' in value:
                            conditions.append(column < value['lt'])
                        elif 'lte' in value:
                            conditions.append(column <= value['lte'])
                    else:
                        conditions.append(column == value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # Aplicar ordenamiento
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column)
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Crear nuevo registro
        
        Args:
            obj_in: Diccionario con datos del nuevo registro
            
        Returns:
            Instancia del modelo creado
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        """
        Actualizar registro existente
        
        Args:
            id: UUID del registro a actualizar
            obj_in: Diccionario con datos a actualizar
            
        Returns:
            Instancia del modelo actualizado o None si no existe
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, id: UUID) -> bool:
        """
        Eliminar registro
        
        Args:
            id: UUID del registro a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        
        await self.db.delete(db_obj)
        await self.db.flush()
        return True
    
    async def exists(self, id: UUID) -> bool:
        """
        Verificar si existe un registro
        
        Args:
            id: UUID del registro
            
        Returns:
            True si existe, False si no
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        count = result.scalar()
        return count > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Contar registros con filtros opcionales
        
        Args:
            filters: Diccionario de filtros {campo: valor}
            
        Returns:
            Número de registros que cumplen los filtros
        """
        query = select(func.count()).select_from(self.model)
        
        # Aplicar filtros
        if filters:
            conditions = []
            for field, value in filters.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if isinstance(value, list):
                        conditions.append(column.in_(value))
                    else:
                        conditions.append(column == value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def exists_by_field(self, field: str, value: Any) -> bool:
        """
        Verificar si existe un registro por campo específico
        
        Args:
            field: Nombre del campo
            value: Valor a buscar
            
        Returns:
            True si existe, False si no
        """
        if not hasattr(self.model, field):
            return False
        
        column = getattr(self.model, field)
        result = await self.db.execute(
            select(func.count()).select_from(self.model).where(column == value)
        )
        count = result.scalar()
        return count > 0
