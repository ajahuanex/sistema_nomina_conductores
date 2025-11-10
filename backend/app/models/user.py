"""
Modelo de Usuario
"""
import enum
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RolUsuario(str, enum.Enum):
    """Roles de usuario en el sistema"""
    SUPERUSUARIO = "superusuario"
    DIRECTOR = "director"
    SUBDIRECTOR = "subdirector"
    OPERARIO = "operario"
    GERENTE = "gerente"


class Usuario(BaseModel):
    """Modelo de Usuario"""
    
    __tablename__ = "usuarios"
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    password_hash = Column(
        String(255),
        nullable=False
    )
    
    nombres = Column(
        String(100),
        nullable=False
    )
    
    apellidos = Column(
        String(100),
        nullable=False
    )
    
    rol = Column(
        SQLEnum(RolUsuario),
        nullable=False,
        index=True
    )
    
    activo = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relación con Empresa (solo para Gerentes)
    # Nota: Esta es la empresa que el gerente gestiona
    empresa_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    
    # Relaciones
    notificaciones = relationship(
        "Notificacion",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_usuario_email_activo', 'email', 'activo'),
        Index('idx_usuario_rol_activo', 'rol', 'activo'),
    )
    
    def __repr__(self):
        return f"<Usuario {self.email} - {self.rol}>"
    
    @property
    def nombre_completo(self) -> str:
        """Retorna nombre completo del usuario"""
        return f"{self.nombres} {self.apellidos}"
    
    def tiene_rol(self, *roles: RolUsuario) -> bool:
        """Verifica si el usuario tiene alguno de los roles especificados"""
        return self.rol in roles
    
    def es_administrador(self) -> bool:
        """Verifica si el usuario es administrador (Superusuario, Director o Subdirector)"""
        return self.rol in [
            RolUsuario.SUPERUSUARIO,
            RolUsuario.DIRECTOR,
            RolUsuario.SUBDIRECTOR
        ]
    
    def puede_habilitar(self) -> bool:
        """Verifica si el usuario puede habilitar conductores"""
        return self.rol in [
            RolUsuario.SUPERUSUARIO,
            RolUsuario.DIRECTOR,
            RolUsuario.SUBDIRECTOR,
            RolUsuario.OPERARIO
        ]
