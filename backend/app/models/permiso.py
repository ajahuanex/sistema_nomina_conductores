"""
Modelo de Permisos de Usuario
Sistema de permisos granular por módulo
"""
import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Modulo(str, enum.Enum):
    """Módulos del sistema"""
    USUARIOS = "usuarios"
    EMPRESAS = "empresas"
    CONDUCTORES = "conductores"
    HABILITACIONES = "habilitaciones"
    PAGOS = "pagos"
    DOCUMENTOS = "documentos"
    INFRACCIONES = "infracciones"
    REPORTES = "reportes"
    AUDITORIA = "auditoria"


class PermisoUsuario(BaseModel):
    """
    Modelo de Permisos de Usuario
    
    Permite al Superusuario otorgar permisos específicos a usuarios
    para acceder a módulos del sistema
    """
    
    __tablename__ = "permisos_usuario"
    
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    modulo = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Módulo del sistema al que se otorga permiso"
    )
    
    puede_leer = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Permiso de lectura"
    )
    
    puede_crear = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Permiso de creación"
    )
    
    puede_editar = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Permiso de edición"
    )
    
    puede_eliminar = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Permiso de eliminación"
    )
    
    permisos_especiales = Column(
        JSON,
        nullable=True,
        comment="Permisos adicionales específicos del módulo"
    )
    
    activo = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relaciones
    usuario = relationship(
        "Usuario",
        backref="permisos"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_permiso_usuario_modulo', 'usuario_id', 'modulo', 'activo'),
    )
    
    def __repr__(self):
        return f"<PermisoUsuario {self.usuario_id} - {self.modulo}>"
    
    def tiene_permiso_completo(self) -> bool:
        """Verifica si tiene todos los permisos"""
        return (
            self.puede_leer and
            self.puede_crear and
            self.puede_editar and
            self.puede_eliminar
        )
    
    def tiene_permiso_lectura_escritura(self) -> bool:
        """Verifica si tiene permisos de lectura y escritura"""
        return (
            self.puede_leer and
            (self.puede_crear or self.puede_editar)
        )
