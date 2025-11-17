"""
Utilidades para manejo de archivos
"""
import os
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status


# Configuración
UPLOAD_DIR = Path("uploads/conductores")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB en bytes
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/jpg',
    'image/png'
}


def ensure_upload_directory():
    """Asegura que el directorio de uploads exista"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_file_type(filename: str, content_type: str) -> None:
    """
    Valida que el tipo de archivo sea permitido
    
    Args:
        filename: Nombre del archivo
        content_type: Tipo MIME del archivo
    
    Raises:
        HTTPException: Si el tipo de archivo no es permitido
    """
    # Validar extensión
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validar MIME type
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo MIME no permitido. Tipos permitidos: {', '.join(ALLOWED_MIME_TYPES)}"
        )


def validate_file_size(file_size: int) -> None:
    """
    Valida que el tamaño del archivo no exceda el límite
    
    Args:
        file_size: Tamaño del archivo en bytes
    
    Raises:
        HTTPException: Si el archivo excede el tamaño máximo
    """
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo permitido de {max_size_mb}MB"
        )


def generate_unique_filename(original_filename: str) -> Tuple[str, str]:
    """
    Genera un nombre único para el archivo
    
    Args:
        original_filename: Nombre original del archivo
    
    Returns:
        Tuple[str, str]: (nombre_unico, extensión)
    """
    file_ext = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{file_ext}"
    return unique_name, file_ext


async def save_upload_file(upload_file: UploadFile) -> Tuple[str, str, int]:
    """
    Guarda un archivo subido
    
    Args:
        upload_file: Archivo subido
    
    Returns:
        Tuple[str, str, int]: (nombre_almacenado, ruta_completa, tamaño_bytes)
    
    Raises:
        HTTPException: Si hay error al guardar el archivo
    """
    try:
        # Asegurar que el directorio existe
        ensure_upload_directory()
        
        # Leer contenido del archivo
        contents = await upload_file.read()
        file_size = len(contents)
        
        # Validar tamaño
        validate_file_size(file_size)
        
        # Validar tipo
        validate_file_type(upload_file.filename, upload_file.content_type)
        
        # Generar nombre único
        unique_filename, _ = generate_unique_filename(upload_file.filename)
        
        # Ruta completa
        file_path = UPLOAD_DIR / unique_filename
        
        # Guardar archivo
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        return unique_filename, str(file_path), file_size
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo: {str(e)}"
        )
    finally:
        await upload_file.close()


def delete_file(file_path: str) -> None:
    """
    Elimina un archivo del sistema
    
    Args:
        file_path: Ruta del archivo a eliminar
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error pero no lanzar excepción
        print(f"Error al eliminar archivo {file_path}: {str(e)}")


def get_file_path(filename: str) -> Path:
    """
    Obtiene la ruta completa de un archivo
    
    Args:
        filename: Nombre del archivo
    
    Returns:
        Path: Ruta completa del archivo
    """
    return UPLOAD_DIR / filename


def file_exists(filename: str) -> bool:
    """
    Verifica si un archivo existe
    
    Args:
        filename: Nombre del archivo
    
    Returns:
        bool: True si el archivo existe
    """
    return get_file_path(filename).exists()
