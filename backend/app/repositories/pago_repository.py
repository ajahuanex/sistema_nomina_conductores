"""
Repositorio para Pago y ConceptoTUPA
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy import select, and_, or_, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.habilitacion import Pago, ConceptoTUPA, EstadoPago
from app.repositories.base import BaseRepository


class ConceptoTUPARepository(BaseRepository[ConceptoTUPA]):
    """Repositorio para ConceptoTUPA"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ConceptoTUPA, db)
    
    async def get_by_codigo(self, codigo: str) -> Optional[ConceptoTUPA]:
        result = await self.db.execute(
            select(ConceptoTUPA).where(ConceptoTUPA.codigo == codigo)
        )
        return result.scalar_one_or_none()
    
    async def get_vigentes(self, fecha: Optional[date] = None) -> List[ConceptoTUPA]:
        if fecha is None:
            fecha = date.today()
        result = await self.db.execute(
            select(ConceptoTUPA).where(
                and_(
                    ConceptoTUPA.activo == True,
                    ConceptoTUPA.vigencia_desde <= fecha,
                    or_(
                        ConceptoTUPA.vigencia_hasta.is_(None),
                        ConceptoTUPA.vigencia_hasta >= fecha
                    )
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_concepto_vigente_por_codigo(self, codigo: str, fecha: Optional[date] = None) -> Optional[ConceptoTUPA]:
        if fecha is None:
            fecha = date.today()
        result = await self.db.execute(
            select(ConceptoTUPA).where(
                and_(
                    ConceptoTUPA.codigo == codigo,
                    ConceptoTUPA.activo == True,
                    ConceptoTUPA.vigencia_desde <= fecha,
                    or_(
                        ConceptoTUPA.vigencia_hasta.is_(None),
                        ConceptoTUPA.vigencia_hasta >= fecha
                    )
                )
            )
        )
        return result.scalar_one_or_none()


class PagoRepository(BaseRepository[Pago]):
    """Repositorio para Pago"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Pago, db)
    
    async def get_by_id_with_relations(self, id: UUID) -> Optional[Pago]:
        result = await self.db.execute(
            select(Pago).options(
                selectinload(Pago.concepto_tupa),
                selectinload(Pago.habilitacion),
                selectinload(Pago.registrador),
                selectinload(Pago.confirmador)
            ).where(Pago.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_habilitacion_id(self, habilitacion_id: UUID) -> Optional[Pago]:
        result = await self.db.execute(
            select(Pago).options(selectinload(Pago.concepto_tupa)).where(Pago.habilitacion_id == habilitacion_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_numero_recibo(self, numero_recibo: str) -> Optional[Pago]:
        result = await self.db.execute(
            select(Pago).where(Pago.numero_recibo == numero_recibo)
        )
        return result.scalar_one_or_none()
    
    async def get_pagos_por_estado(self, estado: EstadoPago, skip: int = 0, limit: int = 100) -> List[Pago]:
        result = await self.db.execute(
            select(Pago).options(
                selectinload(Pago.concepto_tupa),
                selectinload(Pago.habilitacion)
            ).where(Pago.estado == estado).order_by(Pago.fecha_pago.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_pagos_por_rango_fechas(self, fecha_inicio: date, fecha_fin: date, estado: Optional[EstadoPago] = None, skip: int = 0, limit: int = 100) -> List[Pago]:
        conditions = [Pago.fecha_pago >= fecha_inicio, Pago.fecha_pago <= fecha_fin]
        if estado:
            conditions.append(Pago.estado == estado)
        result = await self.db.execute(
            select(Pago).options(
                selectinload(Pago.concepto_tupa),
                selectinload(Pago.habilitacion)
            ).where(and_(*conditions)).order_by(Pago.fecha_pago.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_estadisticas_por_periodo(self, fecha_inicio: date, fecha_fin: date) -> dict:
        result_estados = await self.db.execute(
            select(Pago.estado, func.count(Pago.id).label('cantidad'), func.sum(Pago.monto).label('monto_total'))
            .where(and_(Pago.fecha_pago >= fecha_inicio, Pago.fecha_pago <= fecha_fin))
            .group_by(Pago.estado)
        )
        estadisticas_estados = {}
        for row in result_estados:
            estadisticas_estados[row.estado] = {'cantidad': row.cantidad, 'monto_total': float(row.monto_total) if row.monto_total else 0}
        result_conceptos = await self.db.execute(
            select(ConceptoTUPA.codigo, ConceptoTUPA.descripcion, func.count(Pago.id).label('cantidad'), func.sum(Pago.monto).label('monto_total'))
            .join(Pago.concepto_tupa)
            .where(and_(Pago.fecha_pago >= fecha_inicio, Pago.fecha_pago <= fecha_fin))
            .group_by(ConceptoTUPA.codigo, ConceptoTUPA.descripcion)
        )
        pagos_por_concepto = []
        for row in result_conceptos:
            pagos_por_concepto.append({'codigo': row.codigo, 'descripcion': row.descripcion, 'cantidad': row.cantidad, 'monto_total': float(row.monto_total) if row.monto_total else 0})
        result_meses = await self.db.execute(
            select(extract('year', Pago.fecha_pago).label('anio'), extract('month', Pago.fecha_pago).label('mes'), func.count(Pago.id).label('cantidad'), func.sum(Pago.monto).label('monto_total'))
            .where(and_(Pago.fecha_pago >= fecha_inicio, Pago.fecha_pago <= fecha_fin))
            .group_by('anio', 'mes').order_by('anio', 'mes')
        )
        pagos_por_mes = []
        for row in result_meses:
            pagos_por_mes.append({'anio': int(row.anio), 'mes': int(row.mes), 'cantidad': row.cantidad, 'monto_total': float(row.monto_total) if row.monto_total else 0})
        return {'por_estado': estadisticas_estados, 'por_concepto': pagos_por_concepto, 'por_mes': pagos_por_mes}
