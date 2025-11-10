"""
Tests unitarios para el módulo de seguridad
"""
import pytest
from datetime import datetime, timedelta
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token
)


class TestPasswordHashing:
    """Tests para funciones de hashing de contraseñas"""
    
    def test_hash_password_returns_different_hash(self):
        """Test que el hash de la misma contraseña es diferente cada vez"""
        password = "mi_contraseña_segura"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2
        assert hash1 != password
        assert hash2 != password
    
    def test_verify_password_with_correct_password(self):
        """Test que verify_password retorna True con contraseña correcta"""
        password = "mi_contraseña_segura"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_with_incorrect_password(self):
        """Test que verify_password retorna False con contraseña incorrecta"""
        password = "mi_contraseña_segura"
        wrong_password = "contraseña_incorrecta"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_with_empty_string(self):
        """Test que se puede hashear una cadena vacía"""
        password = ""
        hashed = hash_password(password)
        
        assert hashed != ""
        assert verify_password(password, hashed) is True
    
    def test_hash_password_with_special_characters(self):
        """Test que se pueden hashear contraseñas con caracteres especiales"""
        password = "P@ssw0rd!#$%&*()_+-=[]{}|;:',.<>?/~`"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_password_with_unicode(self):
        """Test que se pueden hashear contraseñas con caracteres unicode"""
        password = "contraseña_con_ñ_y_acentós_🔒"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


class TestAccessToken:
    """Tests para tokens de acceso JWT"""
    
    def test_create_access_token_with_basic_data(self):
        """Test que se puede crear un token de acceso con datos básicos"""
        data = {"sub": "user_id_123", "email": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_includes_all_data(self):
        """Test que el token incluye todos los datos proporcionados"""
        data = {
            "sub": "user_id_123",
            "email": "test@example.com",
            "rol": "DIRECTOR",
            "empresa_id": "empresa_123"
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == "user_id_123"
        assert payload["email"] == "test@example.com"
        assert payload["rol"] == "DIRECTOR"
        assert payload["empresa_id"] == "empresa_123"
    
    def test_create_access_token_includes_metadata(self):
        """Test que el token incluye metadatos (exp, iat, type)"""
        data = {"sub": "user_id_123"}
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert "exp" in payload
        assert "iat" in payload
        assert payload["type"] == "access"
    
    def test_create_access_token_with_custom_expiration(self):
        """Test que se puede crear un token con expiración personalizada"""
        data = {"sub": "user_id_123"}
        custom_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_delta)
        payload = decode_token(token)
        
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        delta = exp_time - iat_time
        
        # Verificar que la diferencia sea aproximadamente 60 minutos
        assert 59 <= delta.total_seconds() / 60 <= 61
    
    def test_verify_access_token_with_valid_token(self):
        """Test que verify_token retorna el payload con token válido"""
        data = {"sub": "user_id_123", "email": "test@example.com"}
        token = create_access_token(data)
        payload = verify_token(token, token_type="access")
        
        assert payload is not None
        assert payload["sub"] == "user_id_123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_access_token_with_expired_token(self):
        """Test que verify_token retorna None con token expirado"""
        data = {"sub": "user_id_123"}
        # Crear token que expira en el pasado
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        payload = verify_token(token, token_type="access")
        
        assert payload is None
    
    def test_verify_access_token_with_invalid_token(self):
        """Test que verify_token retorna None con token inválido"""
        invalid_token = "token_invalido_123"
        payload = verify_token(invalid_token, token_type="access")
        
        assert payload is None
    
    def test_verify_access_token_with_wrong_type(self):
        """Test que verify_token retorna None si el tipo no coincide"""
        data = {"sub": "user_id_123"}
        token = create_access_token(data)
        # Intentar verificar como refresh token
        payload = verify_token(token, token_type="refresh")
        
        assert payload is None


class TestRefreshToken:
    """Tests para tokens de refresco JWT"""
    
    def test_create_refresh_token_with_basic_data(self):
        """Test que se puede crear un token de refresco con datos básicos"""
        data = {"sub": "user_id_123", "email": "test@example.com"}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token_includes_metadata(self):
        """Test que el token de refresco incluye metadatos correctos"""
        data = {"sub": "user_id_123"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        
        assert "exp" in payload
        assert "iat" in payload
        assert payload["type"] == "refresh"
    
    def test_create_refresh_token_with_custom_expiration(self):
        """Test que se puede crear un refresh token con expiración personalizada"""
        data = {"sub": "user_id_123"}
        custom_delta = timedelta(days=14)
        token = create_refresh_token(data, expires_delta=custom_delta)
        payload = decode_token(token)
        
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        delta = exp_time - iat_time
        
        # Verificar que la diferencia sea aproximadamente 14 días
        assert 13.9 <= delta.total_seconds() / 86400 <= 14.1
    
    def test_verify_refresh_token_with_valid_token(self):
        """Test que verify_token retorna el payload con refresh token válido"""
        data = {"sub": "user_id_123", "email": "test@example.com"}
        token = create_refresh_token(data)
        payload = verify_token(token, token_type="refresh")
        
        assert payload is not None
        assert payload["sub"] == "user_id_123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_refresh_token_with_wrong_type(self):
        """Test que verify_token retorna None si el tipo no coincide"""
        data = {"sub": "user_id_123"}
        token = create_refresh_token(data)
        # Intentar verificar como access token
        payload = verify_token(token, token_type="access")
        
        assert payload is None
    
    def test_access_and_refresh_tokens_are_different(self):
        """Test que access y refresh tokens son diferentes para los mismos datos"""
        data = {"sub": "user_id_123", "email": "test@example.com"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        assert access_token != refresh_token


class TestDecodeToken:
    """Tests para la función decode_token"""
    
    def test_decode_token_with_valid_token(self):
        """Test que decode_token puede decodificar un token válido"""
        data = {"sub": "user_id_123", "email": "test@example.com"}
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user_id_123"
        assert payload["email"] == "test@example.com"
    
    def test_decode_token_with_expired_token(self):
        """Test que decode_token puede decodificar un token expirado"""
        data = {"sub": "user_id_123"}
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        payload = decode_token(token)
        
        # decode_token no verifica expiración
        assert payload is not None
        assert payload["sub"] == "user_id_123"
    
    def test_decode_token_with_invalid_token(self):
        """Test que decode_token retorna None con token inválido"""
        invalid_token = "token_completamente_invalido"
        payload = decode_token(invalid_token)
        
        assert payload is None
