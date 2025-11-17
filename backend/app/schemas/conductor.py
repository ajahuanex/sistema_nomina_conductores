"""
Schemas Pydantic para Conductor
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class EstadoConductor(str):
    """Estados del conductor"""
    PENDIENTE = "pendiente"
    HABILITADO = "habilitado"
    OBSERVADO = "observado"
    SUSPENDIDO = "suspendido"
    REVOCADO = "revocado"


class ConductorBase(BaseModel):
    """Schema base para Conductor"""
    dni: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="DNI del conductor (8 dígitos)"
    )
    nombres: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombres del conductor"
    )
    apellidos: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Apellidos del conductor"
    )
    fecha_nacimiento: date = Field(
        ...,
        description="Fecha de nacimiento del conductor"
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Dirección del conductor"
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="Teléfono del conductor"
    )
    email: str = Field(
        ...,
        max_length=255,
        description="Email del conductor"
    )
    licencia_numero: str = Field(
        ...,
        min_length=5,
        max_length=20,
        description="Número de licencia de conducir"
    )
    licencia_categoria: str = Field(
        ...,
        description="Categoría de licencia (A-I, A-IIa, A-IIb, A-IIIa, A-IIIb, A-IIIc)"
    )
    licencia_emision: date = Field(
        ...,
        description="Fecha de emisión de la licencia"
    )
    licencia_vencimiento: date = Field(
        ...,
        description="Fecha de vencimiento de la licencia"
    )
    certificado_medico_numero: Optional[str] = Field(
        None,
        max_length=50,
        description="Número de certificado médico"
    )
    certificado_medico_vencimiento: Optional[date] = Field(
        None,
        description="Fecha de vencimiento del certificado médico"
    )
    observaciones: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observaciones sobre el conductor"
    )

    @field_validator('dni')
    @classmethod
    def validate_dni(cls, v: str) -> str:
        """Valida que el DNI tenga 8 dígitos numéricos"""
        if not v.isdigit():
            raise ValueError('DNI debe contener solo dígitos')
        if len(v) != 8:
            raise ValueError('DNI debe tener exactamente 8 dígitos')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validación básica de email"""
        if '@' not in v or '.' not in v.split('@')[1]:
            raise ValueError('Email inválido')
        return v.lower()

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v: str) -> str:
        """Valida que el teléfono contenga solo dígitos y espacios"""
        cleaned = v.replace(' ', '').replace('-', '').replace('+', '')
        if not cleaned.isdigit():
            raise ValueError('Teléfono debe contener solo dígitos')
        return v

    @field_validator('licencia_categoria')
    @classmethod
    def validate_licencia_categoria(cls, v: str) -> str:
        """Valida que la categoría de licencia sea válida"""
        categorias_validas = ['A-I', 'A-IIa', 'A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc']
        if v not in categorias_validas:
            raise ValueError(
                f'Categoría de licencia inválida. Debe ser una de: {", ".join(categorias_validas)}'
            )
        return v

    @field_validator('licencia_vencimiento')
    @classmethod
    def validate_licencia_no_vencida(cls, v: date) -> date:
        """Valida que la licencia no esté vencida"""
        if v < date.today():
            raise ValueError('La licencia de conducir está vencida')
        return v

    @field_validator('licencia_emision')
    @classmethod
    def validate_licencia_emision(cls, v: date) -> date:
        """Valida que la fecha de emisión no sea futura"""
        if v > date.today():
            raise ValueError('La fecha de emisión no puede ser futura')
        return v

    @field_validator('fecha_nacimiento')
    @classmethod
    def validate_edad_minima(cls, v: date) -> date:
        """Valida que el conductor tenga al menos 18 años"""
        today = date.today()
        edad = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if edad < 18:
            raise ValueError('El conductor debe tener al menos 18 años')
        if edad > 100:
            raise ValueError('Fecha de nacimiento inválida')
        return v


class ConductorCreate(ConductorBase):
    """Schema para crear un conductor"""
    empresa_id: UUID = Field(
        ...,
        description="ID de la empresa a la que pertenece el conductor"
    )

    def validar_categoria_para_tipo_autorizacion(self, tipo_autorizacion_codigo: str) -> bool:
        """
        Valida si la categoría de licencia es apropiada para el tipo de autorización
        
        Args:
            tipo_autorizacion_codigo: Código del tipo de autorización
        
        Returns:
            bool: True si la categoría es válida
        """
        requisitos = {
            'MERCANCIAS': ['A-IIIb', 'A-IIIc'],
            'TURISMO': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'TRABAJADORES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESPECIALES': ['A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESTUDIANTES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'RESIDUOS_PELIGROSOS': ['A-IIIb', 'A-IIIc'],
        }
        
        categorias_requeridas = requisitos.get(tipo_autorizacion_codigo, [])
        return self.licencia_categoria in categorias_requeridas


class ConductorUpdate(BaseModel):
    """Schema para actualizar un conductor"""
    nombres: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )
    apellidos: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )
    direccion: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500
    )
    telefono: Optional[str] = Field(
        None,
        min_length=7,
        max_length=20
    )
    email: Optional[str] = Field(
        None,
        max_length=255
    )
    licencia_numero: Optional[str] = Field(
        None,
        min_length=5,
        max_length=20
    )
    licencia_categoria: Optional[str] = None
    licencia_emision: Optional[date] = None
    licencia_vencimiento: Optional[date] = None
    certificado_medico_numero: Optional[str] = Field(
        None,
        max_length=50
    )
    certificado_medico_vencimiento: Optional[date] = None
    observaciones: Optional[str] = Field(
        None,
        max_length=1000
    )

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validación básica de email"""
        if v is not None:
            if '@' not in v or '.' not in v.split('@')[1]:
                raise ValueError('Email inválido')
            return v.lower()
        return v

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el teléfono contenga solo dígitos y espacios"""
        if v is not None:
            cleaned = v.replace(' ', '').replace('-', '').replace('+', '')
            if not cleaned.isdigit():
                raise ValueError('Teléfono debe contener solo dígitos')
        return v

    @field_validator('licencia_categoria')
    @classmethod
    def validate_licencia_categoria(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la categoría de licencia sea válida"""
        if v is not None:
            categorias_validas = ['A-I', 'A-IIa', 'A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc']
            if v not in categorias_validas:
                raise ValueError(
                    f'Categoría de licencia inválida. Debe ser una de: {", ".join(categorias_validas)}'
                )
        return v

    @field_validator('licencia_vencimiento')
    @classmethod
    def validate_licencia_no_vencida(cls, v: Optional[date]) -> Optional[date]:
        """Valida que la licencia no esté vencida"""
        if v is not None and v < date.today():
            raise ValueError('La licencia de conducir está vencida')
        return v


class ConductorResponse(ConductorBase):
    """Schema para respuesta de conductor"""
    id: UUID
    empresa_id: UUID
    estado: str
    created_at: datetime
    updated_at: datetime
    
    # Propiedades calculadas
    nombre_completo: Optional[str] = None
    licencia_vigente: Optional[bool] = None
    certificado_medico_vigente: Optional[bool] = None
    edad: Optional[int] = None
    puede_operar: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ConductorListResponse(BaseModel):
    """Schema para listado de conductores con paginación"""
    items: list[ConductorResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConductorEstadoUpdate(BaseModel):
    """Schema para cambiar el estado de un conductor"""
    estado: str = Field(
        ...,
        description="Nuevo estado del conductor"
    )
    observacion: Optional[str] = Field(
        None,
        max_length=500,
        description="Observación sobre el cambio de estado"
    )

    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v: str) -> str:
        """Valida que el estado sea válido"""
        estados_validos = ['pendiente', 'habilitado', 'observado', 'suspendido', 'revocado']
        if v not in estados_validos:
            raise ValueError(
                f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}'
            )
        return v


class ConductorBusqueda(BaseModel):
    """Schema para búsqueda de conductores"""
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    empresa_id: Optional[UUID] = None
    estado: Optional[str] = None
    licencia_categoria: Optional[str] = None
    licencia_proxima_vencer: Optional[bool] = Field(
        None,
        description="Filtrar conductores con licencia próxima a vencer (30 días)"
    )
    certificado_proximo_vencer: Optional[bool] = Field(
        None,
        description="Filtrar conductores con certificado médico próximo a vencer (30 días)"
    )
    page: int = Field(1, ge=1, description="Número de página")
    page_size: int = Field(10, ge=1, le=100, description="Tamaño de página")


class ConductorValidacionCategoria(BaseModel):
    """Schema para validar categoría de licencia"""
    licencia_categoria: str
    tipo_autorizacion_codigo: str
    
    @field_validator('licencia_categoria')
    @classmethod
    def validate_licencia_categoria(cls, v: str) -> str:
        """Valida que la categoría de licencia sea válida"""
        categorias_validas = ['A-I', 'A-IIa', 'A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc']
        if v not in categorias_validas:
            raise ValueError(
                f'Categoría de licencia inválida. Debe ser una de: {", ".join(categorias_validas)}'
            )
        return v


class ConductorValidacionCategoriaResponse(BaseModel):
    """Schema para respuesta de validación de categoría"""
    valido: bool
    mensaje: str
    categorias_requeridas: list[str]



class ConductorCambioEstado(BaseModel):
    """Schema para cambio de estado de conductor"""
    nuevo_estado: str = Field(
        ...,
        description="Nuevo estado del conductor (habilitado, suspendido, revocado)"
    )
    motivo: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo del cambio de estado"
    )
    observaciones: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observaciones adicionales"
    )
    
    @field_validator('nuevo_estado')
    @classmethod
    def validate_estado(cls, v: str) -> str:
        """Valida que el estado sea válido"""
        estados_validos = ['pendiente', 'habilitado', 'observado', 'suspendido', 'revocado']
        if v.lower() not in estados_validos:
            raise ValueError(f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}')
        return v.lower()
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "nuevo_estado": "suspendido",
                "motivo": "Infracciones graves acumuladas",
                "observaciones": "Suspensión por 6 meses según resolución N° 123-2024"
            }]
        }
    )
