"""
Tests para UsuarioService
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.usuario_service import UsuarioService
from app.schemas.user import UsuarioCreate, UsuarioUpdate, CambiarPasswordRequest
from app.models.user import RolUsuario
from app.core.security import verify_password
from app.core.exceptions import RecursoNoEncontrado, ValidacionError


@pytest.mark.asyncio
class TestUsuarioService:
    """Tests para UsuarioService"""
    
    async def test_crear_usuario_exitoso(self, db_session: AsyncSession):
        """Test crear usuario con datos válidos"""
        service = UsuarioService(db_session)
        
        usuario_data = UsuarioCreate(
            email="test@drtc.gob.pe",
            nombres="Juan",
            apellidos="Pérez",
            rol=RolUsuario.DIRECTOR,
            password="SecurePass123!",
            activo=True
        )
        
        usuario = await service.crear_usuario(usuario_data)
        
        assert usuario.email == "test@drtc.gob.pe"
        assert usuario.nombres == "Juan"
        assert usuario.apellidos == "Pérez"
        assert usuario.rol == RolUsuario.DIRECTOR
        assert usuario.activo is True
        assert usuario.password_hash is not None
        assert verify_password("SecurePass123!", usuario.password_hash)
    
    async def test_crear_usuario_email_duplicado(self, db_session: AsyncSession):
        """Test crear usuario con email duplicado debe fallar"""
        service = UsuarioService(db_session)
        
        usuario_data = UsuarioCreate(
            email="duplicate@drtc.gob.pe",
            nombres="Juan",
            apellidos="Pérez",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        
        # Crear primer usuario
        await service.crear_usuario(usuario_data)
        
        # Intentar crear segundo usuario con mismo email
        with pytest.raises(ValidacionError) as exc_info:
            await service.crear_usuario(usuario_data)
        
        assert "email" in str(exc_info.value.campo)
        assert "ya está registrado" in str(exc_info.value.message)

    
    async def test_crear_gerente_sin_empresa_debe_fallar(self, db_session: AsyncSession):
        """Test crear gerente sin empresa_id debe fallar"""
        service = UsuarioService(db_session)
        
        usuario_data = UsuarioCreate(
            email="gerente@empresa.com",
            nombres="María",
            apellidos="López",
            rol=RolUsuario.GERENTE,
            password="SecurePass123!",
            activo=True
        )
        
        with pytest.raises(ValidacionError) as exc_info:
            await service.crear_usuario(usuario_data)
        
        assert "empresa_id" in str(exc_info.value.campo)
    
    async def test_actualizar_usuario_exitoso(self, db_session: AsyncSession):
        """Test actualizar usuario con datos válidos"""
        service = UsuarioService(db_session)
        
        # Crear usuario
        usuario_data = UsuarioCreate(
            email="update@drtc.gob.pe",
            nombres="Juan",
            apellidos="Pérez",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        usuario = await service.crear_usuario(usuario_data)
        
        # Actualizar usuario
        update_data = UsuarioUpdate(
            nombres="Juan Carlos",
            apellidos="Pérez García"
        )
        usuario_actualizado = await service.actualizar_usuario(str(usuario.id), update_data)
        
        assert usuario_actualizado.nombres == "Juan Carlos"
        assert usuario_actualizado.apellidos == "Pérez García"
        assert usuario_actualizado.email == "update@drtc.gob.pe"
    
    async def test_actualizar_usuario_no_existente(self, db_session: AsyncSession):
        """Test actualizar usuario que no existe debe fallar"""
        service = UsuarioService(db_session)
        
        update_data = UsuarioUpdate(nombres="Test")
        
        with pytest.raises(RecursoNoEncontrado):
            await service.actualizar_usuario("00000000-0000-0000-0000-000000000000", update_data)
    
    async def test_cambiar_password_exitoso(self, db_session: AsyncSession):
        """Test cambiar contraseña con datos válidos"""
        service = UsuarioService(db_session)
        
        # Crear usuario
        usuario_data = UsuarioCreate(
            email="password@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="OldPass123!",
            activo=True
        )
        usuario = await service.crear_usuario(usuario_data)

        
        # Cambiar contraseña
        password_data = CambiarPasswordRequest(
            password_actual="OldPass123!",
            password_nueva="NewPass456!",
            password_confirmacion="NewPass456!"
        )
        usuario_actualizado = await service.cambiar_password(str(usuario.id), password_data)
        
        # Verificar nueva contraseña
        assert verify_password("NewPass456!", usuario_actualizado.password_hash)
        assert not verify_password("OldPass123!", usuario_actualizado.password_hash)
    
    async def test_cambiar_password_actual_incorrecta(self, db_session: AsyncSession):
        """Test cambiar contraseña con contraseña actual incorrecta debe fallar"""
        service = UsuarioService(db_session)
        
        # Crear usuario
        usuario_data = UsuarioCreate(
            email="wrongpass@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="CorrectPass123!",
            activo=True
        )
        usuario = await service.crear_usuario(usuario_data)
        
        # Intentar cambiar con contraseña incorrecta
        password_data = CambiarPasswordRequest(
            password_actual="WrongPass123!",
            password_nueva="NewPass456!",
            password_confirmacion="NewPass456!"
        )
        
        with pytest.raises(ValidacionError) as exc_info:
            await service.cambiar_password(str(usuario.id), password_data)
        
        assert "password_actual" in str(exc_info.value.campo)
        assert "incorrecta" in str(exc_info.value.message)
    
    async def test_activar_usuario(self, db_session: AsyncSession):
        """Test activar usuario desactivado"""
        service = UsuarioService(db_session)
        
        # Crear usuario inactivo
        usuario_data = UsuarioCreate(
            email="inactive@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=False
        )
        usuario = await service.crear_usuario(usuario_data)
        assert usuario.activo is False
        
        # Activar usuario
        usuario_activado = await service.activar_usuario(str(usuario.id))
        assert usuario_activado.activo is True
    
    async def test_desactivar_usuario(self, db_session: AsyncSession):
        """Test desactivar usuario activo"""
        service = UsuarioService(db_session)
        
        # Crear usuario activo
        usuario_data = UsuarioCreate(
            email="active@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        usuario = await service.crear_usuario(usuario_data)
        assert usuario.activo is True

        
        # Desactivar usuario
        usuario_desactivado = await service.desactivar_usuario(str(usuario.id))
        assert usuario_desactivado.activo is False
    
    async def test_obtener_usuario_existente(self, db_session: AsyncSession):
        """Test obtener usuario por ID"""
        service = UsuarioService(db_session)
        
        # Crear usuario
        usuario_data = UsuarioCreate(
            email="get@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        usuario_creado = await service.crear_usuario(usuario_data)
        
        # Obtener usuario
        usuario = await service.obtener_usuario(str(usuario_creado.id))
        assert usuario.id == usuario_creado.id
        assert usuario.email == "get@drtc.gob.pe"
    
    async def test_obtener_usuario_no_existente(self, db_session: AsyncSession):
        """Test obtener usuario que no existe debe fallar"""
        service = UsuarioService(db_session)
        
        with pytest.raises(RecursoNoEncontrado):
            await service.obtener_usuario("00000000-0000-0000-0000-000000000000")
    
    async def test_obtener_usuario_por_email(self, db_session: AsyncSession):
        """Test obtener usuario por email"""
        service = UsuarioService(db_session)
        
        # Crear usuario
        usuario_data = UsuarioCreate(
            email="byemail@drtc.gob.pe",
            nombres="Test",
            apellidos="User",
            rol=RolUsuario.OPERARIO,
            password="SecurePass123!",
            activo=True
        )
        await service.crear_usuario(usuario_data)
        
        # Obtener por email
        usuario = await service.obtener_usuario_por_email("byemail@drtc.gob.pe")
        assert usuario is not None
        assert usuario.email == "byemail@drtc.gob.pe"
    
    async def test_listar_usuarios(self, db_session: AsyncSession):
        """Test listar usuarios con paginación"""
        service = UsuarioService(db_session)
        
        # Crear varios usuarios
        nombres_list = ["Juan", "María", "Pedro", "Ana", "Luis"]
        for i, nombre in enumerate(nombres_list):
            usuario_data = UsuarioCreate(
                email=f"user{i}@drtc.gob.pe",
                nombres=nombre,
                apellidos="Test",
                rol=RolUsuario.OPERARIO,
                password="SecurePass123!",
                activo=True
            )
            await service.crear_usuario(usuario_data)
        
        # Listar usuarios
        usuarios = await service.listar_usuarios(skip=0, limit=10)
        assert len(usuarios) >= 5
    
    async def test_contar_usuarios(self, db_session: AsyncSession):
        """Test contar usuarios"""
        service = UsuarioService(db_session)
        
        # Crear usuarios
        nombres_list = ["Carlos", "Rosa", "Miguel"]
        for i, nombre in enumerate(nombres_list):
            usuario_data = UsuarioCreate(
                email=f"count{i}@drtc.gob.pe",
                nombres=nombre,
                apellidos="Test",
                rol=RolUsuario.OPERARIO,
                password="SecurePass123!",
                activo=True
            )
            await service.crear_usuario(usuario_data)
        
        # Contar usuarios
        total = await service.contar_usuarios()
        assert total >= 3
