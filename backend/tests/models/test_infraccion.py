"""
Tests para modelos de Infracción
"""
import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.infraccion import (
    TipoInfraccion,
    Infraccion,
    AsignacionVehiculo,
    GravedadInfraccion,
    EstadoInfraccion
)
from app.models.conductor import Conductor, EstadoConductor
from app.models.empresa import Empresa
from app.models.user import Usuario, RolUsuario


class TestTipoInfraccion:
    """Tests para modelo TipoInfraccion"""
    
    def test_crear_tipo_infraccion_leve(self, db_session):
        """Test crear tipo de infracción leve"""
        tipo = TipoInfraccion(
            codigo="L001",
            descripcion="Exceso de velocidad menor a 10 km/h",
            gravedad=GravedadInfraccion.LEVE,
            puntos=5,
            activo="true"
        )
        
        db_session.add(tipo)
        db_session.commit()
        
        assert tipo.id is not None
        assert tipo.codigo == "L001"
        assert tipo.gravedad == GravedadInfraccion.LEVE
        assert tipo.puntos == 5
        assert tipo.activo == "true"
    
    def test_crear_tipo_infraccion_grave(self, db_session):
        """Test crear tipo de infracción grave"""
        tipo = TipoInfraccion(
            codigo="G001",
            descripcion="Conducir bajo efectos del alcohol",
            gravedad=GravedadInfraccion.GRAVE,
            puntos=50,
            activo="true"
        )
        
        db_session.add(tipo)
        db_session.commit()
        
        assert tipo.gravedad == GravedadInfraccion.GRAVE
        assert tipo.puntos == 50
    
    def test_crear_tipo_infraccion_muy_grave(self, db_session):
        """Test crear tipo de infracción muy grave"""
        tipo = TipoInfraccion(
            codigo="MG001",
            descripcion="Causar accidente con víctimas fatales",
            gravedad=GravedadInfraccion.MUY_GRAVE,
            puntos=100,
            activo="true"
        )
        
        db_session.add(tipo)
        db_session.commit()
        
        assert tipo.gravedad == GravedadInfraccion.MUY_GRAVE
        assert tipo.puntos == 100
    
    def test_codigo_unico(self, db_session):
        """Test que el código sea único"""
        tipo1 = TipoInfraccion(
            codigo="L001",
            descripcion="Infracción 1",
            gravedad=GravedadInfraccion.LEVE,
            puntos=5
        )
        
        tipo2 = TipoInfraccion(
            codigo="L001",
            descripcion="Infracción 2",
            gravedad=GravedadInfraccion.LEVE,
            puntos=10
        )
        
        db_session.add(tipo1)
        db_session.commit()
        
        db_session.add(tipo2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestInfraccion:
    """Tests para modelo Infraccion"""
    
    @pytest.fixture
    def usuario(self, db_session):
        """Fixture para crear usuario"""
        usuario = Usuario(
            email="operario@drtc.gob.pe",
            password_hash="hashed_password",
            nombres="Juan",
            apellidos="Pérez",
            rol=RolUsuario.OPERARIO,
            activo="true"
        )
        db_session.add(usuario)
        db_session.commit()
        return usuario
    
    @pytest.fixture
    def empresa(self, db_session):
        """Fixture para crear empresa"""
        empresa = Empresa(
            ruc="20123456789",
            razon_social="Transportes Test SAC",
            direccion="Av. Test 123",
            telefono="987654321",
            email="test@transportes.com",
            activo="true"
        )
        db_session.add(empresa)
        db_session.commit()
        return empresa
    
    @pytest.fixture
    def conductor(self, db_session, empresa):
        """Fixture para crear conductor"""
        conductor = Conductor(
            dni="12345678",
            nombres="Carlos",
            apellidos="López",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Jr. Test 456",
            telefono="987654321",
            email="carlos@test.com",
            licencia_numero="Q12345678",
            licencia_categoria="A-IIIb",
            licencia_emision=date.today() - timedelta(days=365),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=empresa.id,
            estado=EstadoConductor.HABILITADO
        )
        db_session.add(conductor)
        db_session.commit()
        return conductor
    
    @pytest.fixture
    def tipo_infraccion(self, db_session):
        """Fixture para crear tipo de infracción"""
        tipo = TipoInfraccion(
            codigo="G001",
            descripcion="Exceso de velocidad mayor a 50 km/h",
            gravedad=GravedadInfraccion.GRAVE,
            puntos=50,
            activo="true"
        )
        db_session.add(tipo)
        db_session.commit()
        return tipo
    
    def test_crear_infraccion(self, db_session, conductor, tipo_infraccion, usuario):
        """Test crear infracción"""
        infraccion = Infraccion(
            conductor_id=conductor.id,
            tipo_infraccion_id=tipo_infraccion.id,
            fecha_infraccion=date.today(),
            descripcion="Conductor excedió velocidad en 60 km/h en zona urbana",
            entidad_fiscalizadora="Policía Nacional del Perú",
            numero_acta="PNP-2024-001234",
            estado=EstadoInfraccion.REGISTRADA,
            registrado_por=usuario.id
        )
        
        db_session.add(infraccion)
        db_session.commit()
        
        assert infraccion.id is not None
        assert infraccion.conductor_id == conductor.id
        assert infraccion.tipo_infraccion_id == tipo_infraccion.id
        assert infraccion.estado == EstadoInfraccion.REGISTRADA
        assert infraccion.numero_acta == "PNP-2024-001234"
    
    def test_infraccion_con_resolucion(self, db_session, conductor, tipo_infraccion, usuario):
        """Test infracción con resolución"""
        infraccion = Infraccion(
            conductor_id=conductor.id,
            tipo_infraccion_id=tipo_infraccion.id,
            fecha_infraccion=date.today() - timedelta(days=30),
            descripcion="Infracción de tránsito",
            entidad_fiscalizadora="MTC",
            numero_acta="MTC-2024-001",
            estado=EstadoInfraccion.RESUELTA,
            resolucion="Multa pagada. Suspensión de 30 días cumplida.",
            registrado_por=usuario.id
        )
        
        db_session.add(infraccion)
        db_session.commit()
        
        assert infraccion.estado == EstadoInfraccion.RESUELTA
        assert infraccion.resolucion is not None
    
    def test_relacion_conductor_infracciones(self, db_session, conductor, tipo_infraccion, usuario):
        """Test relación entre conductor e infracciones"""
        infraccion1 = Infraccion(
            conductor_id=conductor.id,
            tipo_infraccion_id=tipo_infraccion.id,
            fecha_infraccion=date.today(),
            descripcion="Infracción 1",
            entidad_fiscalizadora="PNP",
            estado=EstadoInfraccion.REGISTRADA,
            registrado_por=usuario.id
        )
        
        infraccion2 = Infraccion(
            conductor_id=conductor.id,
            tipo_infraccion_id=tipo_infraccion.id,
            fecha_infraccion=date.today() - timedelta(days=10),
            descripcion="Infracción 2",
            entidad_fiscalizadora="MTC",
            estado=EstadoInfraccion.EN_PROCESO,
            registrado_por=usuario.id
        )
        
        db_session.add_all([infraccion1, infraccion2])
        db_session.commit()
        
        db_session.refresh(conductor)
        assert len(conductor.infracciones) == 2
    
    def test_infraccion_muy_grave(self, db_session, conductor, usuario):
        """Test infracción muy grave"""
        tipo_muy_grave = TipoInfraccion(
            codigo="MG001",
            descripcion="Conducir en estado de ebriedad",
            gravedad=GravedadInfraccion.MUY_GRAVE,
            puntos=100,
            activo="true"
        )
        db_session.add(tipo_muy_grave)
        db_session.commit()
        
        infraccion = Infraccion(
            conductor_id=conductor.id,
            tipo_infraccion_id=tipo_muy_grave.id,
            fecha_infraccion=date.today(),
            descripcion="Conductor con 0.8g/L de alcohol en sangre",
            entidad_fiscalizadora="Policía Nacional",
            numero_acta="PNP-EBRIEDAD-001",
            estado=EstadoInfraccion.REGISTRADA,
            registrado_por=usuario.id
        )
        
        db_session.add(infraccion)
        db_session.commit()
        
        assert infraccion.tipo_infraccion.gravedad == GravedadInfraccion.MUY_GRAVE
        assert infraccion.tipo_infraccion.puntos == 100
    
    def test_estados_infraccion(self, db_session, conductor, tipo_infraccion, usuario):
        """Test diferentes estados de infracción"""
        estados = [
            EstadoInfraccion.REGISTRADA,
            EstadoInfraccion.EN_PROCESO,
            EstadoInfraccion.RESUELTA,
            EstadoInfraccion.ANULADA
        ]
        
        for estado in estados:
            infraccion = Infraccion(
                conductor_id=conductor.id,
                tipo_infraccion_id=tipo_infraccion.id,
                fecha_infraccion=date.today(),
                descripcion=f"Infracción en estado {estado.value}",
                entidad_fiscalizadora="MTC",
                estado=estado,
                registrado_por=usuario.id
            )
            db_session.add(infraccion)
        
        db_session.commit()
        
        infracciones = db_session.query(Infraccion).filter(
            Infraccion.conductor_id == conductor.id
        ).all()
        
        assert len(infracciones) == 4


class TestAsignacionVehiculo:
    """Tests para modelo AsignacionVehiculo"""
    
    @pytest.fixture
    def empresa(self, db_session):
        """Fixture para crear empresa"""
        empresa = Empresa(
            ruc="20123456789",
            razon_social="Transportes Test SAC",
            direccion="Av. Test 123",
            telefono="987654321",
            email="test@transportes.com",
            activo="true"
        )
        db_session.add(empresa)
        db_session.commit()
        return empresa
    
    @pytest.fixture
    def conductor(self, db_session, empresa):
        """Fixture para crear conductor"""
        conductor = Conductor(
            dni="12345678",
            nombres="Carlos",
            apellidos="López",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Jr. Test 456",
            telefono="987654321",
            email="carlos@test.com",
            licencia_numero="Q12345678",
            licencia_categoria="A-IIIb",
            licencia_emision=date.today() - timedelta(days=365),
            licencia_vencimiento=date.today() + timedelta(days=365),
            empresa_id=empresa.id,
            estado=EstadoConductor.HABILITADO
        )
        db_session.add(conductor)
        db_session.commit()
        return conductor
    
    def test_crear_asignacion_vehiculo(self, db_session, conductor):
        """Test crear asignación de vehículo"""
        asignacion = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="ABC-123",
            fecha_asignacion=date.today(),
            activo="true",
            observaciones="Asignación inicial"
        )
        
        db_session.add(asignacion)
        db_session.commit()
        
        assert asignacion.id is not None
        assert asignacion.conductor_id == conductor.id
        assert asignacion.placa_vehiculo == "ABC-123"
        assert asignacion.activo == "true"
        assert asignacion.fecha_desasignacion is None
    
    def test_desasignar_vehiculo(self, db_session, conductor):
        """Test desasignar vehículo"""
        asignacion = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="ABC-123",
            fecha_asignacion=date.today() - timedelta(days=30),
            activo="true"
        )
        
        db_session.add(asignacion)
        db_session.commit()
        
        # Desasignar
        asignacion.activo = "false"
        asignacion.fecha_desasignacion = date.today()
        asignacion.observaciones = "Cambio de vehículo"
        db_session.commit()
        
        assert asignacion.activo == "false"
        assert asignacion.fecha_desasignacion is not None
    
    def test_multiples_asignaciones_historico(self, db_session, conductor):
        """Test múltiples asignaciones (histórico)"""
        # Primera asignación (inactiva)
        asignacion1 = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="ABC-123",
            fecha_asignacion=date.today() - timedelta(days=60),
            fecha_desasignacion=date.today() - timedelta(days=30),
            activo="false"
        )
        
        # Segunda asignación (activa)
        asignacion2 = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="XYZ-789",
            fecha_asignacion=date.today() - timedelta(days=30),
            activo="true"
        )
        
        db_session.add_all([asignacion1, asignacion2])
        db_session.commit()
        
        db_session.refresh(conductor)
        assert len(conductor.asignaciones_vehiculo) == 2
        
        # Verificar asignación activa
        asignaciones_activas = [a for a in conductor.asignaciones_vehiculo if a.activo == "true"]
        assert len(asignaciones_activas) == 1
        assert asignaciones_activas[0].placa_vehiculo == "XYZ-789"
    
    def test_relacion_conductor_asignaciones(self, db_session, conductor):
        """Test relación entre conductor y asignaciones"""
        asignacion = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="ABC-123",
            fecha_asignacion=date.today(),
            activo="true"
        )
        
        db_session.add(asignacion)
        db_session.commit()
        
        db_session.refresh(conductor)
        assert len(conductor.asignaciones_vehiculo) == 1
        assert conductor.asignaciones_vehiculo[0].placa_vehiculo == "ABC-123"
    
    def test_asignacion_con_observaciones(self, db_session, conductor):
        """Test asignación con observaciones"""
        asignacion = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="ABC-123",
            fecha_asignacion=date.today(),
            activo="true",
            observaciones="Vehículo nuevo. Conductor con experiencia de 5 años."
        )
        
        db_session.add(asignacion)
        db_session.commit()
        
        assert asignacion.observaciones is not None
        assert "experiencia" in asignacion.observaciones.lower()
    
    def test_consultar_vehiculo_actual_conductor(self, db_session, conductor):
        """Test consultar vehículo actual de un conductor"""
        # Crear varias asignaciones
        asignacion1 = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="OLD-111",
            fecha_asignacion=date.today() - timedelta(days=90),
            fecha_desasignacion=date.today() - timedelta(days=60),
            activo="false"
        )
        
        asignacion2 = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="OLD-222",
            fecha_asignacion=date.today() - timedelta(days=60),
            fecha_desasignacion=date.today() - timedelta(days=30),
            activo="false"
        )
        
        asignacion3 = AsignacionVehiculo(
            conductor_id=conductor.id,
            placa_vehiculo="NEW-333",
            fecha_asignacion=date.today() - timedelta(days=30),
            activo="true"
        )
        
        db_session.add_all([asignacion1, asignacion2, asignacion3])
        db_session.commit()
        
        # Consultar asignación activa
        asignacion_actual = db_session.query(AsignacionVehiculo).filter(
            AsignacionVehiculo.conductor_id == conductor.id,
            AsignacionVehiculo.activo == "true"
        ).first()
        
        assert asignacion_actual is not None
        assert asignacion_actual.placa_vehiculo == "NEW-333"
