"""
Endpoints para gestión de usuarios
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_roles
from app.models.user import Usuario, RolUsuario
from app.schemas.user import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    CambiarPasswordRequest
)
from app.schemas.auth import MessageResponse
from app.services.usuario_service import UsuarioService
from app.core.exceptions import RecursoNoEncontrado, ValidacionError


router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get(
    "",
    response_model=List[UsuarioResponse],
    summary="Listar usuarios",
    description="Obtiene lista de usuarios con paginación. Requiere permiso de lectura en módulo usuarios."
)
async def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    rol: Optional[RolUsuario] = Query(None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista usuarios con paginación y filtros"""
    service = UsuarioService(db)
    
    # Preparar filtros
    filtros = {}
    if rol:
        filtros["rol"] = rol
    if activo is not None:
        filtros["activo"] = activo
    
    usuarios = await service.listar_usuarios(skip=skip, limit=limit, filtros=filtros)
    return usuarios



@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Crea un nuevo usuario. Solo SUPERUSUARIO."
)
@require_roles([RolUsuario.SUPERUSUARIO])
async def crear_usuario(
    usuario_data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea un nuevo usuario"""
    service = UsuarioService(db)
    
    try:
        usuario = await service.crear_usuario(usuario_data, current_user)
        await db.commit()
        return usuario
    except ValidacionError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message, "campo": e.campo}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario",
    description="Obtiene un usuario por ID"
)
async def obtener_usuario(
    usuario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene un usuario por ID"""
    service = UsuarioService(db)
    
    try:
        usuario = await service.obtener_usuario(usuario_id)
        
        # Verificar permisos: solo admin o el mismo usuario
        if not current_user.es_administrador() and str(current_user.id) != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "PERMISOS_DENEGADOS", "message": "No tiene permisos para ver este usuario"}
            )
        
        return usuario
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message, "campo": e.campo}
        )



@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario",
    description="Actualiza un usuario existente"
)
async def actualizar_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza un usuario existente"""
    service = UsuarioService(db)
    
    try:
        # Verificar permisos: solo admin o el mismo usuario (pero usuario no puede cambiar su rol)
        if not current_user.es_administrador() and str(current_user.id) != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "PERMISOS_DENEGADOS", "message": "No tiene permisos para actualizar este usuario"}
            )
        
        # Si no es admin, no puede cambiar rol ni empresa_id
        if not current_user.es_administrador():
            if usuario_data.rol is not None or usuario_data.empresa_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"error": "PERMISOS_DENEGADOS", "message": "No puede cambiar rol o empresa"}
                )
        
        usuario = await service.actualizar_usuario(usuario_id, usuario_data, current_user)
        await db.commit()
        return usuario
    except RecursoNoEncontrado as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message, "campo": e.campo}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )


@router.delete(
    "/{usuario_id}",
    response_model=MessageResponse,
    summary="Eliminar usuario",
    description="Desactiva un usuario (soft delete)"
)
async def eliminar_usuario(
    usuario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Desactiva un usuario (soft delete)"""
    service = UsuarioService(db)
    
    try:
        # Verificar permisos: solo admin
        if not current_user.es_administrador():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "PERMISOS_DENEGADOS", "message": "No tiene permisos para eliminar usuarios"}
            )
        
        # No permitir que se elimine a sí mismo
        if str(current_user.id) == usuario_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "VALIDACION_ERROR", "message": "No puede eliminarse a sí mismo"}
            )
        
        await service.desactivar_usuario(usuario_id)
        await db.commit()
        return MessageResponse(message="Usuario desactivado exitosamente")
    except RecursoNoEncontrado as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message, "campo": e.campo}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )



@router.post(
    "/{usuario_id}/cambiar-password",
    response_model=MessageResponse,
    summary="Cambiar contraseña",
    description="Cambia la contraseña de un usuario"
)
async def cambiar_password(
    usuario_id: str,
    password_data: CambiarPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cambia la contraseña de un usuario"""
    service = UsuarioService(db)
    
    try:
        # Solo el mismo usuario puede cambiar su contraseña
        if str(current_user.id) != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "PERMISOS_DENEGADOS", "message": "Solo puede cambiar su propia contraseña"}
            )
        
        await service.cambiar_password(usuario_id, password_data)
        await db.commit()
        return MessageResponse(message="Contraseña cambiada exitosamente")
    except RecursoNoEncontrado as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message, "campo": e.campo}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )
