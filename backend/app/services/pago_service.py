"""
Servicio de Pagos TUPA
"""
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.habilitacion import Pago, ConceptoTUPA, EstadoPago
from app.repositories.pago_repository import PagoRepository, ConceptoTUPARepository
from app.repositories.habilitacion_repository import HabilitacionRepository
from app.repositories.conductor_repository import ConductorRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.core.exceptions import RecursoNoEncontrado, ValidacionError
from app.schemas.pago import (
    PagoCreate,
    PagoResponse,
    PagoConDetalles,
    OrdenPago,
    ReporteIngresos,
    ConceptoTUPAResponse
)


class PagoService:
    """Servicio para gestión de pagos TUPA"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pago_repo = PagoRepository(db)
        self.concepto_repo = ConceptoTUPARepository(db)
        self.habilitacion_repo = HabilitacionRepository(db)
        self.conductor_repo = ConductorRepository(db)
        self.empresa_repo = EmpresaRepository(db)
    
    def _pago_to_dict(self, pago: Pago) -> dict:
        """Convierte un modelo Pago a diccionario con UUIDs como strings"""
        return {
            'id': str(pago.id),
            'habilitacion_id': str(pago.habilitacion_id),
            'concepto_tupa_id': str(pago.concepto_tupa_id),
            'numero_recibo': pago.numero_recibo,
            'monto': pago.monto,
            'fecha_pago': pago.fecha_pago,
            'entidad_bancaria': pago.entidad_bancaria,
            'estado': pago.estado,
            'observaciones': pago.observaciones,
            'registrado_por': str(pago.registrado_por) if pago.registrado_por else None,
            'fecha_confirmacion': pago.fecha_confirmacion,
            'confirmado_por': str(pago.confirmado_por) if pago.confirmado_por else None,
            'created_at': pago.created_at,
            'updated_at': pago.updated_at,
            'concepto_tupa': {
                'id': str(pago.concepto_tupa.id),
                'codigo': pago.concepto_tupa.codigo,
                'descripcion': pago.concepto_tupa.descripcion,
                'monto': pago.concepto_tupa.monto,
                'vigencia_desde': pago.concepto_tupa.vigencia_desde,
                'vigencia_hasta': pago.concepto_tupa.vigencia_hasta,
                'activo': pago.concepto_tupa.activo,
                'created_at': pago.concepto_tupa.created_at,
                'updated_at': pago.concepto_tupa.updated_at,
                'esta_vigente': pago.concepto_tupa.esta_vigente
            }
        }
    
    async def calcular_monto_tupa(
        self,
        tipo_tramite: str,
        fecha: Optional[date] = None
    ) -> Decimal:
        """
        Calcula el monto TUPA según tipo de trámite
        
        Args:
            tipo_tramite: Código del tipo de trámite
            fecha: Fecha para la cual calcular (por defecto hoy)
            
        Returns:
            Monto a pagar
            
        Raises:
            RecursoNoEncontrado: Si no existe concepto TUPA vigente
        """
        if fecha is None:
            fecha = date.today()
        
        concepto = await self.concepto_repo.get_concepto_vigente_por_codigo(
            codigo=tipo_tramite,
            fecha=fecha
        )
        
        if not concepto:
            raise RecursoNoEncontrado(
                recurso="ConceptoTUPA",
                id=f"código {tipo_tramite} vigente en {fecha}"
            )
        
        return concepto.monto
    
    async def generar_orden_pago(
        self,
        habilitacion_id: UUID,
        concepto_tupa_codigo: str = "HAB-CONDUCTOR"
    ) -> OrdenPago:
        """
        Genera una orden de pago para una habilitación
        
        Args:
            habilitacion_id: ID de la habilitación
            concepto_tupa_codigo: Código del concepto TUPA
            
        Returns:
            OrdenPago con los datos para el pago
            
        Raises:
            RecursoNoEncontrado: Si no existe la habilitación o concepto TUPA
            ValidacionError: Si ya existe un pago para la habilitación
        """
        # Verificar que la habilitación existe
        habilitacion = await self.habilitacion_repo.get_by_id_with_relations(habilitacion_id)
        if not habilitacion:
            raise RecursoNoEncontrado(recurso="Habilitacion", id=str(habilitacion_id))
        
        # Verificar que no existe ya un pago
        pago_existente = await self.pago_repo.get_by_habilitacion_id(habilitacion_id)
        if pago_existente:
            raise ValidacionError(
                campo="habilitacion_id",
                mensaje="Ya existe un pago registrado para esta habilitación"
            )
        
        # Obtener concepto TUPA vigente
        concepto = await self.concepto_repo.get_concepto_vigente_por_codigo(concepto_tupa_codigo)
        if not concepto:
            raise RecursoNoEncontrado(
                recurso="ConceptoTUPA",
                id=f"código {concepto_tupa_codigo}"
            )
        
        # Obtener datos del conductor
        conductor = habilitacion.conductor
        if not conductor:
            raise RecursoNoEncontrado(
                recurso="Conductor",
                id=str(habilitacion.conductor_id)
            )
        
        # Obtener datos de la empresa
        empresa = conductor.empresa
        if not empresa:
            raise RecursoNoEncontrado(
                recurso="Empresa",
                id=str(conductor.empresa_id)
            )
        
        # Generar código de orden
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        codigo_orden = f"OP-{habilitacion.codigo_habilitacion}-{timestamp}"
        
        # Fecha de vencimiento (30 días)
        fecha_vencimiento = date.today() + timedelta(days=30)
        
        # Convertir concepto a dict y luego a schema
        concepto_dict = {
            'id': str(concepto.id),
            'codigo': concepto.codigo,
            'descripcion': concepto.descripcion,
            'monto': concepto.monto,
            'vigencia_desde': concepto.vigencia_desde,
            'vigencia_hasta': concepto.vigencia_hasta,
            'activo': concepto.activo,
            'created_at': concepto.created_at,
            'updated_at': concepto.updated_at,
            'esta_vigente': concepto.esta_vigente
        }
        
        return OrdenPago(
            codigo_orden=codigo_orden,
            habilitacion_id=str(habilitacion.id),
            codigo_habilitacion=habilitacion.codigo_habilitacion,
            conductor_nombre=f"{conductor.nombres} {conductor.apellidos}",
            conductor_dni=conductor.dni,
            empresa_razon_social=empresa.razon_social,
            empresa_ruc=empresa.ruc,
            concepto_tupa=ConceptoTUPAResponse(**concepto_dict),
            monto_total=concepto.monto,
            fecha_emision=datetime.now(),
            fecha_vencimiento=fecha_vencimiento
        )
    
    async def registrar_pago(
        self,
        pago_data: PagoCreate,
        usuario_id: UUID
    ) -> PagoConDetalles:
        """
        Registra un nuevo pago
        
        Args:
            pago_data: Datos del pago
            usuario_id: ID del usuario que registra
            
        Returns:
            Pago registrado con detalles
            
        Raises:
            RecursoNoEncontrado: Si no existe habilitación o concepto TUPA
            ValidacionError: Si el monto no coincide o ya existe pago
        """
        # Convertir strings a UUID
        habilitacion_id = UUID(pago_data.habilitacion_id) if isinstance(pago_data.habilitacion_id, str) else pago_data.habilitacion_id
        concepto_tupa_id = UUID(pago_data.concepto_tupa_id) if isinstance(pago_data.concepto_tupa_id, str) else pago_data.concepto_tupa_id
        
        # Verificar que la habilitación existe
        habilitacion = await self.habilitacion_repo.get_by_id(habilitacion_id)
        if not habilitacion:
            raise RecursoNoEncontrado(
                recurso="Habilitacion",
                id=pago_data.habilitacion_id
            )
        
        # Verificar que no existe ya un pago
        pago_existente = await self.pago_repo.get_by_habilitacion_id(habilitacion_id)
        if pago_existente:
            raise ValidacionError(
                campo="habilitacion_id",
                mensaje="Ya existe un pago registrado para esta habilitación"
            )
        
        # Verificar que el concepto TUPA existe
        concepto = await self.concepto_repo.get_by_id(concepto_tupa_id)
        if not concepto:
            raise RecursoNoEncontrado(
                recurso="ConceptoTUPA",
                id=pago_data.concepto_tupa_id
            )
        
        # Validar que el monto coincide con el concepto TUPA
        if abs(pago_data.monto - concepto.monto) >= Decimal('0.01'):
            raise ValidacionError(
                campo="monto",
                mensaje=f"El monto pagado (S/. {pago_data.monto}) no coincide con el monto del concepto TUPA (S/. {concepto.monto})"
            )
        
        # Verificar que el número de recibo no existe
        recibo_existente = await self.pago_repo.get_by_numero_recibo(
            pago_data.numero_recibo
        )
        if recibo_existente:
            raise ValidacionError(
                campo="numero_recibo",
                mensaje=f"Ya existe un pago con el número de recibo {pago_data.numero_recibo}"
            )
        
        # Crear el pago
        pago_dict = {
            'habilitacion_id': habilitacion_id,
            'concepto_tupa_id': concepto_tupa_id,
            'numero_recibo': pago_data.numero_recibo,
            'monto': pago_data.monto,
            'fecha_pago': pago_data.fecha_pago,
            'entidad_bancaria': pago_data.entidad_bancaria,
            'observaciones': pago_data.observaciones,
            'registrado_por': usuario_id,
            'estado': EstadoPago.PENDIENTE
        }
        
        pago = await self.pago_repo.create(pago_dict)
        await self.db.commit()
        
        # Obtener el pago con relaciones
        pago_completo = await self.pago_repo.get_by_id_with_relations(pago.id)
        
        return PagoConDetalles(**self._pago_to_dict(pago_completo))
    
    async def verificar_pago_confirmado(
        self,
        habilitacion_id: UUID
    ) -> bool:
        """
        Verifica si el pago de una habilitación está confirmado
        
        Args:
            habilitacion_id: ID de la habilitación
            
        Returns:
            True si el pago está confirmado, False en caso contrario
        """
        pago = await self.pago_repo.get_by_habilitacion_id(habilitacion_id)
        
        if not pago:
            return False
        
        return pago.estado == EstadoPago.CONFIRMADO
    
    async def confirmar_pago(
        self,
        pago_id: UUID,
        usuario_id: UUID
    ) -> PagoConDetalles:
        """
        Confirma un pago pendiente
        
        Args:
            pago_id: ID del pago
            usuario_id: ID del usuario que confirma
            
        Returns:
            Pago confirmado
            
        Raises:
            RecursoNoEncontrado: Si no existe el pago
            ValidacionError: Si el pago no está pendiente
        """
        pago = await self.pago_repo.get_by_id(pago_id)
        if not pago:
            raise RecursoNoEncontrado(recurso="Pago", id=str(pago_id))
        
        if pago.estado != EstadoPago.PENDIENTE:
            raise ValidacionError(
                campo="estado",
                mensaje=f"El pago no puede ser confirmado porque está en estado {pago.estado}"
            )
        
        # Confirmar el pago
        pago.confirmar_pago(usuario_id)
        await self.db.commit()
        
        # Obtener el pago con relaciones
        pago_completo = await self.pago_repo.get_by_id_with_relations(pago.id)
        
        return PagoConDetalles(**self._pago_to_dict(pago_completo))
    
    async def rechazar_pago(
        self,
        pago_id: UUID,
        motivo: str,
        usuario_id: UUID
    ) -> PagoConDetalles:
        """
        Rechaza un pago
        
        Args:
            pago_id: ID del pago
            motivo: Motivo del rechazo
            usuario_id: ID del usuario que rechaza
            
        Returns:
            Pago rechazado
            
        Raises:
            RecursoNoEncontrado: Si no existe el pago
            ValidacionError: Si el pago no está pendiente
        """
        pago = await self.pago_repo.get_by_id(pago_id)
        if not pago:
            raise RecursoNoEncontrado(recurso="Pago", id=str(pago_id))
        
        if pago.estado != EstadoPago.PENDIENTE:
            raise ValidacionError(
                campo="estado",
                mensaje=f"El pago no puede ser rechazado porque está en estado {pago.estado}"
            )
        
        # Rechazar el pago
        pago.rechazar_pago(motivo)
        await self.db.commit()
        
        # Obtener el pago con relaciones
        pago_completo = await self.pago_repo.get_by_id_with_relations(pago.id)
        
        return PagoConDetalles(**self._pago_to_dict(pago_completo))
    
    async def generar_reporte_ingresos(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> ReporteIngresos:
        """
        Genera un reporte de ingresos por período
        
        Args:
            fecha_inicio: Fecha inicial del período
            fecha_fin: Fecha final del período
            
        Returns:
            ReporteIngresos con estadísticas del período
            
        Raises:
            ValidacionError: Si las fechas son inválidas
        """
        if fecha_inicio > fecha_fin:
            raise ValidacionError(
                campo="fecha_inicio",
                mensaje="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        # Obtener estadísticas del repositorio
        estadisticas = await self.pago_repo.get_estadisticas_por_periodo(
            fecha_inicio,
            fecha_fin
        )
        
        # Calcular totales
        total_pagos = 0
        total_confirmados = 0
        total_pendientes = 0
        total_rechazados = 0
        monto_total = Decimal('0')
        monto_confirmado = Decimal('0')
        monto_pendiente = Decimal('0')
        
        for estado, datos in estadisticas['por_estado'].items():
            cantidad = datos['cantidad']
            monto = Decimal(str(datos['monto_total']))
            
            total_pagos += cantidad
            monto_total += monto
            
            if estado == EstadoPago.CONFIRMADO:
                total_confirmados = cantidad
                monto_confirmado = monto
            elif estado == EstadoPago.PENDIENTE:
                total_pendientes = cantidad
                monto_pendiente = monto
            elif estado == EstadoPago.RECHAZADO:
                total_rechazados = cantidad
        
        return ReporteIngresos(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_pagos=total_pagos,
            total_confirmados=total_confirmados,
            total_pendientes=total_pendientes,
            total_rechazados=total_rechazados,
            monto_total=monto_total,
            monto_confirmado=monto_confirmado,
            monto_pendiente=monto_pendiente,
            pagos_por_concepto=estadisticas['por_concepto'],
            pagos_por_mes=estadisticas['por_mes']
        )
    
    async def get_pago_by_id(self, pago_id: UUID) -> PagoConDetalles:
        """
        Obtiene un pago por ID con detalles
        
        Args:
            pago_id: ID del pago
            
        Returns:
            Pago con detalles
            
        Raises:
            RecursoNoEncontrado: Si no existe el pago
        """
        pago = await self.pago_repo.get_by_id_with_relations(pago_id)
        if not pago:
            raise RecursoNoEncontrado(recurso="Pago", id=str(pago_id))
        
        return PagoConDetalles(**self._pago_to_dict(pago))
    
    async def get_pago_by_habilitacion(
        self,
        habilitacion_id: UUID
    ) -> Optional[PagoConDetalles]:
        """
        Obtiene el pago de una habilitación
        
        Args:
            habilitacion_id: ID de la habilitación
            
        Returns:
            Pago con detalles o None si no existe
        """
        pago = await self.pago_repo.get_by_habilitacion_id(habilitacion_id)
        if not pago:
            return None
        
        # Cargar relaciones
        pago_completo = await self.pago_repo.get_by_id_with_relations(pago.id)
        
        return PagoConDetalles(**self._pago_to_dict(pago_completo))
    
    async def get_pagos(
        self,
        estado: Optional[EstadoPago] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PagoConDetalles]:
        """
        Obtiene lista de pagos con filtros
        
        Args:
            estado: Estado opcional para filtrar
            fecha_inicio: Fecha inicial opcional
            fecha_fin: Fecha final opcional
            skip: Registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de pagos con detalles
        """
        if fecha_inicio and fecha_fin:
            pagos = await self.pago_repo.get_pagos_por_rango_fechas(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado,
                skip=skip,
                limit=limit
            )
        elif estado:
            pagos = await self.pago_repo.get_pagos_por_estado(
                estado=estado,
                skip=skip,
                limit=limit
            )
        else:
            filters = {}
            if estado:
                filters['estado'] = estado
            
            pagos = await self.pago_repo.get_all(
                skip=skip,
                limit=limit,
                filters=filters,
                order_by='fecha_pago',
                order_desc=True
            )
        
        return [PagoConDetalles(**self._pago_to_dict(pago)) for pago in pagos]
