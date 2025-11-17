"""
Endpoints para gestión de empresas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_roles
from app.models.user import Usuario, RolUsuario
from app.schemas.empresa import (
    EmpresaCreate,
    EmpresaUpdate,
    EmpresaResponse,
    EmpresaListResponse,
    AutorizacionEmpresaCreate,
    AutorizacionEmpresaResponse
)
from app.schemas.auth import MessageResponse
from app.services.empresa_service import EmpresaService
from app.core.exceptions import RecursoNoEncontrado, ValidacionError
import math


router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.get(
    "/mi-empresa",
    response_model=EmpresaResponse,
    summary="Obtener empresa del gerente",
    description="Obtiene la empresa asignada al gerente actual"
)
@require_roles(RolUsuario.GERENTE)
async def obtener_mi_empresa(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la empresa del gerente actual
    
    Solo accesible para usuarios con rol GERENTE
    """
    from app.core.dependencies import get_empresa_gerente
    
    try:
        empresa = await get_empresa_gerente(current_user, db)
        return empresa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empresa: {str(e)}"
        )


@router.get(
    "",
    response_model=EmpresaListResponse,
    summary="Listar empresas",
    description="Obtiene lista de empresas con paginación y filtros"
)
async def listar_empresas(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    ruc: Optional[str] = Query(None, description="Filtrar por RUC"),
    razon_social: Optional[str] = Query(None, description="Filtrar por razón social"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Lista empresas con paginación y filtros"""
    service = EmpresaService(db)
    
    # Preparar filtros
    filtros = {}
    if ruc:
        filtros["ruc"] = ruc
    if razon_social:
        filtros["razon_social"] = razon_social
    if activo is not None:
        filtros["activo"] = activo
    
    # Si es Gerente, solo puede ver su empresa
    if current_user.rol == RolUsuario.GERENTE:
        if current_user.empresa_id:
            filtros["id"] = current_user.empresa_id
        else:
            # Gerente sin empresa asignada no ve nada
            return EmpresaListResponse(
                items=[],
                total=0,
                page=skip // limit + 1 if limit > 0 else 1,
                page_size=limit,
                total_pages=0
            )
    
    empresas = await service.obtener_empresas(skip=skip, limit=limit, filtros=filtros)
    total = await service.contar_empresas(filtros=filtros)
    
    return EmpresaListResponse(
        items=empresas,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        total_pages=math.ceil(total / limit) if limit > 0 else 0
    )


@router.post(
    "",
    response_model=EmpresaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear empresa",
    description="Crea una nueva empresa. SUPERUSUARIO, DIRECTOR, SUBDIRECTOR."
)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def crear_empresa(
    empresa_data: EmpresaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea una nueva empresa"""
    service = EmpresaService(db)
    
    try:
        empresa = await service.registrar_empresa(empresa_data)
        return empresa
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message, "campo": e.campo}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    summary="Obtener empresa",
    description="Obtiene una empresa por ID"
)
async def obtener_empresa(
    empresa_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene una empresa por ID"""
    service = EmpresaService(db)
    
    try:
        empresa = await service.obtener_empresa(empresa_id)
        
        # Si es Gerente, solo puede ver su empresa
        if current_user.rol == RolUsuario.GERENTE:
            if not current_user.empresa_id or str(empresa.id) != str(current_user.empresa_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"error": "PERMISOS_DENEGADOS", "message": "No tiene permisos para ver esta empresa"}
                )
        
        return empresa
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message}
        )


@router.put(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    summary="Actualizar empresa",
    description="Actualiza una empresa existente. SUPERUSUARIO, DIRECTOR, SUBDIRECTOR."
)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def actualizar_empresa(
    empresa_id: str,
    empresa_data: EmpresaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza una empresa existente"""
    service = EmpresaService(db)
    
    try:
        empresa = await service.actualizar_empresa(empresa_id, empresa_data)
        return empresa
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )


@router.get(
    "/{empresa_id}/conductores",
    response_model=List[dict],  # Will be ConductorResponse when implemented
    summary="Obtener conductores de empresa",
    description="Obtiene los conductores de una empresa"
)
async def obtener_conductores_empresa(
    empresa_id: str,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los conductores de una empresa"""
    service = EmpresaService(db)
    
    try:
        # Verificar permisos
        if current_user.rol == RolUsuario.GERENTE:
            if not current_user.empresa_id or str(current_user.empresa_id) != empresa_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"error": "PERMISOS_DENEGADOS", "message": "No tiene permisos para ver conductores de esta empresa"}
                )
        
        conductores = await service.obtener_conductores_empresa(
            empresa_id,
            skip=skip,
            limit=limit
        )
        
        # Convertir a dict temporalmente (hasta que tengamos ConductorResponse)
        return [
            {
                "id": str(c.id),
                "dni": c.dni,
                "nombres": c.nombres,
                "apellidos": c.apellidos,
                "estado": c.estado.value if hasattr(c.estado, 'value') else c.estado
            }
            for c in conductores
        ]
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message}
        )


@router.post(
    "/{empresa_id}/autorizaciones",
    response_model=AutorizacionEmpresaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar autorización a empresa",
    description="Agrega una autorización a una empresa. SUPERUSUARIO, DIRECTOR, SUBDIRECTOR."
)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def agregar_autorizacion(
    empresa_id: str,
    autorizacion_data: AutorizacionEmpresaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Agrega una autorización a una empresa"""
    service = EmpresaService(db)
    
    try:
        autorizacion = await service.agregar_autorizacion(empresa_id, autorizacion_data)
        return autorizacion
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.code, "message": e.message}
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "ERROR_INTERNO", "message": str(e)}
        )
