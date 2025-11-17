"""
Servicio de Empresa - Lógica de negocio para gestión de empresas
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.empresa import Empresa, AutorizacionEmpresa, TipoAutorizacion
from app.models.conductor import Conductor
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.empresa import (
    EmpresaCreate,
    EmpresaUpdate,
    AutorizacionEmpresaCreate
)
from app.core.exceptions import (
    RecursoNoEncontrado,
    ValidacionError,
    ConflictoError
)


class EmpresaService:
    """Servicio para gestión de empresas"""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio de empresa
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.repository = EmpresaRepository(db)
    
    async def registrar_empresa(
        self,
        empresa_data: EmpresaCreate
    ) -> Empresa:
        """
        Registra una nueva empresa con validaciones
        
        Args:
            empresa_data: Datos de la empresa a crear
            
        Returns:
            Empresa creada
            
        Raises:
            ValidacionError: Si el RUC ya existe o datos inválidos
        """
        # Verificar que el RUC no exista
        if await self.repository.ruc_exists(empresa_data.ruc):
            raise ValidacionError(
                campo="ruc",
                mensaje=f"El RUC {empresa_data.ruc} ya está registrado"
            )
        
        # Validar formato de RUC
        if not self._validar_ruc(empresa_data.ruc):
            raise ValidacionError(
                campo="ruc",
                mensaje="El RUC debe tener 11 dígitos numéricos"
            )
        
        # Validar gerente_id si se proporciona
        if empresa_data.gerente_id:
            # Convertir a UUID si es string
            try:
                gerente_uuid = UUID(empresa_data.gerente_id) if isinstance(empresa_data.gerente_id, str) else empresa_data.gerente_id
            except ValueError:
                raise ValidacionError(
                    campo="gerente_id",
                    mensaje="ID de gerente inválido"
                )
            
            # Verificar que el gerente no esté asignado a otra empresa
            empresa_existente = await self.repository.get_by_gerente(gerente_uuid)
            if empresa_existente:
                raise ValidacionError(
                    campo="gerente_id",
                    mensaje=f"El gerente ya está asignado a la empresa {empresa_existente.razon_social}"
                )
        
        # Preparar datos de la empresa
        empresa_dict = empresa_data.model_dump(exclude={'autorizaciones'})
        
        # Crear la empresa
        empresa = await self.repository.create(empresa_dict)
        
        # Agregar autorizaciones si se proporcionaron
        if empresa_data.autorizaciones:
            for autorizacion_data in empresa_data.autorizaciones:
                await self._crear_autorizacion(empresa.id, autorizacion_data)
            
            # Recargar empresa con autorizaciones usando eager loading
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            
            result = await self.db.execute(
                select(Empresa)
                .where(Empresa.id == empresa.id)
                .options(selectinload(Empresa.autorizaciones))
            )
            empresa = result.scalar_one()
        
        return empresa
    
    async def agregar_autorizacion(
        self,
        empresa_id: str,
        autorizacion_data: AutorizacionEmpresaCreate
    ) -> AutorizacionEmpresa:
        """
        Agrega una autorización a una empresa con validaciones
        
        Args:
            empresa_id: ID de la empresa
            autorizacion_data: Datos de la autorización
            
        Returns:
            Autorización creada
            
        Raises:
            RecursoNoEncontrado: Si la empresa o tipo de autorización no existe
            ValidacionError: Si los datos son inválidos
        """
        # Convertir string a UUID si es necesario
        if isinstance(empresa_id, str):
            try:
                empresa_id = UUID(empresa_id)
            except ValueError:
                raise ValidacionError(campo="empresa_id", mensaje="ID de empresa inválido")
        
        # Verificar que la empresa existe
        empresa = await self.repository.get_by_id(empresa_id)
        if not empresa:
            raise RecursoNoEncontrado(recurso="Empresa", id=str(empresa_id))
        
        # Crear la autorización
        return await self._crear_autorizacion(empresa_id, autorizacion_data)
    
    async def _crear_autorizacion(
        self,
        empresa_id: UUID,
        autorizacion_data: AutorizacionEmpresaCreate
    ) -> AutorizacionEmpresa:
        """
        Método interno para crear una autorización
        
        Args:
            empresa_id: ID de la empresa
            autorizacion_data: Datos de la autorización
            
        Returns:
            Autorización creada
            
        Raises:
            RecursoNoEncontrado: Si el tipo de autorización no existe
            ValidacionError: Si los datos son inválidos
        """
        # Convertir tipo_autorizacion_id a UUID
        try:
            tipo_autorizacion_id = UUID(autorizacion_data.tipo_autorizacion_id) if isinstance(
                autorizacion_data.tipo_autorizacion_id, str
            ) else autorizacion_data.tipo_autorizacion_id
        except ValueError:
            raise ValidacionError(
                campo="tipo_autorizacion_id",
                mensaje="ID de tipo de autorización inválido"
            )
        
        # Verificar que el tipo de autorización existe
        from sqlalchemy import select
        result = await self.db.execute(
            select(TipoAutorizacion).where(TipoAutorizacion.id == tipo_autorizacion_id)
        )
        tipo_autorizacion = result.scalar_one_or_none()
        
        if not tipo_autorizacion:
            raise RecursoNoEncontrado(
                recurso="TipoAutorizacion",
                id=str(tipo_autorizacion_id)
            )
        
        # Verificar que el número de resolución no exista
        result = await self.db.execute(
            select(AutorizacionEmpresa).where(
                AutorizacionEmpresa.numero_resolucion == autorizacion_data.numero_resolucion
            )
        )
        if result.scalar_one_or_none():
            raise ValidacionError(
                campo="numero_resolucion",
                mensaje=f"El número de resolución {autorizacion_data.numero_resolucion} ya existe"
            )
        
        # Validar fechas
        if autorizacion_data.fecha_vencimiento:
            if autorizacion_data.fecha_vencimiento <= autorizacion_data.fecha_emision:
                raise ValidacionError(
                    campo="fecha_vencimiento",
                    mensaje="La fecha de vencimiento debe ser posterior a la fecha de emisión"
                )
        
        # Crear la autorización
        autorizacion_dict = autorizacion_data.model_dump()
        autorizacion_dict['empresa_id'] = empresa_id
        autorizacion_dict['tipo_autorizacion_id'] = tipo_autorizacion_id
        
        autorizacion = AutorizacionEmpresa(**autorizacion_dict)
        self.db.add(autorizacion)
        await self.db.commit()
        await self.db.refresh(autorizacion)
        
        return autorizacion
    
    async def obtener_empresas(
        self,
        skip: int = 0,
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[Empresa]:
        """
        Obtiene empresas con paginación y filtros
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            filtros: Filtros opcionales (activo, ruc, razon_social, etc.)
            
        Returns:
            Lista de empresas
        """
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            filters=filtros
        )
    
    async def obtener_empresa(self, empresa_id: str) -> Empresa:
        """
        Obtiene una empresa por ID
        
        Args:
            empresa_id: ID de la empresa
            
        Returns:
            Empresa encontrada
            
        Raises:
            RecursoNoEncontrado: Si la empresa no existe
        """
        # Convertir string a UUID si es necesario
        if isinstance(empresa_id, str):
            try:
                empresa_id = UUID(empresa_id)
            except ValueError:
                raise ValidacionError(campo="empresa_id", mensaje="ID de empresa inválido")
        
        empresa = await self.repository.get_by_id(empresa_id)
        if not empresa:
            raise RecursoNoEncontrado(recurso="Empresa", id=str(empresa_id))
        
        return empresa
    
    async def obtener_empresa_por_ruc(self, ruc: str) -> Optional[Empresa]:
        """
        Obtiene una empresa por RUC
        
        Args:
            ruc: RUC de la empresa
            
        Returns:
            Empresa encontrada o None
        """
        return await self.repository.get_by_ruc(ruc)
    
    async def actualizar_empresa(
        self,
        empresa_id: str,
        empresa_data: EmpresaUpdate
    ) -> Empresa:
        """
        Actualiza una empresa existente
        
        Args:
            empresa_id: ID de la empresa a actualizar
            empresa_data: Datos a actualizar
            
        Returns:
            Empresa actualizada
            
        Raises:
            RecursoNoEncontrado: Si la empresa no existe
            ValidacionError: Si los datos son inválidos
        """
        # Convertir string a UUID si es necesario
        if isinstance(empresa_id, str):
            try:
                empresa_id = UUID(empresa_id)
            except ValueError:
                raise ValidacionError(campo="empresa_id", mensaje="ID de empresa inválido")
        
        # Verificar que la empresa existe
        empresa = await self.repository.get_by_id(empresa_id)
        if not empresa:
            raise RecursoNoEncontrado(recurso="Empresa", id=str(empresa_id))
        
        # Preparar datos para actualización
        update_data = empresa_data.model_dump(exclude_unset=True)
        
        # Validar gerente_id si se está actualizando
        if 'gerente_id' in update_data and update_data['gerente_id']:
            try:
                gerente_uuid = UUID(update_data['gerente_id']) if isinstance(
                    update_data['gerente_id'], str
                ) else update_data['gerente_id']
            except ValueError:
                raise ValidacionError(
                    campo="gerente_id",
                    mensaje="ID de gerente inválido"
                )
            
            # Verificar que el gerente no esté asignado a otra empresa
            empresa_existente = await self.repository.get_by_gerente(gerente_uuid)
            if empresa_existente and empresa_existente.id != empresa_id:
                raise ValidacionError(
                    campo="gerente_id",
                    mensaje=f"El gerente ya está asignado a la empresa {empresa_existente.razon_social}"
                )
        
        # Actualizar la empresa
        empresa_actualizada = await self.repository.update(empresa_id, update_data)
        
        return empresa_actualizada
    
    async def obtener_conductores_empresa(
        self,
        empresa_id: str,
        skip: int = 0,
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[Conductor]:
        """
        Obtiene los conductores de una empresa
        
        Args:
            empresa_id: ID de la empresa
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            filtros: Filtros opcionales (estado, etc.)
            
        Returns:
            Lista de conductores
            
        Raises:
            RecursoNoEncontrado: Si la empresa no existe
        """
        # Convertir string a UUID si es necesario
        if isinstance(empresa_id, str):
            try:
                empresa_id = UUID(empresa_id)
            except ValueError:
                raise ValidacionError(campo="empresa_id", mensaje="ID de empresa inválido")
        
        # Verificar que la empresa existe
        empresa = await self.repository.get_by_id(empresa_id)
        if not empresa:
            raise RecursoNoEncontrado(recurso="Empresa", id=str(empresa_id))
        
        # Obtener conductores
        from sqlalchemy import select
        
        query = select(Conductor).where(Conductor.empresa_id == empresa_id)
        
        # Aplicar filtros si se proporcionan
        if filtros:
            if 'estado' in filtros:
                query = query.where(Conductor.estado == filtros['estado'])
            if 'activo' in filtros:
                # Asumiendo que Conductor tiene un campo activo
                pass
        
        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        conductores = result.scalars().all()
        
        return list(conductores)
    
    async def contar_empresas(self, filtros: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el total de empresas
        
        Args:
            filtros: Filtros opcionales
            
        Returns:
            Número total de empresas
        """
        return await self.repository.count(filters=filtros)
    
    async def contar_conductores_empresa(
        self,
        empresa_id: str,
        filtros: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Cuenta el total de conductores de una empresa
        
        Args:
            empresa_id: ID de la empresa
            filtros: Filtros opcionales
            
        Returns:
            Número total de conductores
            
        Raises:
            RecursoNoEncontrado: Si la empresa no existe
        """
        # Convertir string a UUID si es necesario
        if isinstance(empresa_id, str):
            try:
                empresa_id = UUID(empresa_id)
            except ValueError:
                raise ValidacionError(campo="empresa_id", mensaje="ID de empresa inválido")
        
        # Verificar que la empresa existe
        empresa = await self.repository.get_by_id(empresa_id)
        if not empresa:
            raise RecursoNoEncontrado(recurso="Empresa", id=str(empresa_id))
        
        # Contar conductores
        from sqlalchemy import select, func
        
        query = select(func.count(Conductor.id)).where(Conductor.empresa_id == empresa_id)
        
        # Aplicar filtros si se proporcionan
        if filtros:
            if 'estado' in filtros:
                query = query.where(Conductor.estado == filtros['estado'])
        
        result = await self.db.execute(query)
        count = result.scalar()
        
        return count or 0
    
    def _validar_ruc(self, ruc: str) -> bool:
        """
        Valida que el RUC tenga 11 dígitos numéricos
        
        Args:
            ruc: RUC a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        return len(ruc) == 11 and ruc.isdigit()
