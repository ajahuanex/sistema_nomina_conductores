"""
Servicio para gestión de documentos de conductores
"""
from typing import List, Optional
from uuid import UUID
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documento_conductor import DocumentoConductor, TipoDocumento
from app.repositories.documento_repository import DocumentoRepository
from app.repositories.conductor_repository import ConductorRepository
from app.utils.file_handler import (
    save_upload_file,
    delete_file,
    get_file_path,
    file_exists
)
from app.core.exceptions import RecursoNoEncontrado


class DocumentoService:
    """Servicio para gestionar documentos de conductores"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.documento_repo = DocumentoRepository(db)
        self.conductor_repo = ConductorRepository(db)
    
    async def subir_documento(
        self,
        conductor_id: UUID,
        upload_file: UploadFile,
        tipo_documento: TipoDocumento,
        descripcion: Optional[str],
        usuario_id: UUID
    ) -> DocumentoConductor:
        """
        Sube un documento para un conductor
        
        Args:
            conductor_id: ID del conductor
            upload_file: Archivo a subir
            tipo_documento: Tipo de documento
            descripcion: Descripción opcional
            usuario_id: ID del usuario que sube el documento
        
        Returns:
            DocumentoConductor creado
        
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
            HTTPException: Si hay error al subir el archivo
        """
        # Verificar que el conductor existe
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        # Guardar archivo
        nombre_almacenado, ruta_completa, tamano_bytes = await save_upload_file(upload_file)
        
        try:
            # Crear registro en base de datos
            documento = DocumentoConductor(
                conductor_id=conductor_id,
                tipo_documento=tipo_documento,
                nombre_archivo=upload_file.filename,
                nombre_archivo_almacenado=nombre_almacenado,
                ruta_archivo=ruta_completa,
                tipo_mime=upload_file.content_type.lower(),
                tamano_bytes=tamano_bytes,
                descripcion=descripcion,
                subido_por=usuario_id
            )
            
            documento = await self.documento_repo.create(documento)
            await self.db.commit()
            await self.db.refresh(documento)
            
            return documento
            
        except Exception as e:
            # Si falla la creación en BD, eliminar el archivo
            delete_file(ruta_completa)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar el documento: {str(e)}"
            )
    
    async def obtener_documentos_conductor(
        self,
        conductor_id: UUID,
        tipo_documento: Optional[TipoDocumento] = None
    ) -> List[DocumentoConductor]:
        """
        Obtiene todos los documentos de un conductor
        
        Args:
            conductor_id: ID del conductor
            tipo_documento: Filtrar por tipo (opcional)
        
        Returns:
            Lista de documentos
        
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
        """
        # Verificar que el conductor existe
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        return await self.documento_repo.get_by_conductor(conductor_id, tipo_documento)
    
    async def obtener_documento(
        self,
        documento_id: UUID
    ) -> DocumentoConductor:
        """
        Obtiene un documento por su ID
        
        Args:
            documento_id: ID del documento
        
        Returns:
            Documento encontrado
        
        Raises:
            RecursoNoEncontrado: Si el documento no existe
        """
        documento = await self.documento_repo.get_by_id(documento_id)
        if not documento:
            raise RecursoNoEncontrado("Documento", str(documento_id))
        
        # Verificar que el archivo existe físicamente
        if not file_exists(documento.nombre_archivo_almacenado):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El archivo físico no existe en el sistema"
            )
        
        return documento
    
    async def eliminar_documento(
        self,
        documento_id: UUID
    ) -> None:
        """
        Elimina un documento
        
        Args:
            documento_id: ID del documento
        
        Raises:
            RecursoNoEncontrado: Si el documento no existe
        """
        documento = await self.documento_repo.get_by_id(documento_id)
        if not documento:
            raise RecursoNoEncontrado("Documento", str(documento_id))
        
        # Eliminar archivo físico
        delete_file(documento.ruta_archivo)
        
        # Eliminar registro de BD
        await self.documento_repo.delete(documento_id)
        await self.db.commit()
    
    async def contar_documentos_conductor(
        self,
        conductor_id: UUID
    ) -> int:
        """
        Cuenta los documentos de un conductor
        
        Args:
            conductor_id: ID del conductor
        
        Returns:
            Número de documentos
        """
        return await self.documento_repo.count_by_conductor(conductor_id)
    
    def obtener_ruta_archivo(self, nombre_archivo_almacenado: str) -> str:
        """
        Obtiene la ruta completa de un archivo
        
        Args:
            nombre_archivo_almacenado: Nombre del archivo en el sistema
        
        Returns:
            Ruta completa del archivo
        """
        return str(get_file_path(nombre_archivo_almacenado))
