"""
Repositorios para acceso a datos
"""
from app.repositories.base import BaseRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.empresa_repository import EmpresaRepository
from app.repositories.conductor_repository import ConductorRepository
from app.repositories.habilitacion_repository import HabilitacionRepository
from app.repositories.infraccion_repository import InfraccionRepository

__all__ = [
    "BaseRepository",
    "UsuarioRepository",
    "EmpresaRepository",
    "ConductorRepository",
    "HabilitacionRepository",
    "InfraccionRepository",
]
