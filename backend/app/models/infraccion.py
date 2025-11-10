"""
Modelos de Infracción
"""
import enum
from datetime import date, datetime
from sqlalchemy import Column, String, Text, Date, DateTime, Enum, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class GravedadInfraccion(str, enum.Enum):
    """Enum para gravedad de infracciones"""
    LEVE = "leve"
    GRAVE = "grave"
    MUY_GRAVE = "muy_grave"


class EstadoInfraccion(str, enum.Enum):
    """Enum para estado de infracciones"""
    REGISTRADA = "registrada"
    EN_PROCESO = "en_proceso"
    RESUELTA = "resuelta"
    ANULADA = "anulada"


class TipoInfraccion(BaseModel):
    """Modelo para tipos de infracciones según normativa MTC"""
    
    __tablename__ = "tipos_infraccion"
    
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    gravedad = Column(
        Enum(GravedadInfraccion, name="gravedad_infraccion"),
        nullable=False,
        index=True
    )
    puntos = Column(Integer, nullable=False, default=0)
    activo = Column(String(10), nullable=False, default="true")
    
    # Relaciones
    infracciones = relationship("Infraccion", back_populates="tipo_infraccion")
    
    def __repr__(self):
        return f"<TipoInfraccion {self.codigo}: {self.descripcion[:50]}>"


class Infraccion(BaseModel):
    """Modelo para infracciones de conductores"""
    
    __tablename__ = "infracciones"
    
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tipo_infraccion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tipos_infraccion.id"),
        nullable=False,
        index=True
    )
    fecha_infraccion = Column(Date, nullable=False, index=True)
    descripcion = Column(Text, nullable=False)
    entidad_fiscalizadora = Column(String(200), nullable=False)
    numero_acta = Column(String(100), nullable=True, index=True)
    estado = Column(
        Enum(EstadoInfraccion, name="estado_infraccion"),
        nullable=False,
        default=EstadoInfraccion.REGISTRADA,
        index=True
    )
    resolucion = Column(Text, nullable=True)
    registrado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False
    )
    
    # Relaciones
    conductor = relationship("Conductor", back_populates="infracciones")
    tipo_infraccion = relationship("TipoInfraccion", back_populates="infracciones")
    registrado_por_usuario = relationship("Usuario", foreign_keys=[registrado_por])
    
    # Índices compuestos para consultas de historial
    __table_args__ = (
        Index('idx_infraccion_conductor_fecha', 'conductor_id', 'fecha_infraccion'),
        Index('idx_infraccion_estado_fecha', 'estado', 'fecha_infraccion'),
    )
    
    def __repr__(self):
        return f"<Infraccion {self.numero_acta}: {self.conductor_id}>"


class AsignacionVehiculo(BaseModel):
    """Modelo para asignación de vehículos a conductores"""
    
    __tablename__ = "asignaciones_vehiculo"
    
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    placa_vehiculo = Column(String(10), nullable=False, index=True)
    fecha_asignacion = Column(Date, nullable=False, default=date.today)
    fecha_desasignacion = Column(Date, nullable=True)
    activo = Column(String(10), nullable=False, default="true", index=True)
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    conductor = relationship("Conductor", back_populates="asignaciones_vehiculo")
    
    # Índices compuestos para consultas
    __table_args__ = (
        Index('idx_asignacion_conductor_activo', 'conductor_id', 'activo'),
        Index('idx_asignacion_placa_activo', 'placa_vehiculo', 'activo'),
        Index('idx_asignacion_fechas', 'fecha_asignacion', 'fecha_desasignacion'),
    )
    
    def __repr__(self):
        return f"<AsignacionVehiculo {self.placa_vehiculo} -> {self.conductor_id}>"
