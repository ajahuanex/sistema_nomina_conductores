"""
Tests para utilidades de manejo de archivos
"""
import pytest
import io
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.utils.file_handler import (
    validate_file_type,
    validate_file_size,
    generate_unique_filename,
    save_upload_file,
    delete_file,
    get_file_path,
    file_exists,
    ensure_upload_directory,
    MAX_FILE_SIZE,
    UPLOAD_DIR
)


@pytest.mark.asyncio
class TestFileValidation:
    """Tests para validación de archivos"""
    
    def test_validate_file_type_pdf_valido(self):
        """Test validar tipo PDF válido"""
        # No debe lanzar excepción
        validate_file_type("documento.pdf", "application/pdf")
    
    def test_validate_file_type_jpg_valido(self):
        """Test validar tipo JPG válido"""
        validate_file_type("imagen.jpg", "image/jpeg")
    
    def test_validate_file_type_png_valido(self):
        """Test validar tipo PNG válido"""
        validate_file_type("imagen.png", "image/png")
    
    def test_validate_file_type_extension_invalida(self):
        """Test validar extensión inválida"""
        with pytest.raises(HTTPException) as exc_info:
            validate_file_type("documento.txt", "text/plain")
        
        assert exc_info.value.status_code == 400
        assert "no permitido" in exc_info.value.detail.lower()
    
    def test_validate_file_type_mime_invalido(self):
        """Test validar MIME type inválido"""
        with pytest.raises(HTTPException) as exc_info:
            validate_file_type("documento.pdf", "text/plain")
        
        assert exc_info.value.status_code == 400
        assert "no permitido" in exc_info.value.detail.lower()
    
    def test_validate_file_size_valido(self):
        """Test validar tamaño válido"""
        # 5MB - válido
        validate_file_size(5 * 1024 * 1024)
    
    def test_validate_file_size_excedido(self):
        """Test validar tamaño excedido"""
        # 11MB - excede el límite
        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(11 * 1024 * 1024)
        
        assert exc_info.value.status_code == 400
        assert "tamaño máximo" in exc_info.value.detail.lower()


class TestFilenameGeneration:
    """Tests para generación de nombres de archivo"""
    
    def test_generate_unique_filename_pdf(self):
        """Test generar nombre único para PDF"""
        unique_name, ext = generate_unique_filename("documento.pdf")
        
        assert ext == ".pdf"
        assert unique_name.endswith(".pdf")
        assert len(unique_name) > 10  # UUID + extensión
    
    def test_generate_unique_filename_jpg(self):
        """Test generar nombre único para JPG"""
        unique_name, ext = generate_unique_filename("foto.jpg")
        
        assert ext == ".jpg"
        assert unique_name.endswith(".jpg")
    
    def test_generate_unique_filename_png(self):
        """Test generar nombre único para PNG"""
        unique_name, ext = generate_unique_filename("imagen.PNG")
        
        assert ext == ".png"  # Debe convertir a minúsculas
        assert unique_name.endswith(".png")
    
    def test_generate_unique_filename_diferentes(self):
        """Test que nombres generados sean únicos"""
        name1, _ = generate_unique_filename("test.pdf")
        name2, _ = generate_unique_filename("test.pdf")
        
        assert name1 != name2


@pytest.mark.asyncio
class TestFileSaving:
    """Tests para guardar archivos"""
    
    async def test_save_upload_file_exitoso(self):
        """Test guardar archivo exitosamente"""
        # Crear archivo de prueba
        pdf_content = b"%PDF-1.4\n%Test content"
        upload_file = UploadFile(
            filename="test.pdf",
            file=io.BytesIO(pdf_content)
        )
        upload_file.content_type = "application/pdf"
        
        try:
            nombre_almacenado, ruta_completa, tamano = await save_upload_file(upload_file)
            
            assert nombre_almacenado.endswith(".pdf")
            assert os.path.exists(ruta_completa)
            assert tamano == len(pdf_content)
            
            # Verificar contenido
            with open(ruta_completa, 'rb') as f:
                contenido_guardado = f.read()
            assert contenido_guardado == pdf_content
        finally:
            # Limpiar
            if os.path.exists(ruta_completa):
                os.remove(ruta_completa)
    
    async def test_save_upload_file_tipo_invalido(self):
        """Test guardar archivo con tipo inválido"""
        txt_content = b"Texto plano"
        upload_file = UploadFile(
            filename="test.txt",
            file=io.BytesIO(txt_content)
        )
        upload_file.content_type = "text/plain"
        
        with pytest.raises(HTTPException) as exc_info:
            await save_upload_file(upload_file)
        
        assert exc_info.value.status_code == 400
    
    async def test_save_upload_file_tamano_excedido(self):
        """Test guardar archivo que excede tamaño máximo"""
        # Crear archivo de 11MB
        large_content = b"x" * (11 * 1024 * 1024)
        upload_file = UploadFile(
            filename="large.pdf",
            file=io.BytesIO(large_content)
        )
        upload_file.content_type = "application/pdf"
        
        with pytest.raises(HTTPException) as exc_info:
            await save_upload_file(upload_file)
        
        assert exc_info.value.status_code == 400
        assert "tamaño máximo" in exc_info.value.detail.lower()


class TestFileOperations:
    """Tests para operaciones de archivos"""
    
    def test_ensure_upload_directory(self):
        """Test asegurar que directorio de uploads existe"""
        ensure_upload_directory()
        
        assert UPLOAD_DIR.exists()
        assert UPLOAD_DIR.is_dir()
    
    def test_get_file_path(self):
        """Test obtener ruta de archivo"""
        filename = "test.pdf"
        path = get_file_path(filename)
        
        assert isinstance(path, Path)
        assert str(path).endswith("test.pdf")
    
    def test_file_exists_true(self):
        """Test verificar que archivo existe"""
        # Crear archivo temporal
        ensure_upload_directory()
        test_file = UPLOAD_DIR / "test_exists.pdf"
        test_file.write_bytes(b"test")
        
        try:
            assert file_exists("test_exists.pdf") is True
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_file_exists_false(self):
        """Test verificar que archivo no existe"""
        assert file_exists("no_existe.pdf") is False
    
    def test_delete_file_existente(self):
        """Test eliminar archivo existente"""
        # Crear archivo temporal
        ensure_upload_directory()
        test_file = UPLOAD_DIR / "test_delete.pdf"
        test_file.write_bytes(b"test")
        
        assert test_file.exists()
        
        delete_file(str(test_file))
        
        assert not test_file.exists()
    
    def test_delete_file_no_existente(self):
        """Test eliminar archivo que no existe (no debe fallar)"""
        # No debe lanzar excepción
        delete_file("/ruta/inexistente/archivo.pdf")
