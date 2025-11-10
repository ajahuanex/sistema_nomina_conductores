"""
Modelos de Habilitación y Pago
"""
import enum
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, Text, Date, DateTime, Numeric, Index, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class EstadoHabilitacion(str, enum.Enum):
    """Estados del proceso de habilitación"""
    PENDIENTE = "pendiente"
    EN_REVISION = "en_revision"
    APROBADO = "aprobado"
    OBSERVADO = "observado"
    RECHAZADO = "rechazado"
    HABILITADO = "habilitado"


class EstadoPago(str, enum.Enum):
    """Estados del pago"""
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    RECHAZADO = "rechazado"


class ConceptoTUPA(BaseModel):
    """Modelo de Concepto TUPA (Texto Único de Procedimientos Administrativos)"""
    
    __tablename__ = "conceptos_tupa"
    
    codigo = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    descripcion = Column(
        String(500),
        nullable=False
    )
    
    monto = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Monto en soles (PEN)"
    )
    
    vigencia_desde = Column(
        Date,
        nullable=False,
        default=date.today
    )
    
    vigencia_hasta = Column(
        Date,
        nullable=True,
        comment="Null si está vigente indefinidamente"
    )
    
    activo = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relaciones
    pagos = relationship(
        "Pago",
        back_populates="concepto_tupa"
    )
    
    # Índices
    __table_args__ = (
        Index('idx_concepto_tupa_vigencia', 'vigencia_desde', 'vigencia_hasta', 'activo'),
    )
    
    def __repr__(self):
        return f"<ConceptoTUPA {self.codigo} - S/. {self.monto}>"
    
    @property
    def esta_vigente(self) -> bool:
        """Verifica si el concepto TUPA está vigente"""
        if not self.activo:
            return False
        
        hoy = date.today()
        if hoy < self.vigencia_desde:
            return False
        
        if self.vigencia_hasta and hoy > self.vigencia_hasta:
            return False
        
        return True


class Habilitacion(BaseModel):
    """Modelo de Habilitación de Conductor"""
    
    __tablename__ = "habilitaciones"
    
    conductor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conductores.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    codigo_habilitacion = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Código único de habilitación generado automáticamente"
    )
    
    estado = Column(
        SQLEnum(EstadoHabilitacion),
        default=EstadoHabilitacion.PENDIENTE,
        nullable=False,
        index=True
    )
    
    observaciones = Column(
        Text,
        nullable=True,
        comment="Observaciones sobre la solicitud"
    )
    
    # Usuarios que intervienen en el proceso
    revisado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    aprobado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )
    
    habilitado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Fechas del proceso
    fecha_solicitud = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    fecha_revision = Column(
        DateTime,
        nullable=True
    )
    
    fecha_aprobacion = Column(
        DateTime,
        nullable=True
    )
    
    fecha_habilitacion = Column(
        DateTime,
        nullable=True
    )
    
    vigencia_hasta = Column(
        Date,
        nullable=True,
        index=True,
        comment="Fecha de vencimiento de la habilitación"
    )
    
    # Relaciones
    conductor = relationship(
        "Conductor",
        back_populates="habilitaciones"
    )
    
    revisor = relationship(
        "Usuario",
        foreign_keys=[revisado_por],
        backref="habilitaciones_revisadas"
    )
    
    aprobador = relationship(
        "Usuario",
        foreign_keys=[aprobado_por],
        backref="habilitaciones_aprobadas"
    )
    
    habilitador = relationship(
        "Usuario",
        foreign_keys=[habilitado_por],
        backref="habilitaciones_otorgadas"
    )
    
    pago = relationship(
        "Pago",
        back_populates="habilitacion",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_habilitacion_conductor_estado', 'conductor_id', 'estado'),
        Index('idx_habilitacion_estado_fecha', 'estado', 'fecha_solicitud'),
        Index('idx_habilitacion_vigencia', 'vigencia_hasta', 'estado'),
    )
    
    def __repr__(self):
        return f"<Habilitacion {self.codigo_habilitacion} - {self.estado}>"
    
    @property
    def esta_vigente(self) -> bool:
        """Verifica si la habilitación está vigente"""
        if self.estado != EstadoHabilitacion.HABILITADO:
            return False
        
        if self.vigencia_hasta is None:
            return True
        
        return date.today() <= self.vigencia_hasta
    
    @property
    def pago_confirmado(self) -> bool:
        """Verifica si el pago está confirmado"""
        return self.pago is not None and self.pago.estado == EstadoPago.CONFIRMADO
    
    @property
    def dias_hasta_vencimiento(self) -> int:
        """Retorna días hasta el vencimiento de la habilitación"""
        if self.vigencia_hasta is None:
            return 999999  # Sin vencimiento
        return (self.vigencia_hasta - date.today()).days
    
    def puede_aprobar(self) -> bool:
        """Verifica si la habilitación puede ser aprobada"""
        return self.estado == EstadoHabilitacion.EN_REVISION
    
    def puede_habilitar(self) -> bool:
        """Verifica si la habilitación puede ser otorgada"""
        return (
            self.estado == EstadoHabilitacion.APROBADO and
            self.pago_confirmado
        )
    
    def generar_codigo_habilitacion(self, prefijo: str = "HAB") -> str:
        """
        Genera un código único de habilitación
        
        Args:
            prefijo: Prefijo para el código
        
        Returns:
            str: Código de habilitación generado
        """
        import uuid
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"{prefijo}-{timestamp}-{unique_id}"


class Pago(BaseModel):
    """Modelo de Pago TUPA"""
    
    __tablename__ = "pagos"
    
    habilitacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("habilitaciones.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    concepto_tupa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conceptos_tupa.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    numero_recibo = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    
    monto = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Monto pagado en soles (PEN)"
    )
    
    fecha_pago = Column(
        Date,
        nullable=False,
        index=True
    )
    
    entidad_bancaria = Column(
        String(100),
        nullable=False,
        comment="Banco o entidad donde se realizó el pago"
    )
    
    estado = Column(
        SQLEnum(EstadoPago),
        default=EstadoPago.PENDIENTE,
        nullable=False,
        index=True
    )
    
    observaciones = Column(
        Text,
        nullable=True
    )
    
    # Usuario que registra el pago
    registrado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    fecha_confirmacion = Column(
        DateTime,
        nullable=True
    )
    
    confirmado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relaciones
    habilitacion = relationship(
        "Habilitacion",
        back_populates="pago"
    )
    
    concepto_tupa = relationship(
        "ConceptoTUPA",
        back_populates="pagos"
    )
    
    registrador = relationship(
        "Usuario",
        foreign_keys=[registrado_por],
        backref="pagos_registrados"
    )
    
    confirmador = relationship(
        "Usuario",
        foreign_keys=[confirmado_por],
        backref="pagos_confirmados"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_pago_estado_fecha', 'estado', 'fecha_pago'),
        Index('idx_pago_concepto_fecha', 'concepto_tupa_id', 'fecha_pago'),
    )
    
    def __repr__(self):
        return f"<Pago {self.numero_recibo} - S/. {self.monto}>"
    
    def validar_monto(self, monto_esperado: Decimal) -> bool:
        """
        Valida que el monto pagado coincida con el esperado
        
        Args:
            monto_esperado: Monto que se esperaba recibir
        
        Returns:
            bool: True si el monto coincide
        """
        return abs(self.monto - monto_esperado) < Decimal('0.01')
    
    def confirmar_pago(self, usuario_id: UUID) -> None:
        """
        Confirma el pago
        
        Args:
            usuario_id: ID del usuario que confirma el pago
        """
        self.estado = EstadoPago.CONFIRMADO
        self.fecha_confirmacion = datetime.utcnow()
        self.confirmado_por = usuario_id
    
    def rechazar_pago(self, motivo: str) -> None:
        """
        Rechaza el pago
        
        Args:
            motivo: Motivo del rechazo
        """
        self.estado = EstadoPago.RECHAZADO
        if self.observaciones:
            self.observaciones += f"\nRechazado: {motivo}"
        else:
            self.observaciones = f"Rechazado: {motivo}"
