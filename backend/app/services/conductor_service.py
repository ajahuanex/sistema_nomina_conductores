"""
Servicio para gestión de conductores
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa
from app.repositories.conductor_repository import ConductorRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.conductor import (
    ConductorCreate,
    ConductorUpdate,
    ConductorResponse,
    ConductorBusqueda
)
from app.core.exceptions import (
    RecursoNoEncontrado,
    ValidacionError,
    ConflictoError
)


class ConductorService:
    """Servicio para gestión de conductores"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conductor_repo = ConductorRepository(db)
        self.empresa_repo = EmpresaRepository(db)
    
    async def registrar_conductor(
        self,
        conductor_data: ConductorCreate,
        usuario_id: UUID
    ) -> Conductor:
        """
        Registra un nuevo conductor con validaciones completas
        
        Args:
            conductor_data: Datos del conductor
            usuario_id: ID del usuario que registra
            
        Returns:
            Conductor creado
            
        Raises:
            RecursoNoEncontrado: Si la empresa no existe
            ValidacionError: Si hay errores de validación
            ConflictoError: Si DNI o licencia ya existen
        """
        # Verificar que la empresa existe
        empresa = await self.empresa_repo.get_by_id(conductor_data.empresa_id)
        if not empresa:
            raise RecursoNoEncontrado("Empresa", str(conductor_data.empresa_id))
        
        if not empresa.activo:
            raise ValidacionError(
                "empresa",
                "La empresa no está activa"
            )
        
        # Verificar que DNI no existe
        if await self.conductor_repo.dni_exists(conductor_data.dni):
            raise ConflictoError(
                f"Ya existe un conductor con DNI {conductor_data.dni}"
            )
        
        # Verificar que licencia no existe
        if await self.conductor_repo.licencia_exists(conductor_data.licencia_numero):
            raise ConflictoError(
                f"Ya existe un conductor con licencia {conductor_data.licencia_numero}"
            )
        
        # Validar categoría de licencia según autorizaciones de la empresa
        if not await self.validar_categoria_licencia(
            conductor_data.licencia_categoria,
            conductor_data.empresa_id
        ):
            raise ValidacionError(
                "licencia_categoria",
                f"La categoría de licencia {conductor_data.licencia_categoria} no es válida "
                f"para los tipos de autorización de la empresa"
            )
        
        # Crear conductor
        conductor_dict = conductor_data.model_dump()
        conductor_dict['estado'] = EstadoConductor.PENDIENTE
        
        conductor = await self.conductor_repo.create(conductor_dict)
        
        # TODO: Crear habilitación automáticamente (tarea 8)
        # await self.habilitacion_service.crear_solicitud(conductor.id)
        
        return conductor
    
    async def validar_categoria_licencia(
        self,
        licencia_categoria: str,
        empresa_id: UUID
    ) -> bool:
        """
        Valida si la categoría de licencia es apropiada para los tipos de
        autorización de la empresa
        
        Args:
            licencia_categoria: Categoría de licencia del conductor
            empresa_id: ID de la empresa
            
        Returns:
            True si la categoría es válida para al menos una autorización
            
        Raises:
            RecursoNoEncontrado: Si la empresa no existe
        """
        empresa = await self.empresa_repo.get_by_id(empresa_id)
        if not empresa:
            raise RecursoNoEncontrado("Empresa", str(empresa_id))
        
        # Si la empresa no tiene autorizaciones, no se puede validar
        if not empresa.autorizaciones:
            raise ValidacionError(
                "empresa",
                "La empresa no tiene autorizaciones registradas"
            )
        
        # Mapeo de tipos de autorización a categorías mínimas requeridas
        requisitos = {
            'MERCANCIAS': ['A-IIIb', 'A-IIIc'],
            'TURISMO': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'TRABAJADORES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESPECIALES': ['A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESTUDIANTES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'RESIDUOS_PELIGROSOS': ['A-IIIb', 'A-IIIc'],
        }
        
        # Verificar si la categoría es válida para al menos una autorización vigente
        for autorizacion in empresa.autorizaciones:
            if not autorizacion.vigente:
                continue
            
            tipo_codigo = autorizacion.tipo_autorizacion.codigo
            categorias_requeridas = requisitos.get(tipo_codigo, [])
            
            if licencia_categoria in categorias_requeridas:
                return True
        
        return False
    
    async def obtener_requisitos_categoria(
        self,
        tipo_autorizacion_codigo: str
    ) -> List[str]:
        """
        Obtiene las categorías de licencia requeridas para un tipo de autorización
        
        Args:
            tipo_autorizacion_codigo: Código del tipo de autorización
            
        Returns:
            Lista de categorías válidas
        """
        requisitos = {
            'MERCANCIAS': ['A-IIIb', 'A-IIIc'],
            'TURISMO': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'TRABAJADORES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESPECIALES': ['A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESTUDIANTES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'RESIDUOS_PELIGROSOS': ['A-IIIb', 'A-IIIc'],
        }
        
        return requisitos.get(tipo_autorizacion_codigo, [])
    
    async def actualizar_conductor(
        self,
        conductor_id: UUID,
        conductor_data: ConductorUpdate,
        usuario_id: UUID
    ) -> Conductor:
        """
        Actualiza los datos de un conductor
        
        Args:
            conductor_id: ID del conductor
            conductor_data: Datos a actualizar
            usuario_id: ID del usuario que actualiza
            
        Returns:
            Conductor actualizado
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
            ConflictoError: Si licencia ya existe
        """
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        # Si se actualiza la licencia, verificar que no exista
        if conductor_data.licencia_numero:
            if conductor_data.licencia_numero != conductor.licencia_numero:
                if await self.conductor_repo.licencia_exists(conductor_data.licencia_numero):
                    raise ConflictoError(
                        f"Ya existe un conductor con licencia {conductor_data.licencia_numero}"
                    )
        
        # Si se actualiza la categoría, validar
        if conductor_data.licencia_categoria:
            if conductor_data.licencia_categoria != conductor.licencia_categoria:
                if not await self.validar_categoria_licencia(
                    conductor_data.licencia_categoria,
                    conductor.empresa_id
                ):
                    raise ValidacionError(
                        "licencia_categoria",
                        f"La categoría de licencia {conductor_data.licencia_categoria} no es válida "
                        f"para los tipos de autorización de la empresa"
                    )
        
        # Actualizar campos
        update_data = conductor_data.model_dump(exclude_unset=True)
        
        conductor = await self.conductor_repo.update(conductor.id, update_data)
        
        return conductor
    
    async def cambiar_estado_conductor(
        self,
        conductor_id: UUID,
        nuevo_estado: EstadoConductor,
        observacion: Optional[str] = None,
        usuario_id: Optional[UUID] = None
    ) -> Conductor:
        """
        Cambia el estado de un conductor
        
        Args:
            conductor_id: ID del conductor
            nuevo_estado: Nuevo estado
            observacion: Observación sobre el cambio
            usuario_id: ID del usuario que realiza el cambio
            
        Returns:
            Conductor actualizado
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
            ValidacionError: Si el cambio de estado no es válido
        """
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        # Validar transiciones de estado
        estado_actual = conductor.estado
        
        # Reglas de transición de estados
        transiciones_validas = {
            EstadoConductor.PENDIENTE: [
                EstadoConductor.HABILITADO,
                EstadoConductor.OBSERVADO,
                EstadoConductor.REVOCADO
            ],
            EstadoConductor.OBSERVADO: [
                EstadoConductor.PENDIENTE,
                EstadoConductor.HABILITADO,
                EstadoConductor.REVOCADO
            ],
            EstadoConductor.HABILITADO: [
                EstadoConductor.SUSPENDIDO,
                EstadoConductor.REVOCADO,
                EstadoConductor.OBSERVADO
            ],
            EstadoConductor.SUSPENDIDO: [
                EstadoConductor.HABILITADO,
                EstadoConductor.REVOCADO
            ],
            EstadoConductor.REVOCADO: []  # Estado final
        }
        
        if nuevo_estado not in transiciones_validas.get(estado_actual, []):
            raise ValidacionError(
                "estado",
                f"No se puede cambiar de estado {estado_actual.value} a {nuevo_estado.value}"
            )
        
        # Cambiar estado
        conductor.cambiar_estado(nuevo_estado, observacion)
        
        # Actualizar en base de datos
        update_data = {
            "estado": nuevo_estado,
            "observaciones": conductor.observaciones
        }
        conductor = await self.conductor_repo.update(conductor.id, update_data)
        
        # TODO: Registrar en auditoría (tarea 15)
        # TODO: Enviar notificación (tarea 16)
        
        return conductor
    
    async def buscar_conductores(
        self,
        busqueda: ConductorBusqueda
    ) -> Dict[str, Any]:
        """
        Busca conductores con filtros múltiples
        
        Args:
            busqueda: Parámetros de búsqueda
            
        Returns:
            Diccionario con resultados y metadatos de paginación
        """
        # Construir texto de búsqueda
        texto_busqueda = None
        if busqueda.dni:
            texto_busqueda = busqueda.dni
        elif busqueda.nombres or busqueda.apellidos:
            partes = []
            if busqueda.nombres:
                partes.append(busqueda.nombres)
            if busqueda.apellidos:
                partes.append(busqueda.apellidos)
            texto_busqueda = " ".join(partes)
        
        # Convertir estado string a enum si existe
        estado_enum = None
        if busqueda.estado:
            try:
                estado_enum = EstadoConductor(busqueda.estado)
            except ValueError:
                raise ValidacionError("estado", f"Estado inválido: {busqueda.estado}")
        
        # Buscar conductores
        skip = (busqueda.page - 1) * busqueda.page_size
        conductores = await self.conductor_repo.buscar_conductores(
            texto_busqueda=texto_busqueda,
            empresa_id=busqueda.empresa_id,
            estado=estado_enum,
            licencia_categoria=busqueda.licencia_categoria,
            skip=skip,
            limit=busqueda.page_size
        )
        
        # Filtros adicionales para documentos por vencer
        if busqueda.licencia_proxima_vencer:
            conductores_filtrados = []
            for conductor in conductores:
                alertas = conductor.requiere_renovacion_documentos(dias_anticipacion=30)
                if alertas['licencia']:
                    conductores_filtrados.append(conductor)
            conductores = conductores_filtrados
        
        if busqueda.certificado_proximo_vencer:
            conductores_filtrados = []
            for conductor in conductores:
                alertas = conductor.requiere_renovacion_documentos(dias_anticipacion=30)
                if alertas['certificado_medico']:
                    conductores_filtrados.append(conductor)
            conductores = conductores_filtrados
        
        # Contar total (aproximado)
        total = len(conductores)
        if not busqueda.licencia_proxima_vencer and not busqueda.certificado_proximo_vencer:
            # Si no hay filtros especiales, contar del repositorio
            filters = {}
            if busqueda.empresa_id:
                filters["empresa_id"] = busqueda.empresa_id
            if estado_enum:
                filters["estado"] = estado_enum.value
            if busqueda.licencia_categoria:
                filters["licencia_categoria"] = busqueda.licencia_categoria
            
            total = await self.conductor_repo.count(filters=filters)
        
        total_pages = (total + busqueda.page_size - 1) // busqueda.page_size
        
        return {
            "items": conductores,
            "total": total,
            "page": busqueda.page,
            "page_size": busqueda.page_size,
            "total_pages": total_pages
        }
    
    async def obtener_conductor_por_id(
        self,
        conductor_id: UUID
    ) -> Conductor:
        """
        Obtiene un conductor por ID
        
        Args:
            conductor_id: ID del conductor
            
        Returns:
            Conductor
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
        """
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        return conductor
    
    async def obtener_conductor_por_dni(
        self,
        dni: str
    ) -> Conductor:
        """
        Obtiene un conductor por DNI
        
        Args:
            dni: DNI del conductor
            
        Returns:
            Conductor
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
        """
        conductor = await self.conductor_repo.get_by_dni(dni)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", dni)
        
        return conductor
    
    async def eliminar_conductor(
        self,
        conductor_id: UUID,
        usuario_id: UUID
    ) -> None:
        """
        Elimina un conductor (soft delete)
        
        Args:
            conductor_id: ID del conductor
            usuario_id: ID del usuario que elimina
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
            ValidacionError: Si el conductor está habilitado
        """
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        # No permitir eliminar conductores habilitados
        if conductor.estado == EstadoConductor.HABILITADO:
            raise ValidacionError(
                "estado",
                "No se puede eliminar un conductor habilitado. Primero debe suspenderlo o revocarlo."
            )
        
        # Soft delete
        await self.conductor_repo.delete(conductor_id)
        
        # TODO: Registrar en auditoría (tarea 15)
    
    async def obtener_conductores_por_empresa(
        self,
        empresa_id: UUID,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conductor]:
        """
        Obtiene conductores de una empresa
        
        Args:
            empresa_id: ID de la empresa
            estado: Estado del conductor (opcional)
            skip: Registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de conductores
        """
        estado_enum = None
        if estado:
            try:
                estado_enum = EstadoConductor(estado)
            except ValueError:
                raise ValidacionError("estado", f"Estado inválido: {estado}")
        
        return await self.conductor_repo.get_by_empresa(
            empresa_id=empresa_id,
            estado=estado_enum,
            skip=skip,
            limit=limit
        )
    
    async def obtener_conductores_con_documentos_por_vencer(
        self,
        dias_anticipacion: int = 30
    ) -> Dict[str, List[Conductor]]:
        """
        Obtiene conductores con documentos próximos a vencer
        
        Args:
            dias_anticipacion: Días de anticipación
            
        Returns:
            Diccionario con listas de conductores por tipo de documento
        """
        licencias = await self.conductor_repo.get_conductores_con_licencia_por_vencer(
            dias_anticipacion=dias_anticipacion
        )
        
        certificados = await self.conductor_repo.get_conductores_con_certificado_por_vencer(
            dias_anticipacion=dias_anticipacion
        )
        
        return {
            "licencias_por_vencer": licencias,
            "certificados_por_vencer": certificados
        }


    async def cambiar_estado_conductor(
        self,
        conductor_id: UUID,
        nuevo_estado: str,
        motivo: str,
        observaciones: Optional[str],
        usuario_id: UUID
    ) -> Conductor:
        """
        Cambia el estado de un conductor con validaciones
        
        Args:
            conductor_id: ID del conductor
            nuevo_estado: Nuevo estado
            motivo: Motivo del cambio
            observaciones: Observaciones adicionales
            usuario_id: ID del usuario que realiza el cambio
            
        Returns:
            Conductor actualizado
            
        Raises:
            RecursoNoEncontrado: Si el conductor no existe
            ValidacionError: Si la transición no es válida
        """
        from app.models.conductor import EstadoConductor
        
        # Obtener conductor
        conductor = await self.conductor_repo.get_by_id(conductor_id)
        if not conductor:
            raise RecursoNoEncontrado("Conductor", str(conductor_id))
        
        estado_actual = conductor.estado
        
        # Mapear string a enum
        estado_map = {
            'pendiente': EstadoConductor.PENDIENTE,
            'habilitado': EstadoConductor.HABILITADO,
            'observado': EstadoConductor.OBSERVADO,
            'suspendido': EstadoConductor.SUSPENDIDO,
            'revocado': EstadoConductor.REVOCADO
        }
        
        nuevo_estado_enum = estado_map.get(nuevo_estado.lower())
        if not nuevo_estado_enum:
            raise ValidacionError("estado", f"Estado inválido: {nuevo_estado}")
        
        # Validar transiciones permitidas
        transiciones_validas = {
            EstadoConductor.PENDIENTE: [EstadoConductor.HABILITADO, EstadoConductor.OBSERVADO],
            EstadoConductor.OBSERVADO: [EstadoConductor.PENDIENTE, EstadoConductor.HABILITADO],
            EstadoConductor.HABILITADO: [EstadoConductor.SUSPENDIDO, EstadoConductor.REVOCADO],
            EstadoConductor.SUSPENDIDO: [EstadoConductor.HABILITADO],
            EstadoConductor.REVOCADO: []  # No se puede cambiar desde revocado
        }
        
        if nuevo_estado_enum not in transiciones_validas.get(estado_actual, []):
            raise ValidacionError(
                "estado",
                f"No se puede cambiar de {estado_actual.value} a {nuevo_estado_enum.value}"
            )
        
        # Actualizar estado
        conductor.estado = nuevo_estado_enum
        
        # Agregar observaciones
        obs_text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Cambio de estado: {estado_actual.value} → {nuevo_estado_enum.value}. Motivo: {motivo}"
        if observaciones:
            obs_text += f". Observaciones: {observaciones}"
        
        if conductor.observaciones:
            conductor.observaciones += f"\n{obs_text}"
        else:
            conductor.observaciones = obs_text
        
        await self.db.commit()
        await self.db.refresh(conductor)
        
        # TODO: Registrar en auditoría
        # TODO: Enviar notificación
        
        return conductor
