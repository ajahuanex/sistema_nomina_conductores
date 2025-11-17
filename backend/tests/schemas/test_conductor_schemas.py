"""
Tests para schemas de Conductor
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4
from pydantic import ValidationError
from app.schemas.conductor import (
    ConductorBase,
    ConductorCreate,
    ConductorUpdate,
    ConductorEstadoUpdate,
    ConductorValidacionCategoria
)


class TestConductorBase:
    """Tests para ConductorBase schema"""
    
    def test_conductor_base_valido(self):
        """Test crear conductor base con datos válidos"""
        data = {
            "dni": "12345678",
            "nombres": "Juan Carlos",
            "apellidos": "Pérez García",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123, Puno",
            "telefono": "987654321",
            "email": "juan.perez@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        conductor = ConductorBase(**data)
        assert conductor.dni == "12345678"
        assert conductor.nombres == "Juan Carlos"
        assert conductor.licencia_categoria == "A-IIIb"
    
    def test_dni_debe_tener_8_digitos(self):
        """Test validación de DNI con 8 dígitos"""
        data = {
            "dni": "123456",  # Solo 6 dígitos
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        # Pydantic valida el tamaño antes del validator personalizado
        assert "at least 8 characters" in str(exc_info.value) or "DNI debe tener exactamente 8 dígitos" in str(exc_info.value)
    
    def test_dni_debe_ser_numerico(self):
        """Test validación de DNI numérico"""
        data = {
            "dni": "1234567A",  # Contiene letra
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        assert "DNI debe contener solo dígitos" in str(exc_info.value)
    
    def test_email_invalido(self):
        """Test validación de email"""
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "email_invalido",  # Sin @ y dominio
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        assert "Email inválido" in str(exc_info.value)
    
    def test_licencia_vencida(self):
        """Test validación de licencia vencida"""
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() - timedelta(days=1)  # Vencida ayer
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        assert "licencia de conducir está vencida" in str(exc_info.value)
    
    def test_categoria_licencia_invalida(self):
        """Test validación de categoría de licencia"""
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "B-I",  # Categoría inválida
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        assert "Categoría de licencia inválida" in str(exc_info.value)
    
    def test_edad_minima_18_anos(self):
        """Test validación de edad mínima"""
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date.today() - timedelta(days=365*17),  # 17 años
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        assert "debe tener al menos 18 años" in str(exc_info.value)
    
    def test_fecha_emision_futura(self):
        """Test validación de fecha de emisión futura"""
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date.today() + timedelta(days=1),  # Fecha futura
            "licencia_vencimiento": date.today() + timedelta(days=365)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorBase(**data)
        
        assert "fecha de emisión no puede ser futura" in str(exc_info.value)
    
    def test_todas_categorias_validas(self):
        """Test que todas las categorías válidas sean aceptadas"""
        categorias = ['A-I', 'A-IIa', 'A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc']
        
        for categoria in categorias:
            data = {
                "dni": "12345678",
                "nombres": "Juan",
                "apellidos": "Pérez",
                "fecha_nacimiento": date(1990, 5, 15),
                "direccion": "Av. Principal 123",
                "telefono": "987654321",
                "email": "juan@example.com",
                "licencia_numero": "Q12345678",
                "licencia_categoria": categoria,
                "licencia_emision": date(2020, 1, 1),
                "licencia_vencimiento": date.today() + timedelta(days=365)
            }
            
            conductor = ConductorBase(**data)
            assert conductor.licencia_categoria == categoria


class TestConductorCreate:
    """Tests para ConductorCreate schema"""
    
    def test_conductor_create_valido(self):
        """Test crear conductor con empresa_id"""
        empresa_id = uuid4()
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa_id
        }
        
        conductor = ConductorCreate(**data)
        assert conductor.empresa_id == empresa_id
    
    def test_validar_categoria_para_mercancias(self):
        """Test validación de categoría para transporte de mercancías"""
        empresa_id = uuid4()
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa_id
        }
        
        conductor = ConductorCreate(**data)
        assert conductor.validar_categoria_para_tipo_autorizacion("MERCANCIAS") is True
    
    def test_validar_categoria_invalida_para_mercancias(self):
        """Test categoría inválida para transporte de mercancías"""
        empresa_id = uuid4()
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIa",  # No válida para mercancías
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa_id
        }
        
        conductor = ConductorCreate(**data)
        assert conductor.validar_categoria_para_tipo_autorizacion("MERCANCIAS") is False
    
    def test_validar_categoria_para_turismo(self):
        """Test validación de categoría para transporte de turismo"""
        empresa_id = uuid4()
        data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez",
            "fecha_nacimiento": date(1990, 5, 15),
            "direccion": "Av. Principal 123",
            "telefono": "987654321",
            "email": "juan@example.com",
            "licencia_numero": "Q12345678",
            "licencia_categoria": "A-IIb",
            "licencia_emision": date(2020, 1, 1),
            "licencia_vencimiento": date.today() + timedelta(days=365),
            "empresa_id": empresa_id
        }
        
        conductor = ConductorCreate(**data)
        assert conductor.validar_categoria_para_tipo_autorizacion("TURISMO") is True


class TestConductorUpdate:
    """Tests para ConductorUpdate schema"""
    
    def test_conductor_update_parcial(self):
        """Test actualización parcial de conductor"""
        data = {
            "telefono": "999888777",
            "email": "nuevo@example.com"
        }
        
        conductor = ConductorUpdate(**data)
        assert conductor.telefono == "999888777"
        assert conductor.email == "nuevo@example.com"
        assert conductor.nombres is None
    
    def test_conductor_update_email_invalido(self):
        """Test validación de email en actualización"""
        data = {
            "email": "email_invalido"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorUpdate(**data)
        
        assert "Email inválido" in str(exc_info.value)
    
    def test_conductor_update_licencia_vencida(self):
        """Test validación de licencia vencida en actualización"""
        data = {
            "licencia_vencimiento": date.today() - timedelta(days=1)
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorUpdate(**data)
        
        assert "licencia de conducir está vencida" in str(exc_info.value)


class TestConductorEstadoUpdate:
    """Tests para ConductorEstadoUpdate schema"""
    
    def test_cambio_estado_valido(self):
        """Test cambio de estado válido"""
        data = {
            "estado": "habilitado",
            "observacion": "Conductor habilitado correctamente"
        }
        
        estado_update = ConductorEstadoUpdate(**data)
        assert estado_update.estado == "habilitado"
        assert estado_update.observacion == "Conductor habilitado correctamente"
    
    def test_cambio_estado_invalido(self):
        """Test cambio a estado inválido"""
        data = {
            "estado": "estado_invalido"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorEstadoUpdate(**data)
        
        assert "Estado inválido" in str(exc_info.value)
    
    def test_todos_estados_validos(self):
        """Test que todos los estados válidos sean aceptados"""
        estados = ['pendiente', 'habilitado', 'observado', 'suspendido', 'revocado']
        
        for estado in estados:
            data = {"estado": estado}
            estado_update = ConductorEstadoUpdate(**data)
            assert estado_update.estado == estado


class TestConductorValidacionCategoria:
    """Tests para ConductorValidacionCategoria schema"""
    
    def test_validacion_categoria_valida(self):
        """Test validación de categoría válida"""
        data = {
            "licencia_categoria": "A-IIIb",
            "tipo_autorizacion_codigo": "MERCANCIAS"
        }
        
        validacion = ConductorValidacionCategoria(**data)
        assert validacion.licencia_categoria == "A-IIIb"
        assert validacion.tipo_autorizacion_codigo == "MERCANCIAS"
    
    def test_validacion_categoria_invalida(self):
        """Test validación de categoría inválida"""
        data = {
            "licencia_categoria": "B-I",
            "tipo_autorizacion_codigo": "MERCANCIAS"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ConductorValidacionCategoria(**data)
        
        assert "Categoría de licencia inválida" in str(exc_info.value)
