"""
Schemas Pydantic para Habilitación
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.habilitacion import EstadoHabilitacion, EstadoPago


# ============================================================================
# Schemas de ConceptoTUPA
# ============================================================================

class ConceptoTUPABase(BaseModel):
    """Schema base para ConceptoTUPA"""
    codigo: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=500)
    monto: Decimal = Field(..., gt=0)
    vigencia_desde: date
    vigencia_hasta: Optional[date] = None
    activo: bool = True

    @field_validator('monto')
    @classmethod
    def validar_monto(cls, v):
        """Valida que el monto tenga máximo 2 decimales"""
        if v.as_tuple().exponent < -2:
            raise ValueError('El monto debe tener máximo 2 decimales')
        return v

    @field_validator('vigencia_hasta')
    @classmethod
    def validar_vigencia(cls, v, info):
        """Valida que vigencia_hasta sea posterior a vigencia_desde"""
        if v and 'vigencia_desde' in info.data and v <= info.data['vigencia_desde']:
            raise ValueError('vigencia_hasta debe ser posterior a vigencia_desde')
        return v


class ConceptoTUPACreate(ConceptoTUPABase):
    """Schema para crear ConceptoTUPA"""
    pass


class ConceptoTUPAUpdate(BaseModel):
    """Schema para actualizar ConceptoTUPA"""
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    monto: Optional[Decimal] = Field(None, gt=0)
    vigencia_hasta: Optional[date] = None
    activo: Optional[bool] = None

    @field_validator('monto')
    @classmethod
    def validar_monto(cls, v):
        """Valida que el monto tenga máximo 2 decimales"""
        if v and v.as_tuple().exponent < -2:
            raise ValueError('El monto debe tener máximo 2 decimales')
        return v


class ConceptoTUPAResponse(ConceptoTUPABase):
    """Schema de respuesta para ConceptoTUPA"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    esta_vigente: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Schemas de Habilitación
# ============================================================================

class HabilitacionBase(BaseModel):
    """Schema base para Habilitación"""
    conductor_id: UUID
    observaciones: Optional[str] = None


class HabilitacionCreate(BaseModel):
    """Schema para crear Habilitación"""
    conductor_id: UUID


class HabilitacionUpdate(BaseModel):
    """Schema para actualizar Habilitación"""
    observaciones: Optional[str] = None


class HabilitacionReview(BaseModel):
    """Schema para revisar una solicitud de habilitación"""
    observaciones: Optional[str] = Field(
        None,
        description="Observaciones del revisor sobre la solicitud"
    )


class HabilitacionObservacion(BaseModel):
    """Schema para observar una solicitud de habilitación"""
    observaciones: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Observaciones detalladas sobre los problemas encontrados"
    )


class HabilitacionAprobacion(BaseModel):
    """Schema para aprobar una solicitud de habilitación"""
    observaciones: Optional[str] = Field(
        None,
        max_length=1000,
        description="Comentarios adicionales sobre la aprobación"
    )


class HabilitacionHabilitar(BaseModel):
    """Schema para habilitar un conductor"""
    vigencia_hasta: date = Field(
        ...,
        description="Fecha de vencimiento de la habilitación"
    )
    observaciones: Optional[str] = Field(
        None,
        max_length=1000,
        description="Comentarios adicionales sobre la habilitación"
    )

    @field_validator('vigencia_hasta')
    @classmethod
    def validar_vigencia_futura(cls, v):
        """Valida que la vigencia sea futura"""
        if v <= date.today():
            raise ValueError('La fecha de vigencia debe ser futura')
        return v


class HabilitacionSuspension(BaseModel):
    """Schema para suspender una habilitación"""
    motivo: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Justificación detallada de la suspensión"
    )


class HabilitacionRevocacion(BaseModel):
    """Schema para revocar una habilitación"""
    motivo: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Justificación detallada de la revocación"
    )


class HabilitacionResponse(BaseModel):
    """Schema de respuesta para Habilitación"""
    id: UUID
    conductor_id: UUID
    codigo_habilitacion: str
    estado: EstadoHabilitacion
    observaciones: Optional[str] = None
    revisado_por: Optional[UUID] = None
    aprobado_por: Optional[UUID] = None
    habilitado_por: Optional[UUID] = None
    fecha_solicitud: datetime
    fecha_revision: Optional[datetime] = None
    fecha_aprobacion: Optional[datetime] = None
    fecha_habilitacion: Optional[datetime] = None
    vigencia_hasta: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    esta_vigente: bool
    pago_confirmado: bool
    dias_hasta_vencimiento: int

    model_config = ConfigDict(from_attributes=True)


class HabilitacionDetalle(HabilitacionResponse):
    """Schema detallado de Habilitación con relaciones"""
    conductor: Optional[dict] = None
    pago: Optional[dict] = None


# ============================================================================
# Schemas de Pago
# ============================================================================

class PagoBase(BaseModel):
    """Schema base para Pago"""
    numero_recibo: str = Field(..., min_length=1, max_length=100)
    monto: Decimal = Field(..., gt=0)
    fecha_pago: date
    entidad_bancaria: str = Field(..., min_length=1, max_length=100)
    observaciones: Optional[str] = None

    @field_validator('monto')
    @classmethod
    def validar_monto(cls, v):
        """Valida que el monto tenga máximo 2 decimales"""
        if v.as_tuple().exponent < -2:
            raise ValueError('El monto debe tener máximo 2 decimales')
        return v

    @field_validator('fecha_pago')
    @classmethod
    def validar_fecha_pago(cls, v):
        """Valida que la fecha de pago no sea futura"""
        if v > date.today():
            raise ValueError('La fecha de pago no puede ser futura')
        return v


class PagoCreate(PagoBase):
    """Schema para crear Pago"""
    habilitacion_id: UUID
    concepto_tupa_id: UUID


class PagoUpdate(BaseModel):
    """Schema para actualizar Pago"""
    numero_recibo: Optional[str] = Field(None, min_length=1, max_length=100)
    monto: Optional[Decimal] = Field(None, gt=0)
    fecha_pago: Optional[date] = None
    entidad_bancaria: Optional[str] = Field(None, min_length=1, max_length=100)
    observaciones: Optional[str] = None

    @field_validator('monto')
    @classmethod
    def validar_monto(cls, v):
        """Valida que el monto tenga máximo 2 decimales"""
        if v and v.as_tuple().exponent < -2:
            raise ValueError('El monto debe tener máximo 2 decimales')
        return v


class PagoConfirmacion(BaseModel):
    """Schema para confirmar un pago"""
    observaciones: Optional[str] = Field(
        None,
        max_length=1000,
        description="Comentarios adicionales sobre la confirmación"
    )


class PagoRechazo(BaseModel):
    """Schema para rechazar un pago"""
    motivo: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Motivo del rechazo del pago"
    )


class PagoResponse(PagoBase):
    """Schema de respuesta para Pago"""
    id: UUID
    habilitacion_id: UUID
    concepto_tupa_id: UUID
    estado: EstadoPago
    registrado_por: Optional[UUID] = None
    fecha_confirmacion: Optional[datetime] = None
    confirmado_por: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PagoDetalle(PagoResponse):
    """Schema detallado de Pago con relaciones"""
    concepto_tupa: Optional[ConceptoTUPAResponse] = None
    habilitacion: Optional[dict] = None


# ============================================================================
# Schemas de Orden de Pago
# ============================================================================

class OrdenPagoResponse(BaseModel):
    """Schema para orden de pago"""
    habilitacion_id: UUID
    codigo_habilitacion: str
    conductor_nombre: str
    conductor_dni: str
    concepto: str
    monto: Decimal
    codigo_pago: str
    fecha_emision: date
    vigencia_orden: date

    model_config = ConfigDict(from_attributes=True)
