"""
Tests para modelos de Auditoría y Notificación
"""
import pytest
from datetime import datetime, timedelta
from app.models.auditoria import Auditoria, Notificacion, AccionAuditoria, TipoNotificacion
from app.models.user import Usuario, RolUsuario


class TestAuditoria:
    """Tests para modelo Auditoria"""
    
    @pytest.fixture
    def usuario(self, db_session):
        """Fixture para crear usuario"""
        usuario = Usuario(
            email="admin@drtc.gob.pe",
            password_hash="hashed_password",
            nombres="Admin",
            apellidos="Sistema",
            rol=RolUsuario.SUPERUSUARIO,
            activo=True
        )
        db_session.add(usuario)
        db_session.commit()
        return usuario
    
    def test_crear_auditoria_basica(self, db_session, usuario):
        """Test crear registro de auditoría básico"""
        auditoria = Auditoria(
            usuario_id=usuario.id,
            tabla="conductores",
            accion="crear",
            registro_id="123e4567-e89b-12d3-a456-426614174000",
            ip_address="192.168.1.100"
        )
        
        db_session.add(auditoria)
        db_session.commit()
        
        assert auditoria.id is not None
        assert auditoria.usuario_id == usuario.id
        assert auditoria.tabla == "conductores"
        assert auditoria.accion == "crear"
        assert auditoria.ip_address == "192.168.1.100"
    
    def test_auditoria_con_datos_anteriores_y_nuevos(self, db_session, usuario):
        """Test auditoría con datos anteriores y nuevos"""
        datos_anteriores = {
            "estado": "pendiente",
            "observaciones": "Sin observaciones"
        }
        
        datos_nuevos = {
            "estado": "habilitado",
            "observaciones": "Conductor habilitado correctamente"
        }
        
        auditoria = Auditoria(
            usuario_id=usuario.id,
            tabla="conductores",
            accion="actualizar",
            registro_id="conductor-123",
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address="192.168.1.100",
            descripcion="Cambio de estado de conductor"
        )
        
        db_session.add(auditoria)
        db_session.commit()
        
        assert auditoria.datos_anteriores["estado"] == "pendiente"
        assert auditoria.datos_nuevos["estado"] == "habilitado"
        assert auditoria.descripcion is not None
    
    def test_auditoria_login(self, db_session, usuario):
        """Test auditoría de login"""
        auditoria = Auditoria(
            usuario_id=usuario.id,
            tabla="usuarios",
            accion="login",
            registro_id=str(usuario.id),
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            descripcion="Usuario inició sesión"
        )
        
        db_session.add(auditoria)
        db_session.commit()
        
        assert auditoria.accion == "login"
        assert auditoria.user_agent is not None
    
    def test_auditoria_habilitacion(self, db_session, usuario):
        """Test auditoría de habilitación de conductor"""
        auditoria = Auditoria(
            usuario_id=usuario.id,
            tabla="habilitaciones",
            accion="habilitar",
            registro_id="hab-123",
            datos_nuevos={
                "estado": "habilitado",
                "codigo_habilitacion": "DRTC-2024-001",
                "vigencia_hasta": "2025-12-31"
            },
            ip_address="192.168.1.100",
            descripcion="Conductor habilitado tras verificación de documentos y pago"
        )
        
        db_session.add(auditoria)
        db_session.commit()
        
        assert auditoria.accion == "habilitar"
        assert "codigo_habilitacion" in auditoria.datos_nuevos
    
    def test_auditoria_suspension(self, db_session, usuario):
        """Test auditoría de suspensión"""
        auditoria = Auditoria(
            usuario_id=usuario.id,
            tabla="conductores",
            accion="suspender",
            registro_id="conductor-123",
            datos_anteriores={"estado": "habilitado"},
            datos_nuevos={"estado": "suspendido"},
            ip_address="192.168.1.100",
            descripcion="Conductor suspendido por infracción grave"
        )
        
        db_session.add(auditoria)
        db_session.commit()
        
        assert auditoria.accion == "suspender"
        assert auditoria.datos_anteriores["estado"] == "habilitado"
        assert auditoria.datos_nuevos["estado"] == "suspendido"
    
    def test_consultar_auditoria_por_usuario(self, db_session, usuario):
        """Test consultar auditoría por usuario"""
        # Crear múltiples registros de auditoría
        acciones = ["crear", "actualizar", "eliminar"]
        
        for accion in acciones:
            auditoria = Auditoria(
                usuario_id=usuario.id,
                tabla="conductores",
                accion=accion,
                ip_address="192.168.1.100"
            )
            db_session.add(auditoria)
        
        db_session.commit()
        
        # Consultar
        registros = db_session.query(Auditoria).filter(
            Auditoria.usuario_id == usuario.id
        ).all()
        
        assert len(registros) == 3
    
    def test_consultar_auditoria_por_tabla(self, db_session, usuario):
        """Test consultar auditoría por tabla"""
        tablas = ["conductores", "empresas", "habilitaciones"]
        
        for tabla in tablas:
            auditoria = Auditoria(
                usuario_id=usuario.id,
                tabla=tabla,
                accion="crear",
                ip_address="192.168.1.100"
            )
            db_session.add(auditoria)
        
        db_session.commit()
        
        # Consultar solo conductores
        registros = db_session.query(Auditoria).filter(
            Auditoria.tabla == "conductores"
        ).all()
        
        assert len(registros) == 1
        assert registros[0].tabla == "conductores"
    
    def test_auditoria_con_user_agent(self, db_session, usuario):
        """Test auditoría con información de user agent"""
        auditoria = Auditoria(
            usuario_id=usuario.id,
            tabla="configuracion",
            accion="actualizar",
            registro_id="tupa-config",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            descripcion="Actualización de montos TUPA"
        )
        
        db_session.add(auditoria)
        db_session.commit()
        
        assert "Mozilla" in auditoria.user_agent
        assert auditoria.ip_address is not None


class TestNotificacion:
    """Tests para modelo Notificacion"""
    
    @pytest.fixture
    def usuario(self, db_session):
        """Fixture para crear usuario"""
        usuario = Usuario(
            email="gerente@transportes.com",
            password_hash="hashed_password",
            nombres="Juan",
            apellidos="Pérez",
            rol=RolUsuario.GERENTE,
            activo=True
        )
        db_session.add(usuario)
        db_session.commit()
        return usuario
    
    def test_crear_notificacion_basica(self, db_session, usuario):
        """Test crear notificación básica"""
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo="solicitud_observada",
            asunto="Solicitud de habilitación observada",
            mensaje="Su solicitud de habilitación para el conductor DNI 12345678 ha sido observada.",
            leida=False
        )
        
        db_session.add(notificacion)
        db_session.commit()
        
        assert notificacion.id is not None
        assert notificacion.usuario_id == usuario.id
        assert notificacion.leida is False
        assert notificacion.enviada_at is not None
    
    def test_notificacion_conductor_habilitado(self, db_session, usuario):
        """Test notificación de conductor habilitado"""
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo="conductor_habilitado",
            asunto="Conductor habilitado exitosamente",
            mensaje="El conductor Carlos López (DNI: 12345678) ha sido habilitado correctamente.",
            metadata={
                "conductor_id": "123e4567-e89b-12d3-a456-426614174000",
                "conductor_dni": "12345678",
                "codigo_habilitacion": "DRTC-2024-001"
            },
            leida=False
        )
        
        db_session.add(notificacion)
        db_session.commit()
        
        assert notificacion.tipo == "conductor_habilitado"
        assert "conductor_dni" in notificacion.metadata
    
    def test_notificacion_licencia_por_vencer(self, db_session, usuario):
        """Test notificación de licencia por vencer"""
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo="licencia_por_vencer",
            asunto="Licencia de conducir próxima a vencer",
            mensaje="La licencia del conductor Carlos López vence en 30 días.",
            metadata={
                "conductor_id": "123e4567-e89b-12d3-a456-426614174000",
                "dias_restantes": 30,
                "fecha_vencimiento": "2024-12-31"
            },
            leida=False
        )
        
        db_session.add(notificacion)
        db_session.commit()
        
        assert notificacion.tipo == "licencia_por_vencer"
        assert notificacion.metadata["dias_restantes"] == 30
    
    def test_marcar_notificacion_como_leida(self, db_session, usuario):
        """Test marcar notificación como leída"""
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Alerta del sistema",
            mensaje="Mensaje de prueba",
            leida=False
        )
        
        db_session.add(notificacion)
        db_session.commit()
        
        assert notificacion.leida is False
        assert notificacion.leida_at is None
        
        # Marcar como leída
        notificacion.marcar_como_leida()
        db_session.commit()
        
        assert notificacion.leida is True
        assert notificacion.leida_at is not None
    
    def test_consultar_notificaciones_no_leidas(self, db_session, usuario):
        """Test consultar notificaciones no leídas"""
        # Crear notificaciones leídas y no leídas
        notif1 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación 1",
            mensaje="Mensaje 1",
            leida=False
        )
        
        notif2 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación 2",
            mensaje="Mensaje 2",
            leida=True,
            leida_at=datetime.utcnow()
        )
        
        notif3 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación 3",
            mensaje="Mensaje 3",
            leida=False
        )
        
        db_session.add_all([notif1, notif2, notif3])
        db_session.commit()
        
        # Consultar no leídas
        no_leidas = db_session.query(Notificacion).filter(
            Notificacion.usuario_id == usuario.id,
            Notificacion.leida == False
        ).all()
        
        assert len(no_leidas) == 2
    
    def test_notificacion_infraccion_grave(self, db_session, usuario):
        """Test notificación de infracción grave"""
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo="infraccion_grave",
            asunto="Infracción grave registrada",
            mensaje="Se ha registrado una infracción grave para el conductor DNI 12345678.",
            metadata={
                "conductor_id": "123e4567-e89b-12d3-a456-426614174000",
                "infraccion_id": "inf-123",
                "gravedad": "muy_grave",
                "descripcion": "Conducir en estado de ebriedad"
            },
            leida=False
        )
        
        db_session.add(notificacion)
        db_session.commit()
        
        assert notificacion.tipo == "infraccion_grave"
        assert notificacion.metadata["gravedad"] == "muy_grave"
    
    def test_relacion_usuario_notificaciones(self, db_session, usuario):
        """Test relación entre usuario y notificaciones"""
        notif1 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación 1",
            mensaje="Mensaje 1",
            leida=False
        )
        
        notif2 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación 2",
            mensaje="Mensaje 2",
            leida=False
        )
        
        db_session.add_all([notif1, notif2])
        db_session.commit()
        
        db_session.refresh(usuario)
        assert len(usuario.notificaciones) == 2
    
    def test_notificacion_actualizacion_tupa(self, db_session, usuario):
        """Test notificación de actualización de TUPA"""
        notificacion = Notificacion(
            usuario_id=usuario.id,
            tipo="actualizacion_tupa",
            asunto="Actualización de montos TUPA",
            mensaje="Se han actualizado los montos del TUPA. Nuevos montos vigentes desde el 01/01/2025.",
            metadata={
                "fecha_vigencia": "2025-01-01",
                "monto_anterior": 150.00,
                "monto_nuevo": 180.00
            },
            leida=False
        )
        
        db_session.add(notificacion)
        db_session.commit()
        
        assert notificacion.tipo == "actualizacion_tupa"
        assert "monto_nuevo" in notificacion.metadata
    
    def test_ordenar_notificaciones_por_fecha(self, db_session, usuario):
        """Test ordenar notificaciones por fecha"""
        # Crear notificaciones en diferentes momentos
        notif1 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación antigua",
            mensaje="Mensaje 1",
            leida=False
        )
        notif1.enviada_at = datetime.utcnow() - timedelta(days=5)
        
        notif2 = Notificacion(
            usuario_id=usuario.id,
            tipo="alerta_sistema",
            asunto="Notificación reciente",
            mensaje="Mensaje 2",
            leida=False
        )
        notif2.enviada_at = datetime.utcnow()
        
        db_session.add_all([notif1, notif2])
        db_session.commit()
        
        # Consultar ordenadas por fecha descendente
        notificaciones = db_session.query(Notificacion).filter(
            Notificacion.usuario_id == usuario.id
        ).order_by(Notificacion.enviada_at.desc()).all()
        
        assert notificaciones[0].asunto == "Notificación reciente"
        assert notificaciones[1].asunto == "Notificación antigua"
