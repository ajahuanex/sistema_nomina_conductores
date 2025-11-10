"""
Modelos de Empresa y Autorizaciones
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Date, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class TipoAutorizacion(BaseModel):
    """Modelo de Tipo de Autorización de Transporte"""
    
    __tablename__ = "tipos_autorizacion"
    
    codigo = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    nombre = Column(
        String(100),
        nullable=False
    )
    
    descripcion = Column(
        String(500),
        nullable=True
    )
    
    requisitos_especiales = Column(
        JSON,
        nullable=True,
        comment="Requisitos adicionales específicos del tipo de autorización"
    )
    
    # Relaciones
    autorizaciones_empresas = relationship(
        "AutorizacionEmpresa",
        back_populates="tipo_autorizacion",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<TipoAutorizacion {self.codigo} - {self.nombre}>"


class Empresa(BaseModel):
    """Modelo de Empresa de Transporte"""
    
    __tablename__ = "empresas"
    
    ruc = Column(
        String(11),
        unique=True,
        nullable=False,
        index=True
    )
    
    razon_social = Column(
        String(255),
        nullable=False
    )
    
    direccion = Column(
        String(500),
        nullable=False
    )
    
    telefono = Column(
        String(20),
        nullable=False
    )
    
    email = Column(
        String(255),
        nullable=False
    )
    
    gerente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    activo = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relaciones
    gerente = relationship(
        "Usuario",
        foreign_keys=[gerente_id],
        backref="empresa_gestionada"
    )
    
    autorizaciones = relationship(
        "AutorizacionEmpresa",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    
    conductores = relationship(
        "Conductor",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_empresa_ruc_activo', 'ruc', 'activo'),
        Index('idx_empresa_gerente_activo', 'gerente_id', 'activo'),
    )
    
    def __repr__(self):
        return f"<Empresa {self.ruc} - {self.razon_social}>"
    
    @property
    def tiene_autorizaciones_vigentes(self) -> bool:
        """Verifica si la empresa tiene autorizaciones vigentes"""
        return any(auth.vigente for auth in self.autorizaciones)
    
    def tiene_autorizacion(self, codigo_tipo: str) -> bool:
        """Verifica si la empresa tiene un tipo específico de autorización vigente"""
        return any(
            auth.vigente and auth.tipo_autorizacion.codigo == codigo_tipo
            for auth in self.autorizaciones
        )
    
    def validar_ruc(self) -> bool:
        """Valida que el RUC tenga 11 dígitos"""
        return len(self.ruc) == 11 and self.ruc.isdigit()


class AutorizacionEmpresa(BaseModel):
    """Modelo de Autorización de Empresa (relación muchos-a-muchos)"""
    
    __tablename__ = "autorizaciones_empresas"
    
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    tipo_autorizacion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tipos_autorizacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    numero_resolucion = Column(
        String(100),
        nullable=False,
        unique=True
    )
    
    fecha_emision = Column(
        Date,
        nullable=False
    )
    
    fecha_vencimiento = Column(
        Date,
        nullable=True,
        comment="Null si la autorización no tiene vencimiento"
    )
    
    vigente = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relaciones
    empresa = relationship(
        "Empresa",
        back_populates="autorizaciones"
    )
    
    tipo_autorizacion = relationship(
        "TipoAutorizacion",
        back_populates="autorizaciones_empresas"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_autorizacion_empresa_tipo', 'empresa_id', 'tipo_autorizacion_id'),
        Index('idx_autorizacion_vigente', 'vigente', 'fecha_vencimiento'),
    )
    
    def __repr__(self):
        return f"<AutorizacionEmpresa {self.numero_resolucion}>"
    
    @property
    def esta_vencida(self) -> bool:
        """Verifica si la autorización está vencida"""
        if self.fecha_vencimiento is None:
            return False
        from datetime import date
        return date.today() > self.fecha_vencimiento
    
    def actualizar_vigencia(self) -> None:
        """Actualiza el estado de vigencia basado en la fecha de vencimiento"""
        if self.esta_vencida:
            self.vigente = False
