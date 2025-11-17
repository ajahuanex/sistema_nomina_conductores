"""
Repositorio para DocumentoConductor
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.documento_conductor import DocumentoConductor, TipoDocumento
from app.repositories.base import BaseRepository


class DocumentoRepository(BaseRepository[DocumentoConductor]):
    """Repositorio para gestionar documentos de conductores"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DocumentoConductor, db)
    
    async def get_by_conductor(
        self,
        conductor_id: UUID,
        tipo_documento: Optional[TipoDocumento] = None
    ) -> List[DocumentoConductor]:
        """
        Obtiene todos los documentos de un conductor
        
        Args:
            conductor_id: ID del conductor
            tipo_documento: Filtrar por tipo de documento (opcional)
        
        Returns:
            Lista de documentos del conductor
        """
        query = select(DocumentoConductor).where(
            DocumentoConductor.conductor_id == conductor_id
        )
        
        if tipo_documento:
            query = query.where(DocumentoConductor.tipo_documento == tipo_documento)
        
        query = query.order_by(DocumentoConductor.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_nombre_almacenado(
        self,
        nombre_archivo_almacenado: str
    ) -> Optional[DocumentoConductor]:
        """
        Obtiene un documento por su nombre almacenado
        
        Args:
            nombre_archivo_almacenado: Nombre del archivo en el sistema
        
        Returns:
            Documento si existe, None en caso contrario
        """
        query = select(DocumentoConductor).where(
            DocumentoConductor.nombre_archivo_almacenado == nombre_archivo_almacenado
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def count_by_conductor(self, conductor_id: UUID) -> int:
        """
        Cuenta los documentos de un conductor
        
        Args:
            conductor_id: ID del conductor
        
        Returns:
            Número de documentos
        """
        documentos = await self.get_by_conductor(conductor_id)
        return len(documentos)
    
    async def delete_by_conductor(self, conductor_id: UUID) -> int:
        """
        Elimina todos los documentos de un conductor
        
        Args:
            conductor_id: ID del conductor
        
        Returns:
            Número de documentos eliminados
        """
        documentos = await self.get_by_conductor(conductor_id)
        count = len(documentos)
        
        for documento in documentos:
            await self.delete(documento.id)
        
        return count
