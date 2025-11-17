"""
Schemas Pydantic para Pago y ConceptoTUPA
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class EstadoPago(str, Enum):
    """Estados del pago"""
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    RECHAZADO = "rechazado"


# ConceptoTUPA Schemas
class ConceptoTUPABase(BaseModel):
    """Schema base para ConceptoTUPA"""
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único del concepto TUPA")
    descripcion: str = Field(..., min_length=1, max_length=500, description="Descripción del concepto")
    monto: Decimal = Field(..., gt=0, decimal_places=2, description="Monto en soles (PEN)")
    vigencia_desde: date = Field(..., description="Fecha desde la cual es vigente")
    vigencia_hasta: Optional[date] = Field(None, description="Fecha hasta la cual es vigente (null = indefinido)")
    activo: bool = Field(True, description="Si el concepto está activo")

    @field_validator('vigencia_hasta')
    @classmethod
    def validar_vigencia(cls, v, info):
        """Valida que vigencia_hasta sea posterior a vigencia_desde"""
        if v and 'vigencia_desde' in info.data and v < info.data['vigencia_desde']:
            raise ValueError('vigencia_hasta debe ser posterior a vigencia_desde')
        return v


class ConceptoTUPACreate(ConceptoTUPABase):
    """Schema para crear ConceptoTUPA"""
    pass


class ConceptoTUPAUpdate(BaseModel):
    """Schema para actualizar ConceptoTUPA"""
    descripcion: Optional[str] = Field(None, min_length=1, max_length=500)
    monto: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    vigencia_desde: Optional[date] = None
    vigencia_hasta: Optional[date] = None
    activo: Optional[bool] = None


class ConceptoTUPAResponse(ConceptoTUPABase):
    """Schema de respuesta para ConceptoTUPA"""
    id: str
    created_at: datetime
    updated_at: datetime
    esta_vigente: bool

    model_config = ConfigDict(from_attributes=True)


# Pago Schemas
class PagoBase(BaseModel):
    """Schema base para Pago"""
    numero_recibo: str = Field(..., min_length=1, max_length=100, description="Número de recibo del pago")
    monto: Decimal = Field(..., gt=0, decimal_places=2, description="Monto pagado en soles (PEN)")
    fecha_pago: date = Field(..., description="Fecha en que se realizó el pago")
    entidad_bancaria: str = Field(..., min_length=1, max_length=100, description="Banco o entidad donde se pagó")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")


class PagoCreate(PagoBase):
    """Schema para crear Pago"""
    habilitacion_id: str = Field(..., description="ID de la habilitación asociada")
    concepto_tupa_id: str = Field(..., description="ID del concepto TUPA aplicado")


class PagoUpdate(BaseModel):
    """Schema para actualizar Pago"""
    numero_recibo: Optional[str] = Field(None, min_length=1, max_length=100)
    monto: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    fecha_pago: Optional[date] = None
    entidad_bancaria: Optional[str] = Field(None, min_length=1, max_length=100)
    observaciones: Optional[str] = None
    estado: Optional[EstadoPago] = None


class PagoResponse(PagoBase):
    """Schema de respuesta para Pago"""
    id: str
    habilitacion_id: str
    concepto_tupa_id: str
    estado: EstadoPago
    registrado_por: Optional[str] = None
    fecha_confirmacion: Optional[datetime] = None
    confirmado_por: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PagoConDetalles(PagoResponse):
    """Schema de respuesta para Pago con detalles del concepto TUPA"""
    concepto_tupa: ConceptoTUPAResponse

    model_config = ConfigDict(from_attributes=True)


class OrdenPago(BaseModel):
    """Schema para orden de pago"""
    codigo_orden: str = Field(..., description="Código único de la orden de pago")
    habilitacion_id: str = Field(..., description="ID de la habilitación")
    codigo_habilitacion: str = Field(..., description="Código de la habilitación")
    conductor_nombre: str = Field(..., description="Nombre completo del conductor")
    conductor_dni: str = Field(..., description="DNI del conductor")
    empresa_razon_social: str = Field(..., description="Razón social de la empresa")
    empresa_ruc: str = Field(..., description="RUC de la empresa")
    concepto_tupa: ConceptoTUPAResponse = Field(..., description="Concepto TUPA a pagar")
    monto_total: Decimal = Field(..., description="Monto total a pagar")
    fecha_emision: datetime = Field(..., description="Fecha de emisión de la orden")
    fecha_vencimiento: date = Field(..., description="Fecha de vencimiento del pago")


class ReporteIngresos(BaseModel):
    """Schema para reporte de ingresos"""
    fecha_inicio: date
    fecha_fin: date
    total_pagos: int = Field(..., description="Cantidad total de pagos")
    total_confirmados: int = Field(..., description="Cantidad de pagos confirmados")
    total_pendientes: int = Field(..., description="Cantidad de pagos pendientes")
    total_rechazados: int = Field(..., description="Cantidad de pagos rechazados")
    monto_total: Decimal = Field(..., description="Monto total de todos los pagos")
    monto_confirmado: Decimal = Field(..., description="Monto total confirmado")
    monto_pendiente: Decimal = Field(..., description="Monto total pendiente")
    pagos_por_concepto: list[dict] = Field(..., description="Desglose por concepto TUPA")
    pagos_por_mes: list[dict] = Field(..., description="Desglose por mes")


class PagoFilter(BaseModel):
    """Schema para filtros de búsqueda de pagos"""
    estado: Optional[EstadoPago] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    concepto_tupa_id: Optional[str] = None
    entidad_bancaria: Optional[str] = None
    numero_recibo: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
