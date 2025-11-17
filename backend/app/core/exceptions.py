"""
Excepciones personalizadas del sistema
"""


class DRTCException(Exception):
    """Excepción base del sistema"""
    
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


class RecursoNoEncontrado(DRTCException):
    """Excepción cuando un recurso no es encontrado"""
    
    def __init__(self, recurso: str, id: str):
        super().__init__(
            message=f"{recurso} con id {id} no encontrado",
            code="RECURSO_NO_ENCONTRADO"
        )
        self.recurso = recurso
        self.id = id


class PermisosDenegados(DRTCException):
    """Excepción cuando el usuario no tiene permisos"""
    
    def __init__(self, accion: str):
        super().__init__(
            message=f"No tiene permisos para {accion}",
            code="PERMISOS_DENEGADOS"
        )
        self.accion = accion


class ValidacionError(DRTCException):
    """Excepción de validación de datos"""
    
    def __init__(self, campo: str, mensaje: str):
        super().__init__(
            message=f"Error de validación en {campo}: {mensaje}",
            code="VALIDACION_ERROR"
        )
        self.campo = campo


class IntegracionExternaError(DRTCException):
    """Excepción de error en integración externa"""
    
    def __init__(self, servicio: str, detalle: str):
        super().__init__(
            message=f"Error al comunicarse con {servicio}: {detalle}",
            code="INTEGRACION_ERROR"
        )
        self.servicio = servicio
        self.detalle = detalle


class ConflictoError(DRTCException):
    """Excepción cuando hay un conflicto con el estado actual"""
    
    def __init__(self, mensaje: str):
        super().__init__(
            message=mensaje,
            code="CONFLICTO"
        )
