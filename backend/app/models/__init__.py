"""
Modelos de base de datos
"""
from app.models.base import BaseModel
from app.models.user import Usuario, RolUsuario
from app.models.empresa import Empresa, TipoAutorizacion, AutorizacionEmpresa
from app.models.conductor import Conductor, EstadoConductor
from app.models.documento_conductor import DocumentoConductor, TipoDocumento
from app.models.habilitacion import Habilitacion, Pago, ConceptoTUPA, EstadoHabilitacion, EstadoPago
from app.models.infraccion import (
    TipoInfraccion,
    Infraccion,
    AsignacionVehiculo,
    GravedadInfraccion,
    EstadoInfraccion
)
from app.models.auditoria import Auditoria, Notificacion, AccionAuditoria, TipoNotificacion

__all__ = [
    "BaseModel",
    "Usuario",
    "RolUsuario",
    "Empresa",
    "TipoAutorizacion",
    "AutorizacionEmpresa",
    "Conductor",
    "EstadoConductor",
    "DocumentoConductor",
    "TipoDocumento",
    "Habilitacion",
    "Pago",
    "ConceptoTUPA",
    "EstadoHabilitacion",
    "EstadoPago",
    "TipoInfraccion",
    "Infraccion",
    "AsignacionVehiculo",
    "GravedadInfraccion",
    "EstadoInfraccion",
    "Auditoria",
    "Notificacion",
    "AccionAuditoria",
    "TipoNotificacion",
]
