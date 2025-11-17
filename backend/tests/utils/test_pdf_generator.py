"""
Tests para el generador de PDFs
"""
import pytest
from datetime import datetime, date, timedelta
from app.utils.pdf_generator import CertificadoHabilitacionPDF


class TestCertificadoHabilitacionPDF:
    """Tests para generación de certificados de habilitación"""
    
    def test_generar_certificado_basico(self):
        """Test: Debe generar un certificado PDF básico"""
        # Arrange
        generador = CertificadoHabilitacionPDF()
        
        # Act
        pdf_bytes = generador.generar(
            codigo_habilitacion="HAB-20240101120000-ABC123",
            conductor_nombre="Juan Carlos",
            conductor_apellidos="Pérez García",
            conductor_dni="12345678",
            licencia_numero="Q12345678",
            licencia_categoria="A-IIIb",
            empresa_razon_social="Transportes Test SAC",
            empresa_ruc="20123456789",
            fecha_habilitacion=datetime(2024, 1, 1, 12, 0, 0),
            vigencia_hasta=date(2025, 1, 1),
            habilitado_por="Director DRTC"
        )
        
        # Assert
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # Verificar que es un PDF válido (comienza con %PDF)
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generar_certificado_con_datos_completos(self):
        """Test: Debe generar certificado con todos los datos"""
        # Arrange
        generador = CertificadoHabilitacionPDF()
        fecha_hab = datetime.now()
        vigencia = date.today() + timedelta(days=365)
        
        # Act
        pdf_bytes = generador.generar(
            codigo_habilitacion="HAB-20240615143022-XYZ789",
            conductor_nombre="María Elena",
            conductor_apellidos="Rodríguez Mamani",
            conductor_dni="87654321",
            licencia_numero="Q87654321",
            licencia_categoria="A-IIIc",
            empresa_razon_social="Empresa de Transportes Turísticos del Sur EIRL",
            empresa_ruc="20987654321",
            fecha_habilitacion=fecha_hab,
            vigencia_hasta=vigencia,
            habilitado_por="Juan Pérez - Director Regional"
        )
        
        # Assert
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000  # PDF debe tener contenido sustancial
    
    def test_generar_certificado_con_caracteres_especiales(self):
        """Test: Debe manejar caracteres especiales en nombres"""
        # Arrange
        generador = CertificadoHabilitacionPDF()
        
        # Act
        pdf_bytes = generador.generar(
            codigo_habilitacion="HAB-20240101120000-TEST01",
            conductor_nombre="José María",
            conductor_apellidos="Ñuñez Ávila",
            conductor_dni="11223344",
            licencia_numero="Q11223344",
            licencia_categoria="A-IIb",
            empresa_razon_social="Transportes Ñandú S.A.C.",
            empresa_ruc="20111222333",
            fecha_habilitacion=datetime.now(),
            vigencia_hasta=date.today() + timedelta(days=365),
            habilitado_por="Subdirector DRTC"
        )
        
        # Assert
        assert pdf_bytes is not None
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generar_certificado_multiples_veces(self):
        """Test: Debe poder generar múltiples certificados"""
        # Arrange
        generador = CertificadoHabilitacionPDF()
        
        # Act
        pdf1 = generador.generar(
            codigo_habilitacion="HAB-001",
            conductor_nombre="Conductor",
            conductor_apellidos="Uno",
            conductor_dni="11111111",
            licencia_numero="Q11111111",
            licencia_categoria="A-IIIb",
            empresa_razon_social="Empresa Uno",
            empresa_ruc="20111111111",
            fecha_habilitacion=datetime.now(),
            vigencia_hasta=date.today() + timedelta(days=365),
            habilitado_por="Director"
        )
        
        pdf2 = generador.generar(
            codigo_habilitacion="HAB-002",
            conductor_nombre="Conductor",
            conductor_apellidos="Dos",
            conductor_dni="22222222",
            licencia_numero="Q22222222",
            licencia_categoria="A-IIIc",
            empresa_razon_social="Empresa Dos",
            empresa_ruc="20222222222",
            fecha_habilitacion=datetime.now(),
            vigencia_hasta=date.today() + timedelta(days=365),
            habilitado_por="Subdirector"
        )
        
        # Assert
        assert pdf1 is not None
        assert pdf2 is not None
        assert pdf1 != pdf2  # Deben ser diferentes
        assert len(pdf1) > 0
        assert len(pdf2) > 0
