"""
Modelos de Auditoría y Notificación
"""
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class AccionAuditoria(str, enum.Enum):
    """Enum para tipos de acciones auditadas"""
    CREAR = "crear"
    ACTUALIZAR = "actualizar"
    ELIMINAR = "eliminar"
    HABILITAR = "habilitar"
    SUSPENDER = "suspender"
    REVOCAR = "revocar"
    APROBAR = "aprobar"
    RECHAZAR = "rechazar"
    LOGIN = "login"
    LOGOUT = "logout"
    CAMBIO_ESTADO = "cambio_estado"


class Auditoria(BaseModel):
    """Modelo para registro de auditoría de acciones críticas"""
    
    __tablename__ = "auditoria"
    
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True
    )
    tabla = Column(String(100), nullable=False, index=True)
    accion = Column(
        String(50),
        nullable=False,
        index=True
    )
    registro_id = Column(String(100), nullable=True, index=True)
    datos_anteriores = Column(JSON, nullable=True)
    datos_nuevos = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_auditoria_usuario_fecha', 'usuario_id', 'created_at'),
        Index('idx_auditoria_tabla_accion', 'tabla', 'accion'),
        Index('idx_auditoria_registro', 'tabla', 'registro_id'),
        Index('idx_auditoria_fecha', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Auditoria {self.accion} en {self.tabla} por {self.usuario_id}>"


class TipoNotificacion(str, enum.Enum):
    """Enum para tipos de notificaciones"""
    SOLICITUD_OBSERVADA = "solicitud_observada"
    CONDUCTOR_HABILITADO = "conductor_habilitado"
    LICENCIA_POR_VENCER = "licencia_por_vencer"
    CERTIFICADO_VENCIDO = "certificado_vencido"
    INFRACCION_GRAVE = "infraccion_grave"
    ACTUALIZACION_TUPA = "actualizacion_tupa"
    SOLICITUD_PENDIENTE = "solicitud_pendiente"
    PAGO_REGISTRADO = "pago_registrado"
    CAMBIO_ESTADO = "cambio_estado"
    ALERTA_SISTEMA = "alerta_sistema"


class Notificacion(BaseModel):
    """Modelo para notificaciones del sistema"""
    
    __tablename__ = "notificaciones"
    
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tipo = Column(
        String(50),
        nullable=False,
        index=True
    )
    asunto = Column(String(500), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, nullable=False, default=False, index=True)
    enviada_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    leida_at = Column(DateTime, nullable=True)
    
    # Datos adicionales en JSON
    datos_adicionales = Column(JSON, nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="notificaciones")
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_notificacion_usuario_leida', 'usuario_id', 'leida'),
        Index('idx_notificacion_tipo_fecha', 'tipo', 'enviada_at'),
        Index('idx_notificacion_usuario_fecha', 'usuario_id', 'enviada_at'),
    )
    
    def __repr__(self):
        return f"<Notificacion {self.tipo} para {self.usuario_id}>"
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        self.leida = True
        self.leida_at = datetime.utcnow()
