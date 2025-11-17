"""
Modelo de Documento de Conductor
"""
import enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class TipoDocumento(str, enum.Enum):
    """Tipos de documentos que puede subir un conductor"""
    LICENCIA_CONDUCIR = "licencia_conducir"
    CERTIFICADO_MEDICO = "certificado_medico"
    ANTECEDENTES_PENALES = "antecedentes_penales"
    ANTECEDENTES_POLICIALES = "antecedentes_policiales"
    ANTECEDENTES_JUDICIALES = "antecedentes_judiciales"
    FOTO_CONDUCTOR = "foto_conductor"
    OTRO = "otro"


class DocumentoConductor(BaseModel):
    """Modelo de Documento de Conductor para almacenar archivos adjuntos"""
    
    __tablename__ = "documentos_conductor"
    
    # Relación con conductor
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Tipo de documento
    tipo_documento = Column(
        SQLEnum(TipoDocumento),
        nullable=False,
        index=True
    )
    
    # Información del archivo
    nombre_archivo = Column(
        String(255),
        nullable=False,
        comment="Nombre original del archivo"
    )
    
    nombre_archivo_almacenado = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Nombre del archivo en el sistema de almacenamiento"
    )
    
    ruta_archivo = Column(
        String(500),
        nullable=False,
        comment="Ruta completa del archivo en el sistema"
    )
    
    tipo_mime = Column(
        String(100),
        nullable=False,
        comment="Tipo MIME del archivo (application/pdf, image/jpeg, etc.)"
    )
    
    tamano_bytes = Column(
        Integer,
        nullable=False,
        comment="Tamaño del archivo en bytes"
    )
    
    # Descripción opcional
    descripcion = Column(
        String(500),
        nullable=True,
        comment="Descripción opcional del documento"
    )
    
    # Usuario que subió el documento
    subido_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Relaciones
    conductor = relationship(
        "Conductor",
        back_populates="documentos"
    )
    
    usuario = relationship(
        "Usuario",
        foreign_keys=[subido_por]
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_documento_conductor_tipo', 'conductor_id', 'tipo_documento'),
    )
    
    def __repr__(self):
        return f"<DocumentoConductor {self.nombre_archivo} - {self.tipo_documento}>"
    
    # Validaciones
    
    @validates('tipo_mime')
    def validate_tipo_mime(self, key, tipo_mime):
        """Valida que el tipo MIME sea permitido"""
        tipos_permitidos = [
            'application/pdf',
            'image/jpeg',
            'image/jpg',
            'image/png'
        ]
        if tipo_mime and tipo_mime.lower() not in tipos_permitidos:
            raise ValueError(f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(tipos_permitidos)}")
        return tipo_mime.lower() if tipo_mime else None
    
    @validates('tamano_bytes')
    def validate_tamano(self, key, tamano):
        """Valida que el tamaño no exceda 10MB"""
        max_size = 10 * 1024 * 1024  # 10MB en bytes
        if tamano and tamano > max_size:
            raise ValueError(f"El archivo excede el tamaño máximo permitido de 10MB")
        return tamano
    
    # Propiedades
    
    @property
    def tamano_mb(self) -> float:
        """Retorna el tamaño del archivo en MB"""
        return round(self.tamano_bytes / (1024 * 1024), 2)
    
    @property
    def extension(self) -> str:
        """Retorna la extensión del archivo"""
        if '.' in self.nombre_archivo:
            return self.nombre_archivo.rsplit('.', 1)[1].lower()
        return ''
    
    @property
    def es_imagen(self) -> bool:
        """Verifica si el documento es una imagen"""
        return self.tipo_mime.startswith('image/')
    
    @property
    def es_pdf(self) -> bool:
        """Verifica si el documento es un PDF"""
        return self.tipo_mime == 'application/pdf'
