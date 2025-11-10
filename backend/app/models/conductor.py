"""
Modelo de Conductor
"""
import enum
from datetime import date
from sqlalchemy import Column, String, Date, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class EstadoConductor(str, enum.Enum):
    """Estados del conductor en el sistema"""
    PENDIENTE = "pendiente"
    HABILITADO = "habilitado"
    OBSERVADO = "observado"
    SUSPENDIDO = "suspendido"
    REVOCADO = "revocado"


class Conductor(BaseModel):
    """Modelo de Conductor"""
    
    __tablename__ = "conductores"
    
    # Datos personales
    dni = Column(
        String(8),
        unique=True,
        nullable=False,
        index=True
    )
    
    nombres = Column(
        String(100),
        nullable=False
    )
    
    apellidos = Column(
        String(100),
        nullable=False
    )
    
    fecha_nacimiento = Column(
        Date,
        nullable=False
    )
    
    direccion = Column(
        String(500),
        nullable=False
    )
    
    telefono = Column(
        String(20),
        nullable=False
    )
    
    email = Column(
        String(255),
        nullable=False
    )
    
    # Datos de licencia
    licencia_numero = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    
    licencia_categoria = Column(
        String(10),
        nullable=False,
        comment="Categoría de licencia (A-I, A-IIa, A-IIb, A-IIIa, A-IIIb, A-IIIc)"
    )
    
    licencia_emision = Column(
        Date,
        nullable=False
    )
    
    licencia_vencimiento = Column(
        Date,
        nullable=False,
        index=True
    )
    
    # Certificado médico
    certificado_medico_numero = Column(
        String(50),
        nullable=True
    )
    
    certificado_medico_vencimiento = Column(
        Date,
        nullable=True,
        index=True
    )
    
    # Relación con empresa
    empresa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Estado del conductor
    estado = Column(
        SQLEnum(EstadoConductor),
        default=EstadoConductor.PENDIENTE,
        nullable=False,
        index=True
    )
    
    # Observaciones
    observaciones = Column(
        String(1000),
        nullable=True,
        comment="Observaciones sobre el conductor"
    )
    
    # Relaciones
    empresa = relationship(
        "Empresa",
        back_populates="conductores"
    )
    
    habilitaciones = relationship(
        "Habilitacion",
        back_populates="conductor",
        cascade="all, delete-orphan"
    )
    
    infracciones = relationship(
        "Infraccion",
        back_populates="conductor",
        cascade="all, delete-orphan"
    )
    
    asignaciones_vehiculo = relationship(
        "AsignacionVehiculo",
        back_populates="conductor",
        cascade="all, delete-orphan"
    )
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_conductor_dni_estado', 'dni', 'estado'),
        Index('idx_conductor_empresa_estado', 'empresa_id', 'estado'),
        Index('idx_conductor_licencia_estado', 'licencia_numero', 'estado'),
        Index('idx_conductor_vencimientos', 'licencia_vencimiento', 'certificado_medico_vencimiento'),
    )
    
    def __repr__(self):
        return f"<Conductor {self.dni} - {self.nombre_completo}>"
    
    # Validaciones
    
    @validates('dni')
    def validate_dni(self, key, dni):
        """Valida que el DNI tenga 8 dígitos"""
        if dni and (len(dni) != 8 or not dni.isdigit()):
            raise ValueError("DNI debe tener exactamente 8 dígitos numéricos")
        return dni
    
    @validates('licencia_numero')
    def validate_licencia_numero(self, key, licencia):
        """Valida formato de número de licencia"""
        if licencia and len(licencia) < 5:
            raise ValueError("Número de licencia inválido")
        return licencia
    
    @validates('licencia_categoria')
    def validate_licencia_categoria(self, key, categoria):
        """Valida que la categoría de licencia sea válida"""
        categorias_validas = [
            'A-I', 'A-IIa', 'A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'
        ]
        if categoria and categoria not in categorias_validas:
            raise ValueError(f"Categoría de licencia inválida. Debe ser una de: {', '.join(categorias_validas)}")
        return categoria
    
    @validates('licencia_vencimiento')
    def validate_licencia_vencimiento(self, key, fecha_vencimiento):
        """Valida que la licencia no esté vencida"""
        if fecha_vencimiento and fecha_vencimiento < date.today():
            raise ValueError("La licencia de conducir está vencida")
        return fecha_vencimiento
    
    @validates('email')
    def validate_email(self, key, email):
        """Validación básica de email"""
        if email and '@' not in email:
            raise ValueError("Email inválido")
        return email
    
    # Propiedades
    
    @property
    def nombre_completo(self) -> str:
        """Retorna nombre completo del conductor"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def licencia_vigente(self) -> bool:
        """Verifica si la licencia está vigente"""
        return self.licencia_vencimiento >= date.today()
    
    @property
    def certificado_medico_vigente(self) -> bool:
        """Verifica si el certificado médico está vigente"""
        if self.certificado_medico_vencimiento is None:
            return False
        return self.certificado_medico_vencimiento >= date.today()
    
    @property
    def edad(self) -> int:
        """Calcula la edad del conductor"""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def puede_operar(self) -> bool:
        """Verifica si el conductor puede operar (habilitado y documentos vigentes)"""
        return (
            self.estado == EstadoConductor.HABILITADO and
            self.licencia_vigente and
            self.certificado_medico_vigente
        )
    
    # Métodos
    
    def validar_categoria_para_tipo_autorizacion(self, tipo_autorizacion_codigo: str) -> bool:
        """
        Valida si la categoría de licencia es apropiada para el tipo de autorización
        
        Args:
            tipo_autorizacion_codigo: Código del tipo de autorización (MERCANCIAS, TURISMO, etc.)
        
        Returns:
            bool: True si la categoría es válida para el tipo de autorización
        """
        # Mapeo de tipos de autorización a categorías mínimas requeridas
        requisitos = {
            'MERCANCIAS': ['A-IIIb', 'A-IIIc'],
            'TURISMO': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'TRABAJADORES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESPECIALES': ['A-IIIa', 'A-IIIb', 'A-IIIc'],
            'ESTUDIANTES': ['A-IIb', 'A-IIIa', 'A-IIIb', 'A-IIIc'],
            'RESIDUOS_PELIGROSOS': ['A-IIIb', 'A-IIIc'],
        }
        
        categorias_requeridas = requisitos.get(tipo_autorizacion_codigo, [])
        return self.licencia_categoria in categorias_requeridas
    
    def dias_hasta_vencimiento_licencia(self) -> int:
        """Retorna días hasta el vencimiento de la licencia"""
        return (self.licencia_vencimiento - date.today()).days
    
    def dias_hasta_vencimiento_certificado(self) -> int:
        """Retorna días hasta el vencimiento del certificado médico"""
        if self.certificado_medico_vencimiento is None:
            return 0
        return (self.certificado_medico_vencimiento - date.today()).days
    
    def requiere_renovacion_documentos(self, dias_anticipacion: int = 30) -> dict:
        """
        Verifica si el conductor requiere renovar documentos
        
        Args:
            dias_anticipacion: Días de anticipación para alertar
        
        Returns:
            dict: Diccionario con alertas de renovación
        """
        alertas = {
            'licencia': False,
            'certificado_medico': False,
            'dias_licencia': self.dias_hasta_vencimiento_licencia(),
            'dias_certificado': self.dias_hasta_vencimiento_certificado()
        }
        
        if alertas['dias_licencia'] <= dias_anticipacion:
            alertas['licencia'] = True
        
        if alertas['dias_certificado'] <= dias_anticipacion:
            alertas['certificado_medico'] = True
        
        return alertas
    
    def cambiar_estado(self, nuevo_estado: EstadoConductor, observacion: str = None) -> None:
        """
        Cambia el estado del conductor
        
        Args:
            nuevo_estado: Nuevo estado del conductor
            observacion: Observación sobre el cambio de estado
        """
        self.estado = nuevo_estado
        if observacion:
            if self.observaciones:
                self.observaciones += f"\n{date.today()}: {observacion}"
            else:
                self.observaciones = f"{date.today()}: {observacion}"
