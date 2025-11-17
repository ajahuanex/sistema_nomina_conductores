"""
Schemas para Usuario
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.user import RolUsuario
import re


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    email: EmailStr = Field(..., description="Email del usuario")
    nombres: str = Field(..., min_length=2, max_length=100, description="Nombres del usuario")
    apellidos: str = Field(..., min_length=2, max_length=100, description="Apellidos del usuario")
    rol: RolUsuario = Field(..., description="Rol del usuario en el sistema")
    empresa_id: Optional[str] = Field(None, description="ID de la empresa (solo para Gerentes)")
    activo: bool = Field(default=True, description="Estado del usuario")
    
    @field_validator('nombres', 'apellidos')
    @classmethod
    def validar_nombres(cls, v: str) -> str:
        """Valida que nombres y apellidos no contengan números"""
        if not v or not v.strip():
            raise ValueError('El campo no puede estar vacío')
        if any(char.isdigit() for char in v):
            raise ValueError('No puede contener números')
        return v.strip()
    
    @field_validator('empresa_id')
    @classmethod
    def validar_empresa_id(cls, v: Optional[str], info) -> Optional[str]:
        """Valida que solo Gerentes tengan empresa_id"""
        if info.data.get('rol') == RolUsuario.GERENTE and not v:
            raise ValueError('Los Gerentes deben tener una empresa asignada')
        if info.data.get('rol') != RolUsuario.GERENTE and v:
            raise ValueError('Solo los Gerentes pueden tener empresa asignada')
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "director@drtc.gob.pe",
                    "nombres": "Juan",
                    "apellidos": "Pérez García",
                    "rol": "DIRECTOR",
                    "empresa_id": None,
                    "activo": True
                }
            ]
        }
    }



class UsuarioCreate(UsuarioBase):
    """Schema para crear un nuevo usuario"""
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )
    
    @field_validator('password')
    @classmethod
    def validar_password_fuerte(cls, v: str) -> str:
        """
        Valida que la contraseña sea fuerte:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un carácter especial
        """
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?":{}|<>)')
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "operario@drtc.gob.pe",
                    "nombres": "María",
                    "apellidos": "López Sánchez",
                    "rol": "OPERARIO",
                    "empresa_id": None,
                    "activo": True,
                    "password": "SecurePass123!"
                }
            ]
        }
    }



class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario existente"""
    email: Optional[EmailStr] = Field(None, description="Email del usuario")
    nombres: Optional[str] = Field(None, min_length=2, max_length=100, description="Nombres del usuario")
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100, description="Apellidos del usuario")
    rol: Optional[RolUsuario] = Field(None, description="Rol del usuario en el sistema")
    empresa_id: Optional[str] = Field(None, description="ID de la empresa (solo para Gerentes)")
    activo: Optional[bool] = Field(None, description="Estado del usuario")
    
    @field_validator('nombres', 'apellidos')
    @classmethod
    def validar_nombres(cls, v: Optional[str]) -> Optional[str]:
        """Valida que nombres y apellidos no contengan números"""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('El campo no puede estar vacío')
        if any(char.isdigit() for char in v):
            raise ValueError('No puede contener números')
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombres": "Juan Carlos",
                    "apellidos": "Pérez García",
                    "activo": True
                }
            ]
        }
    }


class CambiarPasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    password_actual: str = Field(..., description="Contraseña actual del usuario")
    password_nueva: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="Nueva contraseña del usuario"
    )
    password_confirmacion: str = Field(..., description="Confirmación de la nueva contraseña")
    
    @field_validator('password_nueva')
    @classmethod
    def validar_password_fuerte(cls, v: str) -> str:
        """
        Valida que la contraseña sea fuerte:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un carácter especial
        """
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?":{}|<>)')
        
        return v

    
    @field_validator('password_confirmacion')
    @classmethod
    def validar_passwords_coinciden(cls, v: str, info) -> str:
        """Valida que las contraseñas coincidan"""
        if 'password_nueva' in info.data and v != info.data['password_nueva']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "password_actual": "OldPass123!",
                    "password_nueva": "NewSecurePass456!",
                    "password_confirmacion": "NewSecurePass456!"
                }
            ]
        }
    }


class UsuarioResponse(BaseModel):
    """Schema para respuesta de usuario"""
    id: str = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    nombres: str = Field(..., description="Nombres del usuario")
    apellidos: str = Field(..., description="Apellidos del usuario")
    rol: RolUsuario = Field(..., description="Rol del usuario")
    empresa_id: Optional[str] = Field(None, description="ID de la empresa (solo para Gerentes)")
    activo: bool = Field(..., description="Estado del usuario")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    
    @field_validator('id', 'empresa_id', mode='before')
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
                    "email": "director@drtc.gob.pe",
                    "nombres": "Juan",
                    "apellidos": "Pérez García",
                    "rol": "DIRECTOR",
                    "empresa_id": None,
                    "activo": True,
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00"
                }
            ]
        }
    }
