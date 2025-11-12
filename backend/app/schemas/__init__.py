"""
Schemas Pydantic para validación de datos
"""
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse
)
from app.schemas.user import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    CambiarPasswordRequest,
    UsuarioResponse
)
from app.schemas.empresa import (
    TipoAutorizacionBase,
    TipoAutorizacionResponse,
    AutorizacionEmpresaBase,
    AutorizacionEmpresaCreate,
    AutorizacionEmpresaResponse,
    EmpresaBase,
    EmpresaCreate,
    EmpresaUpdate,
    EmpresaResponse,
    EmpresaListResponse
)
from app.schemas.conductor import (
    ConductorBase,
    ConductorCreate,
    ConductorUpdate,
    ConductorResponse,
    ConductorListResponse,
    ConductorEstadoUpdate,
    ConductorBusqueda,
    ConductorValidacionCategoria,
    ConductorValidacionCategoriaResponse
)

__all__ = [
    # Auth schemas
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "MessageResponse",
    # User schemas
    "UsuarioBase",
    "UsuarioCreate",
    "UsuarioUpdate",
    "CambiarPasswordRequest",
    "UsuarioResponse",
    # Empresa schemas
    "TipoAutorizacionBase",
    "TipoAutorizacionResponse",
    "AutorizacionEmpresaBase",
    "AutorizacionEmpresaCreate",
    "AutorizacionEmpresaResponse",
    "EmpresaBase",
    "EmpresaCreate",
    "EmpresaUpdate",
    "EmpresaResponse",
    "EmpresaListResponse",
    # Conductor schemas
    "ConductorBase",
    "ConductorCreate",
    "ConductorUpdate",
    "ConductorResponse",
    "ConductorListResponse",
    "ConductorEstadoUpdate",
    "ConductorBusqueda",
    "ConductorValidacionCategoria",
    "ConductorValidacionCategoriaResponse",
]
