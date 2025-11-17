"""
Schemas para Empresa y Autorizaciones
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, date


class TipoAutorizacionBase(BaseModel):
    """Schema base para Tipo de Autorización"""
    codigo: str = Field(..., min_length=1, max_length=50, description="Código del tipo de autorización")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del tipo de autorización")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del tipo de autorización")
    requisitos_especiales: Optional[dict] = Field(None, description="Requisitos adicionales específicos")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "codigo": "MERCANCIAS",
                    "nombre": "Transporte de Mercancías",
                    "descripcion": "Autorización para transporte de carga general",
                    "requisitos_especiales": {"licencia_minima": "A-IIIb"}
                }
            ]
        }
    }


class TipoAutorizacionResponse(TipoAutorizacionBase):
    """Schema para respuesta de Tipo de Autorización"""
    id: str = Field(..., description="ID del tipo de autorización")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convierte UUID a string"""
        if v is None:
            return v
        return str(v)
    
    model_config = {
        "from_attributes": True
    }


class AutorizacionEmpresaBase(BaseModel):
    """Schema base para Autorización de Empresa"""
    tipo_autorizacion_id: str = Field(..., description="ID del tipo de autorización")
    numero_resolucion: str = Field(..., min_length=1, max_length=100, description="Número de resolución")
    fecha_emision: date = Field(..., description="Fecha de emisión de la autorización")
    fecha_vencimiento: Optional[date] = Field(None, description="Fecha de vencimiento (null si no vence)")
    vigente: bool = Field(default=True, description="Estado de vigencia")
    
    @field_validator('fecha_vencimiento')
    @classmethod
    def validar_fecha_vencimiento(cls, v: Optional[date], info) -> Optional[date]:
        """Valida que la fecha de vencimiento sea posterior a la fecha de emisión"""
        if v is not None and 'fecha_emision' in info.data:
            if v <= info.data['fecha_emision']:
                raise ValueError('La fecha de vencimiento debe ser posterior a la fecha de emisión')
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tipo_autorizacion_id": "123e4567-e89b-12d3-a456-426614174000",
                    "numero_resolucion": "RD-2024-001",
                    "fecha_emision": "2024-01-15",
                    "fecha_vencimiento": "2025-01-15",
                    "vigente": True
                }
            ]
        }
    }


class AutorizacionEmpresaCreate(AutorizacionEmpresaBase):
    """Schema para crear una autorización de empresa"""
    pass


class AutorizacionEmpresaResponse(AutorizacionEmpresaBase):
    """Schema para respuesta de Autorización de Empresa"""
    id: str = Field(..., description="ID de la autorización")
    empresa_id: str = Field(..., description="ID de la empresa")
    tipo_autorizacion: Optional[TipoAutorizacionResponse] = Field(None, description="Datos del tipo de autorización")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    @field_validator('id', 'empresa_id', 'tipo_autorizacion_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convierte UUID a string"""
        if v is None:
            return v
        return str(v)
    
    model_config = {
        "from_attributes": True
    }


class EmpresaBase(BaseModel):
    """Schema base para Empresa"""
    ruc: str = Field(..., min_length=11, max_length=11, description="RUC de la empresa (11 dígitos)")
    razon_social: str = Field(..., min_length=1, max_length=255, description="Razón social de la empresa")
    direccion: str = Field(..., min_length=1, max_length=500, description="Dirección de la empresa")
    telefono: str = Field(..., min_length=7, max_length=20, description="Teléfono de la empresa")
    email: EmailStr = Field(..., description="Email de la empresa")
    gerente_id: Optional[str] = Field(None, description="ID del gerente asignado")
    activo: bool = Field(default=True, description="Estado de la empresa")
    
    @field_validator('ruc')
    @classmethod
    def validar_ruc(cls, v: str) -> str:
        """Valida que el RUC tenga 11 dígitos numéricos"""
        if not v:
            raise ValueError('El RUC es requerido')
        
        # Eliminar espacios
        v = v.strip()
        
        if len(v) != 11:
            raise ValueError('El RUC debe tener exactamente 11 dígitos')
        
        if not v.isdigit():
            raise ValueError('El RUC debe contener solo números')
        
        return v
    
    @field_validator('telefono')
    @classmethod
    def validar_telefono(cls, v: str) -> str:
        """Valida el formato del teléfono"""
        if not v:
            raise ValueError('El teléfono es requerido')
        
        # Eliminar espacios y caracteres especiales comunes
        v_clean = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if not v_clean.isdigit():
            raise ValueError('El teléfono debe contener solo números')
        
        if len(v_clean) < 7:
            raise ValueError('El teléfono debe tener al menos 7 dígitos')
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ruc": "20123456789",
                    "razon_social": "Transportes Puno SAC",
                    "direccion": "Av. El Sol 123, Puno",
                    "telefono": "051-123456",
                    "email": "contacto@transportespuno.com",
                    "gerente_id": None,
                    "activo": True
                }
            ]
        }
    }


class EmpresaCreate(EmpresaBase):
    """Schema para crear una nueva empresa"""
    autorizaciones: Optional[List[AutorizacionEmpresaCreate]] = Field(
        default=[],
        description="Lista de autorizaciones iniciales de la empresa"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ruc": "20123456789",
                    "razon_social": "Transportes Puno SAC",
                    "direccion": "Av. El Sol 123, Puno",
                    "telefono": "051-123456",
                    "email": "contacto@transportespuno.com",
                    "gerente_id": None,
                    "activo": True,
                    "autorizaciones": [
                        {
                            "tipo_autorizacion_id": "123e4567-e89b-12d3-a456-426614174000",
                            "numero_resolucion": "RD-2024-001",
                            "fecha_emision": "2024-01-15",
                            "fecha_vencimiento": "2025-01-15",
                            "vigente": True
                        }
                    ]
                }
            ]
        }
    }


class EmpresaUpdate(BaseModel):
    """Schema para actualizar una empresa existente"""
    razon_social: Optional[str] = Field(None, min_length=1, max_length=255, description="Razón social de la empresa")
    direccion: Optional[str] = Field(None, min_length=1, max_length=500, description="Dirección de la empresa")
    telefono: Optional[str] = Field(None, min_length=7, max_length=20, description="Teléfono de la empresa")
    email: Optional[EmailStr] = Field(None, description="Email de la empresa")
    gerente_id: Optional[str] = Field(None, description="ID del gerente asignado")
    activo: Optional[bool] = Field(None, description="Estado de la empresa")
    
    @field_validator('telefono')
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        """Valida el formato del teléfono"""
        if v is None:
            return v
        
        # Eliminar espacios y caracteres especiales comunes
        v_clean = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if not v_clean.isdigit():
            raise ValueError('El teléfono debe contener solo números')
        
        if len(v_clean) < 7:
            raise ValueError('El teléfono debe tener al menos 7 dígitos')
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "razon_social": "Transportes Puno SAC",
                    "direccion": "Av. El Sol 456, Puno",
                    "telefono": "051-654321",
                    "activo": True
                }
            ]
        }
    }


class EmpresaResponse(EmpresaBase):
    """Schema para respuesta de Empresa"""
    id: str = Field(..., description="ID de la empresa")
    autorizaciones: List[AutorizacionEmpresaResponse] = Field(default=[], description="Lista de autorizaciones de la empresa")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    @field_validator('id', 'gerente_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        """Convierte UUID a string"""
        if v is None:
            return v
        return str(v)
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "ruc": "20123456789",
                    "razon_social": "Transportes Puno SAC",
                    "direccion": "Av. El Sol 123, Puno",
                    "telefono": "051-123456",
                    "email": "contacto@transportespuno.com",
                    "gerente_id": None,
                    "activo": True,
                    "autorizaciones": [],
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                }
            ]
        }
    }


class EmpresaListResponse(BaseModel):
    """Schema para respuesta de lista de empresas con paginación"""
    items: List[EmpresaResponse] = Field(..., description="Lista de empresas")
    total: int = Field(..., description="Total de empresas")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Total de páginas")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 0
                }
            ]
        }
    }
