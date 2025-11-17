"""
Dependencias de FastAPI para inyección de dependencias
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import Usuario


# Esquema de seguridad HTTP Bearer
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario actual desde el token JWT
    Valida el token, verifica que el usuario exista y esté activo
    
    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe/inactivo
    """
    token = credentials.credentials
    
    # Verificar el token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener el ID del usuario del payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: falta identificador de usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar el usuario en la base de datos
    from uuid import UUID
    try:
        user_uuid = UUID(user_id)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: identificador de usuario malformado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(
        select(Usuario).where(Usuario.id == user_uuid)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
        )
    
    return user


async def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Obtiene el usuario actual y verifica que esté activo
    
    Args:
        current_user: Usuario actual
        
    Returns:
        Usuario activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[Usuario]:
    """
    Obtiene el usuario actual si existe un token, None en caso contrario
    Útil para endpoints que pueden funcionar con o sin autenticación
    
    Args:
        credentials: Credenciales HTTP Bearer (opcional)
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado o None
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None



async def get_empresa_gerente(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la empresa del gerente actual
    Solo funciona si el usuario es gerente y tiene empresa asignada
    
    Args:
        current_user: Usuario actual
        db: Sesión de base de datos
        
    Returns:
        Empresa del gerente
        
    Raises:
        HTTPException: Si el usuario no es gerente o no tiene empresa asignada
    """
    from app.models.user import RolUsuario
    from app.models.empresa import Empresa
    
    if current_user.rol != RolUsuario.GERENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los gerentes pueden acceder a esta funcionalidad"
        )
    
    if not current_user.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El gerente no tiene una empresa asignada"
        )
    
    # Obtener la empresa con sus relaciones
    result = await db.execute(
        select(Empresa).where(Empresa.id == current_user.empresa_id)
    )
    empresa = result.scalar_one_or_none()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada"
        )
    
    if not empresa.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La empresa está inactiva"
        )
    
    return empresa


def require_admin_or_gerente_own_empresa(empresa_id: str):
    """
    Dependency factory que valida que el usuario sea admin o gerente de la empresa especificada
    
    Args:
        empresa_id: ID de la empresa a validar
        
    Returns:
        Dependency function
    """
    async def _validate(
        current_user: Usuario = Depends(get_current_user)
    ):
        from app.models.user import RolUsuario
        from uuid import UUID
        
        # Admins pueden acceder a cualquier empresa
        if current_user.es_administrador():
            return current_user
        
        # Gerentes solo pueden acceder a su propia empresa
        if current_user.rol == RolUsuario.GERENTE:
            if not current_user.empresa_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Gerente sin empresa asignada"
                )
            
            try:
                empresa_uuid = UUID(empresa_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de empresa inválido"
                )
            
            if current_user.empresa_id != empresa_uuid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para acceder a esta empresa"
                )
            
            return current_user
        
        # Otros roles no tienen acceso
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta funcionalidad"
        )
    
    return _validate



def require_module_permission(modulo: str, accion: str = "leer"):
    """
    Dependency factory que verifica permisos de módulo
    
    Args:
        modulo: Nombre del módulo (usuarios, empresas, conductores, etc.)
        accion: Tipo de acción (leer, crear, editar, eliminar)
        
    Returns:
        Dependency function
        
    Example:
        @router.get("/usuarios")
        async def listar_usuarios(
            current_user: Usuario = Depends(require_module_permission("usuarios", "leer"))
        ):
            ...
    """
    async def _validate(
        current_user: Usuario = Depends(get_current_user)
    ):
        from app.models.user import RolUsuario
        
        # Superusuario siempre tiene acceso
        if current_user.rol == RolUsuario.SUPERUSUARIO:
            return current_user
        
        # Verificar permiso específico
        if not current_user.tiene_permiso_modulo(modulo, accion):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permisos para {accion} en el módulo {modulo}"
            )
        
        return current_user
    
    return _validate
