"""
Endpoints de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import Usuario
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse
)


router = APIRouter(prefix="/auth", tags=["Autenticación"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.LOGIN_RATE_LIMIT_PER_MINUTE}/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint de inicio de sesión
    
    Valida las credenciales del usuario y retorna tokens JWT (access y refresh)
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    
    Rate limit: 5 intentos por minuto
    """
    # Buscar usuario por email
    result = await db.execute(
        select(Usuario).where(Usuario.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    # Verificar que el usuario existe y la contraseña es correcta
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
        )
    
    # Crear payload para los tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "rol": user.rol.value,
    }
    
    # Agregar empresa_id si el usuario es gerente
    if user.empresa_id:
        token_data["empresa_id"] = str(user.empresa_id)
    
    # Generar tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para renovar el access token usando un refresh token
    
    - **refresh_token**: Token de refresco válido
    
    Retorna un nuevo par de tokens (access y refresh)
    """
    # Verificar el refresh token
    payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener el ID del usuario
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar el usuario en la base de datos
    from uuid import UUID
    result = await db.execute(
        select(Usuario).where(Usuario.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    
    # Crear payload para los nuevos tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "rol": user.rol.value,
    }
    
    if user.empresa_id:
        token_data["empresa_id"] = str(user.empresa_id)
    
    # Generar nuevos tokens
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint de cierre de sesión
    
    En una implementación con tokens JWT stateless, el logout se maneja en el cliente
    eliminando los tokens. Este endpoint existe para mantener consistencia en la API
    y podría extenderse para implementar una lista negra de tokens si fuera necesario.
    
    Requiere autenticación.
    """
    # En una implementación futura, aquí se podría agregar el token a una lista negra en Redis
    # Por ahora, simplemente retornamos un mensaje de éxito
    return MessageResponse(message="Sesión cerrada exitosamente")


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene la información del usuario actual
    
    Requiere autenticación mediante token JWT.
    
    Retorna los datos del usuario autenticado.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        nombres=current_user.nombres,
        apellidos=current_user.apellidos,
        rol=current_user.rol,
        empresa_id=str(current_user.empresa_id) if current_user.empresa_id else None,
        activo=current_user.activo
    )
