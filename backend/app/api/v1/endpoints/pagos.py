"""
Endpoints para gestión de pagos TUPA
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import Usuario
from app.models.habilitacion import EstadoPago
from app.services.pago_service import PagoService
from app.schemas.pago import PagoCreate, PagoConDetalles, OrdenPago, ReporteIngresos
from app.core.exceptions import RecursoNoEncontrado, ValidacionError

router = APIRouter()


@router.get("", response_model=List[PagoConDetalles])
async def get_pagos(
    estado: Optional[EstadoPago] = Query(None, description="Filtrar por estado"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha inicial"),
    fecha_fin: Optional[date] = Query(None, description="Fecha final"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener lista de pagos con filtros opcionales"""
    service = PagoService(db)
    pagos = await service.get_pagos(estado=estado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, skip=skip, limit=limit)
    return pagos


@router.post("", response_model=PagoConDetalles, status_code=status.HTTP_201_CREATED)
async def registrar_pago(
    pago_data: PagoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registrar un nuevo pago"""
    service = PagoService(db)
    try:
        pago = await service.registrar_pago(pago_data, current_user.id)
        return pago
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{pago_id}", response_model=PagoConDetalles)
async def get_pago(
    pago_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener un pago por ID"""
    service = PagoService(db)
    try:
        pago = await service.get_pago_by_id(pago_id)
        return pago
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/habilitacion/{habilitacion_id}", response_model=PagoConDetalles)
async def get_pago_by_habilitacion(
    habilitacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtener el pago de una habilitación"""
    service = PagoService(db)
    pago = await service.get_pago_by_habilitacion(habilitacion_id)
    if not pago:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró pago para la habilitación {habilitacion_id}")
    return pago


@router.get("/{pago_id}/orden-pago", response_model=dict)
async def descargar_orden_pago(
    pago_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Descargar orden de pago"""
    service = PagoService(db)
    try:
        pago = await service.get_pago_by_id(pago_id)
        return {"message": "Funcionalidad pendiente", "pago_id": str(pago_id), "numero_recibo": pago.numero_recibo}
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{pago_id}/confirmar", response_model=PagoConDetalles)
async def confirmar_pago(
    pago_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Confirmar un pago pendiente"""
    service = PagoService(db)
    try:
        pago = await service.confirmar_pago(pago_id, current_user.id)
        return pago
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{pago_id}/rechazar", response_model=PagoConDetalles)
async def rechazar_pago(
    pago_id: UUID,
    motivo: str = Query(..., description="Motivo del rechazo"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Rechazar un pago"""
    service = PagoService(db)
    try:
        pago = await service.rechazar_pago(pago_id, motivo, current_user.id)
        return pago
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/reportes/ingresos", response_model=ReporteIngresos)
async def generar_reporte_ingresos(
    fecha_inicio: date = Query(..., description="Fecha inicial del reporte"),
    fecha_fin: date = Query(..., description="Fecha final del reporte"),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Generar reporte de ingresos por período"""
    service = PagoService(db)
    try:
        reporte = await service.generar_reporte_ingresos(fecha_inicio, fecha_fin)
        return reporte
    except ValidacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/habilitacion/{habilitacion_id}/generar-orden", response_model=OrdenPago)
async def generar_orden_pago(
    habilitacion_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Generar orden de pago para una habilitación"""
    service = PagoService(db)
    try:
        orden = await service.generar_orden_pago(habilitacion_id)
        return orden
    except RecursoNoEncontrado as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidacionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
