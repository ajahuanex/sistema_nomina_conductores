"""
Endpoints para gestión de habilitaciones
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_roles
from app.core.exceptions import RecursoNoEncontrado, ValidacionError
from app.models.user import Usuario, RolUsuario
from app.models.habilitacion import EstadoHabilitacion
from app.services.habilitacion_service import HabilitacionService
from app.schemas.habilitacion import (
    HabilitacionResponse,
    HabilitacionReview,
    HabilitacionAprobacion,
    HabilitacionObservacion,
    HabilitacionHabilitar,
    HabilitacionSuspension
)

router = APIRouter(prefix="/habilitaciones", tags=["habilitaciones"])


@router.get("", response_model=List[HabilitacionResponse], status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO)
async def listar_habilitaciones(
    estado: Optional[EstadoHabilitacion] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar habilitaciones con filtros por estado
    
    - **estado**: Estado de la habilitación (opcional)
    - **skip**: Número de registros a saltar para paginación
    - **limit**: Número máximo de registros a retornar
    
    Retorna lista de habilitaciones
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO
    """
    try:
        service = HabilitacionService(db)
        habilitaciones = await service.obtener_habilitaciones(
            estado=estado,
            skip=skip,
            limit=limit
        )
        return habilitaciones
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo habilitaciones: {str(e)}"
        )


@router.get("/pendientes", response_model=List[HabilitacionResponse], status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO)
async def listar_habilitaciones_pendientes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Listar habilitaciones pendientes de revisión
    
    - **skip**: Número de registros a saltar para paginación
    - **limit**: Número máximo de registros a retornar
    
    Retorna lista de habilitaciones en estado PENDIENTE
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO
    """
    try:
        service = HabilitacionService(db)
        habilitaciones = await service.obtener_solicitudes_pendientes(
            skip=skip,
            limit=limit
        )
        return habilitaciones
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo habilitaciones pendientes: {str(e)}"
        )


@router.get("/{habilitacion_id}", response_model=HabilitacionResponse, status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def obtener_habilitacion(
    habilitacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener detalles de una habilitación específica
    
    - **habilitacion_id**: ID de la habilitación
    
    Retorna los detalles completos de la habilitación
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE
    """
    try:
        service = HabilitacionService(db)
        habilitacion = await service.obtener_habilitacion(habilitacion_id)
        return habilitacion
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo habilitación: {str(e)}"
        )


@router.post("/{habilitacion_id}/revisar", response_model=HabilitacionResponse, status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO)
async def revisar_solicitud(
    habilitacion_id: UUID,
    data: HabilitacionReview,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar solicitud a estado EN_REVISION
    
    - **habilitacion_id**: ID de la habilitación
    - **observaciones**: Observaciones del revisor (opcional)
    
    Cambia el estado de PENDIENTE a EN_REVISION
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO
    """
    try:
        service = HabilitacionService(db)
        habilitacion = await service.revisar_solicitud(
            habilitacion_id=habilitacion_id,
            usuario_id=current_user.id,
            observaciones=data.observaciones
        )
        return habilitacion
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error revisando solicitud: {str(e)}"
        )


@router.post("/{habilitacion_id}/aprobar", response_model=HabilitacionResponse, status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def aprobar_solicitud(
    habilitacion_id: UUID,
    data: HabilitacionAprobacion,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Aprobar solicitud de habilitación
    
    - **habilitacion_id**: ID de la habilitación
    - **observaciones**: Comentarios adicionales sobre la aprobación (opcional)
    
    Cambia el estado de EN_REVISION a APROBADO después de validar documentos
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR
    """
    try:
        service = HabilitacionService(db)
        habilitacion = await service.aprobar_solicitud(
            habilitacion_id=habilitacion_id,
            usuario_id=current_user.id,
            observaciones=data.observaciones
        )
        return habilitacion
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error aprobando solicitud: {str(e)}"
        )


@router.post("/{habilitacion_id}/observar", response_model=HabilitacionResponse, status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO)
async def observar_solicitud(
    habilitacion_id: UUID,
    data: HabilitacionObservacion,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Observar solicitud de habilitación
    
    - **habilitacion_id**: ID de la habilitación
    - **observaciones**: Observaciones detalladas sobre los problemas encontrados
    
    Cambia el estado de EN_REVISION a OBSERVADO con comentarios específicos
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO
    """
    try:
        service = HabilitacionService(db)
        habilitacion = await service.observar_solicitud(
            habilitacion_id=habilitacion_id,
            observaciones=data.observaciones,
            usuario_id=current_user.id
        )
        return habilitacion
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error observando solicitud: {str(e)}"
        )


@router.post("/{habilitacion_id}/habilitar", response_model=HabilitacionResponse, status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def habilitar_conductor(
    habilitacion_id: UUID,
    data: HabilitacionHabilitar,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Habilitar conductor después de verificar pago
    
    - **habilitacion_id**: ID de la habilitación
    - **vigencia_hasta**: Fecha de vencimiento de la habilitación
    - **observaciones**: Comentarios adicionales (opcional)
    
    Cambia el estado de APROBADO a HABILITADO después de verificar pago confirmado
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR
    """
    try:
        service = HabilitacionService(db)
        habilitacion = await service.habilitar_conductor(
            habilitacion_id=habilitacion_id,
            usuario_id=current_user.id,
            vigencia_hasta=data.vigencia_hasta,
            observaciones=data.observaciones
        )
        return habilitacion
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error habilitando conductor: {str(e)}"
        )


@router.post("/{habilitacion_id}/suspender", response_model=HabilitacionResponse, status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR)
async def suspender_habilitacion(
    habilitacion_id: UUID,
    data: HabilitacionSuspension,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Suspender habilitación de conductor
    
    - **habilitacion_id**: ID de la habilitación
    - **motivo**: Justificación detallada de la suspensión
    
    Suspende una habilitación HABILITADA con justificación documentada
    
    Requiere roles: SUPERUSUARIO, DIRECTOR
    """
    try:
        service = HabilitacionService(db)
        habilitacion = await service.suspender_habilitacion(
            habilitacion_id=habilitacion_id,
            motivo=data.motivo,
            usuario_id=current_user.id
        )
        return habilitacion
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suspendiendo habilitación: {str(e)}"
        )


@router.get("/{habilitacion_id}/certificado", status_code=status.HTTP_200_OK)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def descargar_certificado(
    habilitacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Descargar certificado de habilitación en PDF
    
    - **habilitacion_id**: ID de la habilitación
    
    Retorna el certificado en formato PDF
    
    Requiere roles: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE
    """
    try:
        service = HabilitacionService(db)
        
        # Generar certificado
        pdf_bytes = await service.generar_certificado(habilitacion_id)
        
        # Obtener habilitación para el nombre del archivo
        habilitacion = await service.obtener_habilitacion(habilitacion_id)
        filename = f"certificado_{habilitacion.codigo_habilitacion}.pdf"
        
        # Retornar PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando certificado: {str(e)}"
        )
