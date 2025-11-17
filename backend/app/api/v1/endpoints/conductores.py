"""
Endpoints para gestión de conductores
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import require_roles
from app.core.exceptions import RecursoNoEncontrado, ValidacionError, ConflictoError
from app.models.user import Usuario, RolUsuario
from app.models.documento_conductor import TipoDocumento
from app.services.conductor_service import ConductorService
from app.services.documento_service import DocumentoService
from app.repositories.empresa_repository import EmpresaRepository
from app.schemas.conductor import (
    ConductorCreate,
    ConductorUpdate,
    ConductorResponse,
    ConductorListResponse,
    ConductorEstadoUpdate,
    ConductorBusqueda,
    ConductorValidacionCategoria,
    ConductorValidacionCategoriaResponse,
    ConductorCambioEstado
)
from app.schemas.documento import (
    DocumentoConductorResponse,
    DocumentoConductorListResponse,
    DocumentoUploadResponse
)

router = APIRouter(prefix="/conductores", tags=["conductores"])


async def get_empresa_gerente(current_user: Usuario, db: AsyncSession) -> UUID:
    """Helper para obtener la empresa de un gerente"""
    if current_user.rol != RolUsuario.GERENTE:
        return None
    
    from app.models.empresa import Empresa
    from sqlalchemy import select
    
    # Buscar empresa del gerente
    query = select(Empresa).where(Empresa.gerente_id == current_user.id)
    result = await db.execute(query)
    empresa = result.scalar_one_or_none()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gerente no tiene empresa asignada"
        )
    
    return empresa.id


@router.get("", response_model=ConductorListResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def listar_conductores(
    dni: str = Query(None, description="Filtrar por DNI"),
    nombres: str = Query(None, description="Filtrar por nombres"),
    apellidos: str = Query(None, description="Filtrar por apellidos"),
    empresa_id: UUID = Query(None, description="Filtrar por empresa"),
    estado: str = Query(None, description="Filtrar por estado"),
    licencia_categoria: str = Query(None, description="Filtrar por categoría de licencia"),
    licencia_proxima_vencer: bool = Query(None, description="Filtrar licencias próximas a vencer"),
    certificado_proximo_vencer: bool = Query(None, description="Filtrar certificados próximos a vencer"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamaño de página"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar conductores con paginación y filtros
    
    - Gerentes solo pueden ver conductores de su empresa
    - Filtro automático aplicado para gerentes
    - Otros roles pueden ver todos los conductores
    """
    service = ConductorService(db)
    
    # Si es gerente, filtrar por su empresa
    if current_user.rol == RolUsuario.GERENTE:
        empresa_id = await get_empresa_gerente(current_user, db)
    
    busqueda = ConductorBusqueda(
        dni=dni,
        nombres=nombres,
        apellidos=apellidos,
        empresa_id=empresa_id,
        estado=estado,
        licencia_categoria=licencia_categoria,
        licencia_proxima_vencer=licencia_proxima_vencer,
        certificado_proximo_vencer=certificado_proximo_vencer,
        page=page,
        page_size=page_size
    )
    
    try:
        resultado = await service.buscar_conductores(busqueda)
        return resultado
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.post("", response_model=ConductorResponse, status_code=status.HTTP_201_CREATED)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def crear_conductor(
    conductor_data: ConductorCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo conductor
    
    - Gerentes solo pueden crear conductores para su propia empresa
    - Otros roles pueden crear conductores para cualquier empresa
    """
    service = ConductorService(db)
    
    # Si es gerente, verificar que solo cree conductores para su empresa
    if current_user.rol == RolUsuario.GERENTE:
        empresa_gerente_id = await get_empresa_gerente(current_user, db)
        
        if conductor_data.empresa_id != empresa_gerente_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puede crear conductores para su propia empresa"
            )
    
    try:
        conductor = await service.registrar_conductor(
            conductor_data=conductor_data,
            usuario_id=current_user.id
        )
        return conductor
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ConflictoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


@router.get("/{conductor_id}", response_model=ConductorResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def obtener_conductor(
    conductor_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un conductor por ID
    
    - Gerentes solo pueden ver conductores de su empresa
    """
    service = ConductorService(db)
    
    try:
        conductor = await service.obtener_conductor_por_id(conductor_id)
        
        # Si es gerente, verificar que el conductor sea de su empresa
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para ver este conductor"
                )
        
        return conductor
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.put("/{conductor_id}", response_model=ConductorResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def actualizar_conductor(
    conductor_id: UUID,
    conductor_data: ConductorUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un conductor
    
    - Gerentes solo pueden actualizar conductores de su empresa
    """
    service = ConductorService(db)
    
    try:
        # Verificar que el conductor existe y pertenece a la empresa del gerente
        conductor = await service.obtener_conductor_por_id(conductor_id)
        
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para actualizar este conductor"
                )
        
        conductor_actualizado = await service.actualizar_conductor(
            conductor_id=conductor_id,
            conductor_data=conductor_data,
            usuario_id=current_user.id
        )
        return conductor_actualizado
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ConflictoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


@router.delete("/{conductor_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR)
async def eliminar_conductor(
    conductor_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un conductor (soft delete)
    
    - Solo Superusuarios y Directores pueden eliminar conductores
    """
    service = ConductorService(db)
    
    try:
        await service.eliminar_conductor(
            conductor_id=conductor_id,
            usuario_id=current_user.id
        )
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


@router.get("/dni/{dni}", response_model=ConductorResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def obtener_conductor_por_dni(
    dni: str,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un conductor por DNI
    
    - Gerentes solo pueden ver conductores de su empresa
    """
    service = ConductorService(db)
    
    try:
        conductor = await service.obtener_conductor_por_dni(dni)
        
        # Si es gerente, verificar que el conductor sea de su empresa
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para ver este conductor"
                )
        
        return conductor
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.put("/{conductor_id}/estado", response_model=ConductorResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def cambiar_estado_conductor(
    conductor_id: UUID,
    estado_data: ConductorEstadoUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cambiar el estado de un conductor
    
    - Solo Superusuarios, Directores y Subdirectores pueden cambiar estados
    """
    service = ConductorService(db)
    
    try:
        from app.models.conductor import EstadoConductor
        nuevo_estado = EstadoConductor(estado_data.estado)
        
        conductor = await service.cambiar_estado_conductor(
            conductor_id=conductor_id,
            nuevo_estado=nuevo_estado,
            observacion=estado_data.observacion,
            usuario_id=current_user.id
        )
        return conductor
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado inválido: {str(e)}"
        )


@router.post("/validar-categoria", response_model=ConductorValidacionCategoriaResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def validar_categoria_licencia(
    validacion_data: ConductorValidacionCategoria,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validar si una categoría de licencia es válida para un tipo de autorización
    """
    service = ConductorService(db)
    
    requisitos = await service.obtener_requisitos_categoria(
        validacion_data.tipo_autorizacion_codigo
    )
    
    valido = validacion_data.licencia_categoria in requisitos
    
    mensaje = (
        f"La categoría {validacion_data.licencia_categoria} es válida para {validacion_data.tipo_autorizacion_codigo}"
        if valido
        else f"La categoría {validacion_data.licencia_categoria} NO es válida para {validacion_data.tipo_autorizacion_codigo}"
    )
    
    return ConductorValidacionCategoriaResponse(
        valido=valido,
        mensaje=mensaje,
        categorias_requeridas=requisitos
    )



@router.post("/{conductor_id}/documentos", response_model=DocumentoUploadResponse, status_code=status.HTTP_201_CREATED)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def subir_documento_conductor(
    conductor_id: UUID,
    file: UploadFile = File(..., description="Archivo a subir (PDF, JPG, PNG, máximo 10MB)"),
    tipo_documento: TipoDocumento = Form(..., description="Tipo de documento"),
    descripcion: Optional[str] = Form(None, description="Descripción opcional del documento"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Subir un documento para un conductor
    
    - Tipos de archivo permitidos: PDF, JPG, PNG
    - Tamaño máximo: 10MB
    - Gerentes solo pueden subir documentos para conductores de su empresa
    """
    service = DocumentoService(db)
    conductor_service = ConductorService(db)
    
    try:
        # Verificar que el conductor existe
        conductor = await conductor_service.obtener_conductor_por_id(conductor_id)
        
        # Si es gerente, verificar que el conductor sea de su empresa
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para subir documentos a este conductor"
                )
        
        # Subir documento
        documento = await service.subir_documento(
            conductor_id=conductor_id,
            upload_file=file,
            tipo_documento=tipo_documento,
            descripcion=descripcion,
            usuario_id=current_user.id
        )
        
        return DocumentoUploadResponse(
            id=documento.id,
            mensaje="Documento subido exitosamente",
            nombre_archivo=documento.nombre_archivo,
            tamano_mb=documento.tamano_mb,
            tipo_documento=documento.tipo_documento
        )
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir documento: {str(e)}"
        )


@router.get("/{conductor_id}/documentos", response_model=DocumentoConductorListResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def listar_documentos_conductor(
    conductor_id: UUID,
    tipo_documento: Optional[TipoDocumento] = Query(None, description="Filtrar por tipo de documento"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los documentos de un conductor
    
    - Gerentes solo pueden ver documentos de conductores de su empresa
    """
    service = DocumentoService(db)
    conductor_service = ConductorService(db)
    
    try:
        # Verificar que el conductor existe
        conductor = await conductor_service.obtener_conductor_por_id(conductor_id)
        
        # Si es gerente, verificar que el conductor sea de su empresa
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para ver documentos de este conductor"
                )
        
        # Obtener documentos
        documentos = await service.obtener_documentos_conductor(
            conductor_id=conductor_id,
            tipo_documento=tipo_documento
        )
        
        return DocumentoConductorListResponse(
            documentos=documentos,
            total=len(documentos)
        )
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


@router.get("/{conductor_id}/documentos/{documento_id}", response_class=FileResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.OPERARIO, RolUsuario.GERENTE)
async def descargar_documento_conductor(
    conductor_id: UUID,
    documento_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Descargar un documento de un conductor
    
    - Gerentes solo pueden descargar documentos de conductores de su empresa
    """
    service = DocumentoService(db)
    conductor_service = ConductorService(db)
    
    try:
        # Verificar que el conductor existe
        conductor = await conductor_service.obtener_conductor_por_id(conductor_id)
        
        # Si es gerente, verificar que el conductor sea de su empresa
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para descargar documentos de este conductor"
                )
        
        # Obtener documento
        documento = await service.obtener_documento(documento_id)
        
        # Verificar que el documento pertenece al conductor
        if documento.conductor_id != conductor_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado para este conductor"
            )
        
        # Retornar archivo
        return FileResponse(
            path=documento.ruta_archivo,
            filename=documento.nombre_archivo,
            media_type=documento.tipo_mime
        )
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar documento: {str(e)}"
        )


@router.delete("/{conductor_id}/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR, RolUsuario.GERENTE)
async def eliminar_documento_conductor(
    conductor_id: UUID,
    documento_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un documento de un conductor
    
    - Gerentes solo pueden eliminar documentos de conductores de su empresa
    """
    service = DocumentoService(db)
    conductor_service = ConductorService(db)
    
    try:
        # Verificar que el conductor existe
        conductor = await conductor_service.obtener_conductor_por_id(conductor_id)
        
        # Si es gerente, verificar que el conductor sea de su empresa
        if current_user.rol == RolUsuario.GERENTE:
            empresa_gerente_id = await get_empresa_gerente(current_user, db)
            if conductor.empresa_id != empresa_gerente_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tiene permisos para eliminar documentos de este conductor"
                )
        
        # Obtener documento
        documento = await service.obtener_documento(documento_id)
        
        # Verificar que el documento pertenece al conductor
        if documento.conductor_id != conductor_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado para este conductor"
            )
        
        # Eliminar documento
        await service.eliminar_documento(documento_id)
        
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )



@router.post("/{conductor_id}/cambiar-estado", response_model=ConductorResponse)
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def cambiar_estado_conductor(
    conductor_id: UUID,
    cambio_estado: ConductorCambioEstado,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cambiar el estado de un conductor
    
    - Solo DIRECTOR y SUBDIRECTOR pueden cambiar estados
    - Se validan las transiciones permitidas
    - Se registra el motivo y observaciones
    
    Transiciones permitidas:
    - PENDIENTE → HABILITADO, OBSERVADO
    - OBSERVADO → PENDIENTE, HABILITADO
    - HABILITADO → SUSPENDIDO, REVOCADO
    - SUSPENDIDO → HABILITADO
    - REVOCADO → (ninguno, es irreversible)
    """
    service = ConductorService(db)
    
    try:
        conductor = await service.cambiar_estado_conductor(
            conductor_id=conductor_id,
            nuevo_estado=cambio_estado.nuevo_estado,
            motivo=cambio_estado.motivo,
            observaciones=cambio_estado.observaciones,
            usuario_id=current_user.id
        )
        return conductor
    except RecursoNoEncontrado as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except ValidacionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
