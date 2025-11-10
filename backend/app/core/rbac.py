"""
Sistema de Control de Acceso Basado en Roles (RBAC)
"""
from typing import List, Callable, Optional
from functools import wraps
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import Usuario, RolUsuario


class PermissionDenied(HTTPException):
    """Excepción personalizada para permisos denegados"""
    def __init__(self, detail: str = "No tiene permisos para realizar esta acción"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


def require_roles(*allowed_roles: RolUsuario):
    """
    Decorador para proteger endpoints según roles permitidos
    
    Args:
        *allowed_roles: Roles permitidos para acceder al endpoint
        
    Returns:
        Decorador que verifica el rol del usuario
        
    Example:
        @router.get("/admin")
        @require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR)
        async def admin_endpoint(current_user: Usuario = Depends(get_current_user)):
            return {"message": "Admin access"}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user: Usuario = Depends(get_current_user), **kwargs):
            if current_user.rol not in allowed_roles:
                raise PermissionDenied(
                    detail=f"Acceso denegado. Roles permitidos: {', '.join([r.value for r in allowed_roles])}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_admin():
    """
    Decorador para endpoints que requieren rol de administrador
    (Superusuario, Director o Subdirector)
    
    Returns:
        Decorador que verifica si el usuario es administrador
    """
    return require_roles(
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR,
        RolUsuario.SUBDIRECTOR
    )


def require_superuser():
    """
    Decorador para endpoints que requieren rol de Superusuario
    
    Returns:
        Decorador que verifica si el usuario es superusuario
    """
    return require_roles(RolUsuario.SUPERUSUARIO)


async def verify_empresa_access(
    empresa_id: UUID,
    current_user: Usuario,
    db: AsyncSession
) -> bool:
    """
    Verifica si el usuario tiene acceso a una empresa específica
    
    Args:
        empresa_id: ID de la empresa a verificar
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        True si el usuario tiene acceso, False en caso contrario
        
    Rules:
        - Superusuarios, Directores, Subdirectores y Operarios tienen acceso a todas las empresas
        - Gerentes solo tienen acceso a su propia empresa
    """
    # Administradores y operarios tienen acceso a todas las empresas
    if current_user.rol in [
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR,
        RolUsuario.SUBDIRECTOR,
        RolUsuario.OPERARIO
    ]:
        return True
    
    # Gerentes solo tienen acceso a su propia empresa
    if current_user.rol == RolUsuario.GERENTE:
        return current_user.empresa_id == empresa_id
    
    return False


async def verify_conductor_access(
    conductor_id: UUID,
    current_user: Usuario,
    db: AsyncSession
) -> bool:
    """
    Verifica si el usuario tiene acceso a un conductor específico
    
    Args:
        conductor_id: ID del conductor a verificar
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        True si el usuario tiene acceso, False en caso contrario
        
    Rules:
        - Superusuarios, Directores, Subdirectores y Operarios tienen acceso a todos los conductores
        - Gerentes solo tienen acceso a conductores de su empresa
    """
    # Administradores y operarios tienen acceso a todos los conductores
    if current_user.rol in [
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR,
        RolUsuario.SUBDIRECTOR,
        RolUsuario.OPERARIO
    ]:
        return True
    
    # Gerentes solo tienen acceso a conductores de su empresa
    if current_user.rol == RolUsuario.GERENTE:
        from app.models.conductor import Conductor
        result = await db.execute(
            select(Conductor).where(Conductor.id == conductor_id)
        )
        conductor = result.scalar_one_or_none()
        
        if conductor is None:
            return False
        
        return conductor.empresa_id == current_user.empresa_id
    
    return False


async def require_empresa_access(
    empresa_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Dependency para verificar acceso a una empresa
    
    Args:
        empresa_id: ID de la empresa
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        Usuario actual si tiene acceso
        
    Raises:
        PermissionDenied: Si el usuario no tiene acceso a la empresa
    """
    has_access = await verify_empresa_access(empresa_id, current_user, db)
    
    if not has_access:
        raise PermissionDenied(
            detail="No tiene permisos para acceder a esta empresa"
        )
    
    return current_user


async def require_conductor_access(
    conductor_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Dependency para verificar acceso a un conductor
    
    Args:
        conductor_id: ID del conductor
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        Usuario actual si tiene acceso
        
    Raises:
        PermissionDenied: Si el usuario no tiene acceso al conductor
    """
    has_access = await verify_conductor_access(conductor_id, current_user, db)
    
    if not has_access:
        raise PermissionDenied(
            detail="No tiene permisos para acceder a este conductor"
        )
    
    return current_user


def can_modify_user(current_user: Usuario, target_user: Usuario) -> bool:
    """
    Verifica si el usuario actual puede modificar a otro usuario
    
    Args:
        current_user: Usuario que intenta modificar
        target_user: Usuario objetivo
        
    Returns:
        True si puede modificar, False en caso contrario
        
    Rules:
        - Superusuarios pueden modificar a cualquier usuario
        - Directores pueden modificar a Subdirectores, Operarios y Gerentes
        - Subdirectores pueden modificar a Operarios y Gerentes
        - Nadie más puede modificar usuarios
    """
    if current_user.rol == RolUsuario.SUPERUSUARIO:
        return True
    
    if current_user.rol == RolUsuario.DIRECTOR:
        return target_user.rol in [
            RolUsuario.SUBDIRECTOR,
            RolUsuario.OPERARIO,
            RolUsuario.GERENTE
        ]
    
    if current_user.rol == RolUsuario.SUBDIRECTOR:
        return target_user.rol in [
            RolUsuario.OPERARIO,
            RolUsuario.GERENTE
        ]
    
    return False


def can_create_user_with_role(current_user: Usuario, target_role: RolUsuario) -> bool:
    """
    Verifica si el usuario actual puede crear un usuario con un rol específico
    
    Args:
        current_user: Usuario que intenta crear
        target_role: Rol del nuevo usuario
        
    Returns:
        True si puede crear, False en caso contrario
        
    Rules:
        - Superusuarios pueden crear cualquier rol
        - Directores pueden crear Subdirectores, Operarios y Gerentes
        - Subdirectores pueden crear Operarios y Gerentes
        - Nadie más puede crear usuarios
    """
    if current_user.rol == RolUsuario.SUPERUSUARIO:
        return True
    
    if current_user.rol == RolUsuario.DIRECTOR:
        return target_role in [
            RolUsuario.SUBDIRECTOR,
            RolUsuario.OPERARIO,
            RolUsuario.GERENTE
        ]
    
    if current_user.rol == RolUsuario.SUBDIRECTOR:
        return target_role in [
            RolUsuario.OPERARIO,
            RolUsuario.GERENTE
        ]
    
    return False


def can_habilitar_conductor(current_user: Usuario) -> bool:
    """
    Verifica si el usuario puede habilitar conductores
    
    Args:
        current_user: Usuario actual
        
    Returns:
        True si puede habilitar, False en caso contrario
        
    Rules:
        - Superusuarios, Directores y Subdirectores pueden habilitar
        - Operarios NO pueden habilitar (solo revisar)
        - Gerentes NO pueden habilitar
    """
    return current_user.rol in [
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR,
        RolUsuario.SUBDIRECTOR
    ]


def can_revisar_solicitud(current_user: Usuario) -> bool:
    """
    Verifica si el usuario puede revisar solicitudes de habilitación
    
    Args:
        current_user: Usuario actual
        
    Returns:
        True si puede revisar, False en caso contrario
        
    Rules:
        - Superusuarios, Directores, Subdirectores y Operarios pueden revisar
        - Gerentes NO pueden revisar
    """
    return current_user.rol in [
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR,
        RolUsuario.SUBDIRECTOR,
        RolUsuario.OPERARIO
    ]


def can_access_configuracion(current_user: Usuario) -> bool:
    """
    Verifica si el usuario puede acceder a la configuración del sistema
    
    Args:
        current_user: Usuario actual
        
    Returns:
        True si puede acceder, False en caso contrario
        
    Rules:
        - Solo Superusuarios y Directores pueden acceder a configuración
    """
    return current_user.rol in [
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR
    ]


def can_access_auditoria(current_user: Usuario) -> bool:
    """
    Verifica si el usuario puede acceder a los logs de auditoría
    
    Args:
        current_user: Usuario actual
        
    Returns:
        True si puede acceder, False en caso contrario
        
    Rules:
        - Solo Superusuarios y Directores pueden acceder a auditoría completa
    """
    return current_user.rol in [
        RolUsuario.SUPERUSUARIO,
        RolUsuario.DIRECTOR
    ]


async def filter_empresas_by_access(
    current_user: Usuario,
    db: AsyncSession
) -> Optional[UUID]:
    """
    Retorna el filtro de empresa_id según el rol del usuario
    
    Args:
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        UUID de la empresa si es Gerente, None si tiene acceso a todas
        
    Usage:
        empresa_filter = await filter_empresas_by_access(current_user, db)
        if empresa_filter:
            query = query.where(Conductor.empresa_id == empresa_filter)
    """
    if current_user.rol == RolUsuario.GERENTE:
        return current_user.empresa_id
    
    return None
