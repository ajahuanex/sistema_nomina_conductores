"""
Servicio de Habilitación
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.habilitacion import Habilitacion, EstadoHabilitacion, Pago, EstadoPago
from app.models.conductor import Conductor, EstadoConductor
from app.repositories.habilitacion_repository import HabilitacionRepository
from app.repositories.conductor_repository import ConductorRepository
from app.core.exceptions import (
    RecursoNoEncontrado,
    ValidacionError,
    PermisosDenegados
)


class HabilitacionService:
    """Servicio para gestionar habilitaciones de conductores"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.habilitacion_repo = HabilitacionRepository(db)
        self.conductor_repo = ConductorRepository(db)
    
    async def crear_solicitud(
        self,
        conductor_id: UUID,
        usuario_id: Optional[UUID] = None
    ) -> Habilitacion:
        """
        Crear solicitud de habilitación automáticamente al registrar conductor
        
        Args:
            conductor_id: ID del conductor
            usuario_id: ID del usuario que crea la solicitud (opcional)
            
        Returns:
            Habilitación creada
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
            ValidacionError: Si el conductor ya tiene una habilitación activa
        """
        # Verificar que el conductor existe
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        # Verificar que no tenga una habilitación activa
        ultima_habilitacion = await self.habilitacion_repo.get_ultima_habilitacion_conductor(
            conductor_id
        )
        
        if ultima_habilitacion and ultima_habilitacion.estado in [
            EstadoHabilitacion.PENDIENTE,
            EstadoHabilitacion.EN_REVISION,
            EstadoHabilitacion.APROBADO,
            EstadoHabilitacion.HABILITADO
        ]:
            raise ValidacionError(
                "conductor_id",
                f"El conductor ya tiene una habilitación en estado {ultima_habilitacion.estado.value}"
            )
        
        # Generar código único de habilitación
        codigo_habilitacion = await self._generar_codigo_unico()
        
        # Crear habilitación
        habilitacion = Habilitacion(
            conductor_id=conductor_id,
            codigo_habilitacion=codigo_habilitacion,
            estado=EstadoHabilitacion.PENDIENTE,
            fecha_solicitud=datetime.utcnow()
        )
        
        self.db.add(habilitacion)
        await self.db.commit()
        await self.db.refresh(habilitacion)
        
        # Actualizar estado del conductor a PENDIENTE
        conductor.estado = EstadoConductor.PENDIENTE
        await self.db.commit()
        
        return habilitacion
    
    async def obtener_solicitudes_pendientes(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener solicitudes pendientes de revisión
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones pendientes
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.estado == EstadoHabilitacion.PENDIENTE)
            .order_by(Habilitacion.fecha_solicitud)
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def revisar_solicitud(
        self,
        habilitacion_id: UUID,
        usuario_id: UUID,
        observaciones: Optional[str] = None
    ) -> Habilitacion:
        """
        Cambiar solicitud a EN_REVISION
        
        Args:
            habilitacion_id: ID de la habilitación
            usuario_id: ID del usuario que revisa
            observaciones: Observaciones del revisor
            
        Returns:
            Habilitación actualizada
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si la habilitación no está en estado PENDIENTE
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        if habilitacion.estado != EstadoHabilitacion.PENDIENTE:
            raise ValidacionError(
                "estado",
                f"Solo se pueden revisar habilitaciones en estado PENDIENTE. Estado actual: {habilitacion.estado.value}"
            )
        
        # Actualizar estado
        habilitacion.estado = EstadoHabilitacion.EN_REVISION
        habilitacion.revisado_por = usuario_id
        habilitacion.fecha_revision = datetime.utcnow()
        
        if observaciones:
            habilitacion.observaciones = observaciones
        
        await self.db.commit()
        await self.db.refresh(habilitacion, ['pago'])
        
        return habilitacion
    
    async def aprobar_solicitud(
        self,
        habilitacion_id: UUID,
        usuario_id: UUID,
        observaciones: Optional[str] = None
    ) -> Habilitacion:
        """
        Aprobar solicitud con validación de documentos
        
        Args:
            habilitacion_id: ID de la habilitación
            usuario_id: ID del usuario que aprueba
            observaciones: Observaciones adicionales
            
        Returns:
            Habilitación aprobada
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si la habilitación no puede ser aprobada
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        if not habilitacion.puede_aprobar():
            raise ValidacionError(
                "estado",
                f"Solo se pueden aprobar habilitaciones en estado EN_REVISION. Estado actual: {habilitacion.estado.value}"
            )
        
        # Validar que el conductor tenga documentos necesarios
        conductor = await self.conductor_repo.get_by_id(habilitacion.conductor_id)
        await self._validar_documentos_conductor(conductor)
        
        # Actualizar estado
        habilitacion.estado = EstadoHabilitacion.APROBADO
        habilitacion.aprobado_por = usuario_id
        habilitacion.fecha_aprobacion = datetime.utcnow()
        
        if observaciones:
            if habilitacion.observaciones:
                habilitacion.observaciones += f"\n\nAprobación: {observaciones}"
            else:
                habilitacion.observaciones = f"Aprobación: {observaciones}"
        
        await self.db.commit()
        await self.db.refresh(habilitacion, ['pago'])
        
        return habilitacion
    
    async def observar_solicitud(
        self,
        habilitacion_id: UUID,
        observaciones: str,
        usuario_id: UUID
    ) -> Habilitacion:
        """
        Observar solicitud con comentarios
        
        Args:
            habilitacion_id: ID de la habilitación
            observaciones: Observaciones detalladas
            usuario_id: ID del usuario que observa
            
        Returns:
            Habilitación observada
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si la habilitación no está en revisión
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        if habilitacion.estado != EstadoHabilitacion.EN_REVISION:
            raise ValidacionError(
                "estado",
                f"Solo se pueden observar habilitaciones en estado EN_REVISION. Estado actual: {habilitacion.estado.value}"
            )
        
        # Actualizar estado
        habilitacion.estado = EstadoHabilitacion.OBSERVADO
        
        # Agregar observaciones con timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        nueva_observacion = f"[{timestamp}] Observado por usuario {usuario_id}:\n{observaciones}"
        
        if habilitacion.observaciones:
            habilitacion.observaciones += f"\n\n{nueva_observacion}"
        else:
            habilitacion.observaciones = nueva_observacion
        
        await self.db.commit()
        await self.db.refresh(habilitacion, ['pago'])
        
        # Actualizar estado del conductor
        conductor = await self.conductor_repo.get_by_id(habilitacion.conductor_id)
        conductor.estado = EstadoConductor.OBSERVADO
        await self.db.commit()
        
        return habilitacion
    
    async def habilitar_conductor(
        self,
        habilitacion_id: UUID,
        usuario_id: UUID,
        vigencia_hasta: date,
        observaciones: Optional[str] = None
    ) -> Habilitacion:
        """
        Habilitar conductor con verificación de pago
        
        Args:
            habilitacion_id: ID de la habilitación
            usuario_id: ID del usuario que habilita
            vigencia_hasta: Fecha de vencimiento de la habilitación
            observaciones: Observaciones adicionales
            
        Returns:
            Habilitación otorgada
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si no se puede habilitar
        """
        # Cargar habilitación con pago eager
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        # Verificar estado
        if habilitacion.estado != EstadoHabilitacion.APROBADO:
            raise ValidacionError(
                "estado",
                f"Solo se pueden habilitar solicitudes APROBADAS. Estado actual: {habilitacion.estado.value}"
            )
        
        # Verificar pago
        if not habilitacion.pago or habilitacion.pago.estado != EstadoPago.CONFIRMADO:
            raise ValidacionError(
                "pago",
                "No se puede habilitar sin pago confirmado"
            )
        
        # Validar fecha de vigencia
        if vigencia_hasta <= date.today():
            raise ValidacionError(
                "vigencia_hasta",
                "La fecha de vigencia debe ser futura"
            )
        
        # Actualizar estado
        habilitacion.estado = EstadoHabilitacion.HABILITADO
        habilitacion.habilitado_por = usuario_id
        habilitacion.fecha_habilitacion = datetime.utcnow()
        habilitacion.vigencia_hasta = vigencia_hasta
        
        if observaciones:
            if habilitacion.observaciones:
                habilitacion.observaciones += f"\n\nHabilitación: {observaciones}"
            else:
                habilitacion.observaciones = f"Habilitación: {observaciones}"
        
        await self.db.commit()
        await self.db.refresh(habilitacion, ['pago'])
        
        # Actualizar estado del conductor
        conductor = await self.conductor_repo.get_by_id(habilitacion.conductor_id)
        conductor.estado = EstadoConductor.HABILITADO
        await self.db.commit()
        
        return habilitacion
    
    async def suspender_habilitacion(
        self,
        habilitacion_id: UUID,
        motivo: str,
        usuario_id: UUID
    ) -> Habilitacion:
        """
        Suspender habilitación con justificación
        
        Args:
            habilitacion_id: ID de la habilitación
            motivo: Justificación de la suspensión
            usuario_id: ID del usuario que suspende
            
        Returns:
            Habilitación suspendida
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si la habilitación no está habilitada
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        if habilitacion.estado != EstadoHabilitacion.HABILITADO:
            raise ValidacionError(
                "estado",
                f"Solo se pueden suspender habilitaciones HABILITADAS. Estado actual: {habilitacion.estado.value}"
            )
        
        # Registrar suspensión
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        suspension_info = f"[{timestamp}] SUSPENDIDO por usuario {usuario_id}:\nMotivo: {motivo}"
        
        if habilitacion.observaciones:
            habilitacion.observaciones += f"\n\n{suspension_info}"
        else:
            habilitacion.observaciones = suspension_info
        
        await self.db.commit()
        await self.db.refresh(habilitacion, ['pago'])
        
        # Actualizar estado del conductor
        conductor = await self.conductor_repo.get_by_id(habilitacion.conductor_id)
        conductor.estado = EstadoConductor.SUSPENDIDO
        await self.db.commit()
        
        return habilitacion
    
    async def revocar_habilitacion(
        self,
        habilitacion_id: UUID,
        motivo: str,
        usuario_id: UUID
    ) -> Habilitacion:
        """
        Revocar habilitación
        
        Args:
            habilitacion_id: ID de la habilitación
            motivo: Justificación de la revocación
            usuario_id: ID del usuario que revoca
            
        Returns:
            Habilitación revocada
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si la habilitación no puede ser revocada
        """
        habilitacion = await self.habilitacion_repo.get_by_id(habilitacion_id)
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        if habilitacion.estado not in [
            EstadoHabilitacion.HABILITADO,
            EstadoHabilitacion.APROBADO
        ]:
            raise ValidacionError(
                "estado",
                f"Solo se pueden revocar habilitaciones HABILITADAS o APROBADAS. Estado actual: {habilitacion.estado.value}"
            )
        
        # Actualizar estado
        habilitacion.estado = EstadoHabilitacion.RECHAZADO
        
        # Registrar revocación
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        revocacion_info = f"[{timestamp}] REVOCADO por usuario {usuario_id}:\nMotivo: {motivo}"
        
        if habilitacion.observaciones:
            habilitacion.observaciones += f"\n\n{revocacion_info}"
        else:
            habilitacion.observaciones = revocacion_info
        
        await self.db.commit()
        await self.db.refresh(habilitacion)
        
        # Actualizar estado del conductor
        conductor = await self.conductor_repo.get_by_id(habilitacion.conductor_id)
        conductor.estado = EstadoConductor.REVOCADO
        await self.db.commit()
        
        return habilitacion
    
    async def obtener_habilitacion(self, habilitacion_id: UUID) -> Habilitacion:
        """
        Obtener habilitación por ID
        
        Args:
            habilitacion_id: ID de la habilitación
            
        Returns:
            Habilitación
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Habilitacion)
            .options(selectinload(Habilitacion.pago))
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        return habilitacion
    
    async def obtener_habilitaciones(
        self,
        estado: Optional[EstadoHabilitacion] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Habilitacion]:
        """
        Obtener habilitaciones con filtros
        
        Args:
            estado: Estado de la habilitación (opcional)
            skip: Número de registros a saltar
            limit: Número máximo de registros
            
        Returns:
            Lista de habilitaciones
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Build query with eager loading
        query = select(Habilitacion).options(selectinload(Habilitacion.pago))
        
        if estado:
            query = query.where(Habilitacion.estado == estado)
        
        query = query.order_by(Habilitacion.fecha_solicitud.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def verificar_vigencia(self, conductor_id: UUID) -> bool:
        """
        Verificar si un conductor tiene habilitación vigente
        
        Args:
            conductor_id: ID del conductor
            
        Returns:
            True si tiene habilitación vigente, False si no
        """
        ultima_habilitacion = await self.habilitacion_repo.get_ultima_habilitacion_conductor(
            conductor_id
        )
        
        if not ultima_habilitacion:
            return False
        
        return ultima_habilitacion.esta_vigente
    
    async def generar_certificado(self, habilitacion_id: UUID) -> bytes:
        """
        Generar certificado de habilitación en PDF
        
        Args:
            habilitacion_id: ID de la habilitación
            
        Returns:
            Bytes del PDF generado
            
        Raises:
            RecursoNoEncontrado: Si la habilitación no existe
            ValidacionError: Si la habilitación no está habilitada
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.utils.pdf_generator import CertificadoHabilitacionPDF
        
        # Cargar habilitación con relaciones
        result = await self.db.execute(
            select(Habilitacion)
            .options(
                selectinload(Habilitacion.conductor).selectinload(Conductor.empresa),
                selectinload(Habilitacion.habilitador)
            )
            .where(Habilitacion.id == habilitacion_id)
        )
        habilitacion = result.scalar_one_or_none()
        
        if not habilitacion:
            raise RecursoNoEncontrado("Habilitacion", str(habilitacion_id))
        
        if habilitacion.estado != EstadoHabilitacion.HABILITADO:
            raise ValidacionError(
                "estado",
                f"Solo se pueden generar certificados para habilitaciones HABILITADAS. Estado actual: {habilitacion.estado.value}"
            )
        
        # Obtener datos del conductor y empresa
        conductor = habilitacion.conductor
        empresa = conductor.empresa
        
        # Obtener nombre del funcionario que habilitó
        habilitado_por_nombre = "DRTC Puno"
        if habilitacion.habilitador:
            habilitado_por_nombre = f"{habilitacion.habilitador.nombres} {habilitacion.habilitador.apellidos}"
        
        # Generar PDF
        generador = CertificadoHabilitacionPDF()
        pdf_bytes = generador.generar(
            codigo_habilitacion=habilitacion.codigo_habilitacion,
            conductor_nombre=conductor.nombres,
            conductor_apellidos=conductor.apellidos,
            conductor_dni=conductor.dni,
            licencia_numero=conductor.licencia_numero,
            licencia_categoria=conductor.licencia_categoria,
            empresa_razon_social=empresa.razon_social,
            empresa_ruc=empresa.ruc,
            fecha_habilitacion=habilitacion.fecha_habilitacion,
            vigencia_hasta=habilitacion.vigencia_hasta,
            habilitado_por=habilitado_por_nombre
        )
        
        return pdf_bytes
    
    # Métodos privados
    
    async def _generar_codigo_unico(self) -> str:
        """
        Generar código único de habilitación
        
        Returns:
            Código único
        """
        import uuid
        
        while True:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_id = str(uuid.uuid4())[:8].upper()
            codigo = f"HAB-{timestamp}-{unique_id}"
            
            # Verificar que no exista
            if not await self.habilitacion_repo.codigo_exists(codigo):
                return codigo
    
    async def _validar_documentos_conductor(self, conductor: Conductor) -> None:
        """
        Validar que el conductor tenga todos los documentos necesarios
        
        Args:
            conductor: Conductor a validar
            
        Raises:
            ValidacionError: Si faltan documentos
        """
        # Validar licencia vigente
        if conductor.licencia_vencimiento < date.today():
            raise ValidacionError(
                "licencia_vencimiento",
                "La licencia de conducir está vencida"
            )
        
        # Aquí se pueden agregar más validaciones de documentos
        # Por ejemplo, verificar que tenga documentos adjuntos
        # if not conductor.documentos:
        #     raise ValidacionError("documentos", "El conductor no tiene documentos adjuntos")
