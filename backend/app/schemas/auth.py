"""
Schemas para autenticación
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import RolUsuario


class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "usuario@example.com",
                    "password": "password123"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Schema para respuesta de tokens"""
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresco JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema para solicitud de refresh token"""
    refresh_token: str = Field(..., description="Token de refresco")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Schema para respuesta de usuario actual"""
    id: str = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    nombres: str = Field(..., description="Nombres del usuario")
    apellidos: str = Field(..., description="Apellidos del usuario")
    rol: RolUsuario = Field(..., description="Rol del usuario")
    empresa_id: Optional[str] = Field(None, description="ID de la empresa (solo para Gerentes)")
    activo: bool = Field(..., description="Estado del usuario")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "usuario@example.com",
                    "nombres": "Juan",
                    "apellidos": "Pérez",
                    "rol": "DIRECTOR",
                    "empresa_id": None,
                    "activo": True
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """Schema para respuestas simples con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Operación exitosa"
                }
            ]
        }
    }
