"""
Tests para schemas de Habilitación
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.habilitacion import (
    ConceptoTUPACreate,
    ConceptoTUPAUpdate,
    HabilitacionCreate,
    HabilitacionReview,
    HabilitacionObservacion,
    HabilitacionAprobacion,
    HabilitacionHabilitar,
    HabilitacionSuspension,
    HabilitacionRevocacion,
    PagoCreate,
    PagoConfirmacion,
    PagoRechazo
)


class TestConceptoTUPASchemas:
    """Tests para schemas de ConceptoTUPA"""
    
    def test_concepto_tupa_create_valido(self):
        """Test crear ConceptoTUPA con datos válidos"""
        data = {
            "codigo": "HAB-001",
            "descripcion": "Habilitación de conductor",
            "monto": Decimal("150.00"),
            "vigencia_desde": date.today(),
            "vigencia_hasta": date.today() + timedelta(days=365),
            "activo": True
        }
        
        schema = ConceptoTUPACreate(**data)
        
        assert schema.codigo == "HAB-001"
        assert schema.monto == Decimal("150.00")
        assert schema.activo is True
    
    def test_concepto_tupa_vigencia_invalida(self):
        """Test validación de vigencia_hasta anterior a vigencia_desde"""
        data = {
            "codigo": "HAB-001",
            "descripcion": "Habilitación de conductor",
            "monto": Decimal("150.00"),
            "vigencia_desde": date.today(),
            "vigencia_hasta": date.today() - timedelta(days=1),
            "activo": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConceptoTUPACreate(**data)
        
        assert "vigencia_hasta debe ser posterior" in str(exc_info.value)
    
    def test_concepto_tupa_monto_negativo(self):
        """Test validación de monto negativo"""
        data = {
            "codigo": "HAB-001",
            "descripcion": "Habilitación de conductor",
            "monto": Decimal("-150.00"),
            "vigencia_desde": date.today(),
            "activo": True
        }
        
        with pytest.raises(ValidationError):
            ConceptoTUPACreate(**data)
    
    def test_concepto_tupa_update_parcial(self):
        """Test actualización parcial de ConceptoTUPA"""
        data = {
            "monto": Decimal("200.00"),
            "activo": False
        }
        
        schema = ConceptoTUPAUpdate(**data)
        
        assert schema.monto == Decimal("200.00")
        assert schema.activo is False
        assert schema.descripcion is None


class TestHabilitacionSchemas:
    """Tests para schemas de Habilitación"""
    
    def test_habilitacion_create_valido(self):
        """Test crear Habilitación con datos válidos"""
        conductor_id = uuid4()
        data = {
            "conductor_id": conductor_id
        }
        
        schema = HabilitacionCreate(**data)
        
        assert schema.conductor_id == conductor_id
    
    def test_habilitacion_review_valido(self):
        """Test schema de revisión"""
        data = {
            "observaciones": "Documentos completos y válidos"
        }
        
        schema = HabilitacionReview(**data)
        
        assert schema.observaciones == "Documentos completos y válidos"
    
    def test_habilitacion_observacion_valida(self):
        """Test schema de observación con texto mínimo"""
        data = {
            "observaciones": "Falta certificado médico actualizado y licencia vencida"
        }
        
        schema = HabilitacionObservacion(**data)
        
        assert "certificado médico" in schema.observaciones
    
    def test_habilitacion_observacion_texto_corto(self):
        """Test validación de observación con texto muy corto"""
        data = {
            "observaciones": "Falta"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            HabilitacionObservacion(**data)
        
        assert "at least 10 characters" in str(exc_info.value)
    
    def test_habilitacion_aprobacion_valida(self):
        """Test schema de aprobación"""
        data = {
            "observaciones": "Aprobado sin observaciones"
        }
        
        schema = HabilitacionAprobacion(**data)
        
        assert schema.observaciones == "Aprobado sin observaciones"
    
    def test_habilitacion_habilitar_valido(self):
        """Test schema para habilitar conductor"""
        vigencia = date.today() + timedelta(days=365)
        data = {
            "vigencia_hasta": vigencia,
            "observaciones": "Habilitado por 1 año"
        }
        
        schema = HabilitacionHabilitar(**data)
        
        assert schema.vigencia_hasta == vigencia
        assert schema.observaciones == "Habilitado por 1 año"
    
    def test_habilitacion_habilitar_fecha_pasada(self):
        """Test validación de fecha de vigencia pasada"""
        data = {
            "vigencia_hasta": date.today() - timedelta(days=1),
            "observaciones": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            HabilitacionHabilitar(**data)
        
        assert "debe ser futura" in str(exc_info.value)
    
    def test_habilitacion_habilitar_fecha_hoy(self):
        """Test validación de fecha de vigencia igual a hoy"""
        data = {
            "vigencia_hasta": date.today(),
            "observaciones": "Test"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            HabilitacionHabilitar(**data)
        
        assert "debe ser futura" in str(exc_info.value)
    
    def test_habilitacion_suspension_valida(self):
        """Test schema de suspensión"""
        data = {
            "motivo": "Suspendido por infracción grave registrada en el sistema MTC"
        }
        
        schema = HabilitacionSuspension(**data)
        
        assert "infracción grave" in schema.motivo
    
    def test_habilitacion_suspension_motivo_corto(self):
        """Test validación de motivo de suspensión muy corto"""
        data = {
            "motivo": "Infracción"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            HabilitacionSuspension(**data)
        
        assert "at least 20 characters" in str(exc_info.value)
    
    def test_habilitacion_revocacion_valida(self):
        """Test schema de revocación"""
        data = {
            "motivo": "Revocado por acumulación de infracciones muy graves y decisión administrativa"
        }
        
        schema = HabilitacionRevocacion(**data)
        
        assert "Revocado" in schema.motivo


class TestPagoSchemas:
    """Tests para schemas de Pago"""
    
    def test_pago_create_valido(self):
        """Test crear Pago con datos válidos"""
        data = {
            "habilitacion_id": uuid4(),
            "concepto_tupa_id": uuid4(),
            "numero_recibo": "REC-2024-001",
            "monto": Decimal("150.00"),
            "fecha_pago": date.today(),
            "entidad_bancaria": "Banco de la Nación"
        }
        
        schema = PagoCreate(**data)
        
        assert schema.numero_recibo == "REC-2024-001"
        assert schema.monto == Decimal("150.00")
        assert schema.entidad_bancaria == "Banco de la Nación"
    
    def test_pago_fecha_futura(self):
        """Test validación de fecha de pago futura"""
        data = {
            "habilitacion_id": uuid4(),
            "concepto_tupa_id": uuid4(),
            "numero_recibo": "REC-2024-001",
            "monto": Decimal("150.00"),
            "fecha_pago": date.today() + timedelta(days=1),
            "entidad_bancaria": "Banco de la Nación"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PagoCreate(**data)
        
        assert "no puede ser futura" in str(exc_info.value)
    
    def test_pago_monto_negativo(self):
        """Test validación de monto negativo"""
        data = {
            "habilitacion_id": uuid4(),
            "concepto_tupa_id": uuid4(),
            "numero_recibo": "REC-2024-001",
            "monto": Decimal("-150.00"),
            "fecha_pago": date.today(),
            "entidad_bancaria": "Banco de la Nación"
        }
        
        with pytest.raises(ValidationError):
            PagoCreate(**data)
    
    def test_pago_confirmacion_valida(self):
        """Test schema de confirmación de pago"""
        data = {
            "observaciones": "Pago verificado correctamente"
        }
        
        schema = PagoConfirmacion(**data)
        
        assert schema.observaciones == "Pago verificado correctamente"
    
    def test_pago_rechazo_valido(self):
        """Test schema de rechazo de pago"""
        data = {
            "motivo": "Monto incorrecto, se esperaba S/. 150.00"
        }
        
        schema = PagoRechazo(**data)
        
        assert "Monto incorrecto" in schema.motivo
    
    def test_pago_rechazo_motivo_corto(self):
        """Test validación de motivo de rechazo muy corto"""
        data = {
            "motivo": "Error"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PagoRechazo(**data)
        
        assert "at least 10 characters" in str(exc_info.value)
