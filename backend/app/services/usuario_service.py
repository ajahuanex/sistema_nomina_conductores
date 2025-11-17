"""
Servicio de Usuario - Lógica de negocio para gestión de usuarios
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import Usuario, RolUsuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.user import UsuarioCreate, UsuarioUpdate, CambiarPasswordRequest
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    RecursoNoEncontrado,
    ValidacionError,
    PermisosDenegados
)


class UsuarioService:
    """Servicio para gestión de usuarios"""
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio de usuario
        
        Args:
            db: Sesión de base de datos
        """
        self.db = db
        self.repository = UsuarioRepository(db)
    
    async def crear_usuario(
        self, 
        usuario_data: UsuarioCreate,
        usuario_creador: Optional[Usuario] = None
    ) -> Usuario:
        """
        Crea un nuevo usuario con validaciones
        
        Args:
            usuario_data: Datos del usuario a crear
            usuario_creador: Usuario que está creando (para auditoría)
            
        Returns:
            Usuario creado
            
        Raises:
            ValidacionError: Si el email ya existe o datos inválidos
        """
        # Verificar que el email no exista
        if await self.repository.email_exists(usuario_data.email):
            raise ValidacionError(
                campo="email",
                mensaje=f"El email {usuario_data.email} ya está registrado"
            )
        
        # Validar empresa_id para Gerentes
        if usuario_data.rol == RolUsuario.GERENTE and not usuario_data.empresa_id:
            raise ValidacionError(
                campo="empresa_id",
                mensaje="Los Gerentes deben tener una empresa asignada"
            )

        
        # Validar que no Gerentes no tengan empresa_id
        if usuario_data.rol != RolUsuario.GERENTE and usuario_data.empresa_id:
            raise ValidacionError(
                campo="empresa_id",
                mensaje="Solo los Gerentes pueden tener empresa asignada"
            )
        
        # Hashear la contraseña
        password_hash = hash_password(usuario_data.password)
        
        # Crear el usuario
        usuario_dict = usuario_data.model_dump(exclude={'password'})
        usuario_dict['password_hash'] = password_hash
        
        usuario = await self.repository.create(usuario_dict)
        
        return usuario
    
    async def actualizar_usuario(
        self,
        usuario_id: str,
        usuario_data: UsuarioUpdate,
        usuario_actualizador: Optional[Usuario] = None
    ) -> Usuario:
        """
        Actualiza un usuario existente
        
        Args:
            usuario_id: ID del usuario a actualizar
            usuario_data: Datos a actualizar
            usuario_actualizador: Usuario que está actualizando (para auditoría)
            
        Returns:
            Usuario actualizado
            
        Raises:
            RecursoNoEncontrado: Si el usuario no existe
            ValidacionError: Si los datos son inválidos
        """
        # Convertir string a UUID si es necesario
        from uuid import UUID
        if isinstance(usuario_id, str):
            try:
                usuario_id = UUID(usuario_id)
            except ValueError:
                raise ValidacionError(campo="usuario_id", mensaje="ID de usuario inválido")
        
        # Verificar que el usuario existe
        usuario = await self.repository.get_by_id(usuario_id)
        if not usuario:
            raise RecursoNoEncontrado(recurso="Usuario", id=usuario_id)
        
        # Preparar datos para actualización
        update_data = usuario_data.model_dump(exclude_unset=True)
        
        # Si se está actualizando el email, verificar que no exista
        if 'email' in update_data and update_data['email'] != usuario.email:
            if await self.repository.email_exists(update_data['email']):
                raise ValidacionError(
                    campo="email",
                    mensaje=f"El email {update_data['email']} ya está registrado"
                )

        
        # Validar cambio de rol y empresa_id
        if 'rol' in update_data:
            nuevo_rol = update_data['rol']
            # Si cambia a Gerente, debe tener empresa_id
            if nuevo_rol == RolUsuario.GERENTE:
                empresa_id = update_data.get('empresa_id', usuario.empresa_id)
                if not empresa_id:
                    raise ValidacionError(
                        campo="empresa_id",
                        mensaje="Los Gerentes deben tener una empresa asignada"
                    )
            # Si cambia de Gerente a otro rol, limpiar empresa_id
            elif usuario.rol == RolUsuario.GERENTE and nuevo_rol != RolUsuario.GERENTE:
                update_data['empresa_id'] = None
        
        # Validar empresa_id
        if 'empresa_id' in update_data:
            rol_actual = update_data.get('rol', usuario.rol)
            if rol_actual != RolUsuario.GERENTE and update_data['empresa_id']:
                raise ValidacionError(
                    campo="empresa_id",
                    mensaje="Solo los Gerentes pueden tener empresa asignada"
                )
        
        # Actualizar el usuario
        usuario_actualizado = await self.repository.update(usuario_id, update_data)
        
        return usuario_actualizado
    
    async def cambiar_password(
        self,
        usuario_id: str,
        password_data: CambiarPasswordRequest
    ) -> Usuario:
        """
        Cambia la contraseña de un usuario
        
        Args:
            usuario_id: ID del usuario
            password_data: Datos de cambio de contraseña
            
        Returns:
            Usuario actualizado
            
        Raises:
            RecursoNoEncontrado: Si el usuario no existe
            ValidacionError: Si la contraseña actual es incorrecta
        """
        # Convertir string a UUID si es necesario
        from uuid import UUID
        if isinstance(usuario_id, str):
            try:
                usuario_id = UUID(usuario_id)
            except ValueError:
                raise ValidacionError(campo="usuario_id", mensaje="ID de usuario inválido")
        
        # Verificar que el usuario existe
        usuario = await self.repository.get_by_id(usuario_id)
        if not usuario:
            raise RecursoNoEncontrado(recurso="Usuario", id=usuario_id)
        
        # Verificar la contraseña actual
        if not verify_password(password_data.password_actual, usuario.password_hash):
            raise ValidacionError(
                campo="password_actual",
                mensaje="La contraseña actual es incorrecta"
            )

        
        # Hashear la nueva contraseña
        nuevo_password_hash = hash_password(password_data.password_nueva)
        
        # Actualizar la contraseña
        usuario_actualizado = await self.repository.update(
            usuario_id,
            {"password_hash": nuevo_password_hash}
        )
        
        return usuario_actualizado
    
    async def activar_usuario(self, usuario_id: str) -> Usuario:
        """
        Activa un usuario
        
        Args:
            usuario_id: ID del usuario a activar
            
        Returns:
            Usuario activado
            
        Raises:
            RecursoNoEncontrado: Si el usuario no existe
        """
        # Convertir string a UUID si es necesario
        from uuid import UUID
        if isinstance(usuario_id, str):
            try:
                usuario_id = UUID(usuario_id)
            except ValueError:
                raise ValidacionError(campo="usuario_id", mensaje="ID de usuario inválido")
        
        usuario = await self.repository.get_by_id(usuario_id)
        if not usuario:
            raise RecursoNoEncontrado(recurso="Usuario", id=usuario_id)
        
        if usuario.activo:
            return usuario
        
        return await self.repository.update(usuario_id, {"activo": True})
    
    async def desactivar_usuario(self, usuario_id: str) -> Usuario:
        """
        Desactiva un usuario (soft delete)
        
        Args:
            usuario_id: ID del usuario a desactivar
            
        Returns:
            Usuario desactivado
            
        Raises:
            RecursoNoEncontrado: Si el usuario no existe
        """
        # Convertir string a UUID si es necesario
        from uuid import UUID
        if isinstance(usuario_id, str):
            try:
                usuario_id = UUID(usuario_id)
            except ValueError:
                raise ValidacionError(campo="usuario_id", mensaje="ID de usuario inválido")
        
        usuario = await self.repository.get_by_id(usuario_id)
        if not usuario:
            raise RecursoNoEncontrado(recurso="Usuario", id=usuario_id)
        
        if not usuario.activo:
            return usuario
        
        return await self.repository.update(usuario_id, {"activo": False})
    
    async def obtener_usuario(self, usuario_id: str) -> Usuario:
        """
        Obtiene un usuario por ID
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Usuario encontrado
            
        Raises:
            RecursoNoEncontrado: Si el usuario no existe
        """
        # Convertir string a UUID si es necesario
        from uuid import UUID
        if isinstance(usuario_id, str):
            try:
                usuario_id = UUID(usuario_id)
            except ValueError:
                raise ValidacionError(campo="usuario_id", mensaje="ID de usuario inválido")
        
        usuario = await self.repository.get_by_id(usuario_id)
        if not usuario:
            raise RecursoNoEncontrado(recurso="Usuario", id=usuario_id)
        
        return usuario

    
    async def obtener_usuario_por_email(self, email: str) -> Optional[Usuario]:
        """
        Obtiene un usuario por email
        
        Args:
            email: Email del usuario
            
        Returns:
            Usuario encontrado o None
        """
        return await self.repository.get_by_email(email)
    
    async def listar_usuarios(
        self,
        skip: int = 0,
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[Usuario]:
        """
        Lista usuarios con paginación y filtros
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            filtros: Filtros opcionales (rol, activo, etc.)
            
        Returns:
            Lista de usuarios
        """
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
            filters=filtros
        )
    
    async def contar_usuarios(self, filtros: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el total de usuarios
        
        Args:
            filtros: Filtros opcionales
            
        Returns:
            Número total de usuarios
        """
        return await self.repository.count(filters=filtros)
