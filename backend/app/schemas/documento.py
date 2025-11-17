"""
Schemas para DocumentoConductor
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.documento_conductor import TipoDocumento


class DocumentoBase(BaseModel):
    """Schema base para documento"""
    tipo_documento: TipoDocumento = Field(
        ...,
        description="Tipo de documento"
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=500,
        description="Descripción opcional del documento"
    )


class DocumentoCreate(DocumentoBase):
    """Schema para crear documento (usado en form data)"""
    pass


class DocumentoConductorResponse(DocumentoBase):
    """Schema de respuesta para documento"""
    id: UUID
    conductor_id: UUID
    nombre_archivo: str = Field(..., description="Nombre original del archivo")
    nombre_archivo_almacenado: str = Field(..., description="Nombre del archivo en el sistema")
    tipo_mime: str = Field(..., description="Tipo MIME del archivo")
    tamano_bytes: int = Field(..., description="Tamaño del archivo en bytes")
    tamano_mb: float = Field(..., description="Tamaño del archivo en MB")
    extension: str = Field(..., description="Extensión del archivo")
    es_imagen: bool = Field(..., description="Indica si es una imagen")
    es_pdf: bool = Field(..., description="Indica si es un PDF")
    subido_por: Optional[UUID] = Field(None, description="ID del usuario que subió el documento")
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class DocumentoConductorListResponse(BaseModel):
    """Schema de respuesta para lista de documentos"""
    documentos: list[DocumentoConductorResponse]
    total: int
    
    model_config = {"from_attributes": True}


class DocumentoUploadResponse(BaseModel):
    """Schema de respuesta al subir un documento"""
    id: UUID
    mensaje: str
    nombre_archivo: str
    tamano_mb: float
    tipo_documento: TipoDocumento
    
    model_config = {"from_attributes": True}
