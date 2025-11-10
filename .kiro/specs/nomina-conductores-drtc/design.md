# Documento de Diseño - Sistema de Nómina de Conductores DRTC Puno

## Visión General

El Sistema de Nómina de Conductores DRTC Puno es una aplicación web de tres capas diseñada con arquitectura moderna y escalable. El sistema utiliza Astro para el frontend, FastAPI para el backend, PostgreSQL como base de datos principal, Redis para caché y sesiones, y está completamente dockerizado para facilitar el despliegue.

### Stack Tecnológico

**Frontend:**
- Astro 4.x (SSR/SSG híbrido)
- React 18 para componentes interactivos
- TailwindCSS para estilos
- TypeScript para type safety
- Axios para comunicación con API

**Backend:**
- FastAPI 0.104+ (Python 3.11+)
- SQLAlchemy 2.0 como ORM
- Alembic para migraciones
- Pydantic v2 para validación
- JWT para autenticación
- Celery para tareas asíncronas

**Base de Datos:**
- PostgreSQL 15+ (base de datos principal)
- Redis 7+ (caché, sesiones, cola de tareas)

**Infraestructura:**
- Docker & Docker Compose
- Nginx como reverse proxy
- Gunicorn/Uvicorn para ASGI

## Arquitectura del Sistema

### Diagrama de Arquitectura

```mermaid
graph TB
    subgraph "Cliente"
        Browser[Navegador Web]
    end
    
    subgraph "Capa de Presentación"
        Nginx[Nginx Reverse Proxy]
        Frontend[Astro Frontend]
    end
    
    subgraph "Capa de Aplicación"
        API[FastAPI Backend]
        Auth[Servicio de Autenticación]
        Workers[Celery Workers]
    end
    
    subgraph "Capa de Datos"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis)]
    end
    
    subgraph "Servicios Externos"
        MTC[API MTC]
        SUNARP[API SUNARP]
        VehicleSystem[Sistema de Vehículos DRTC]
    end
    
    Browser --> Nginx
    Nginx --> Frontend
    Nginx --> API
    Frontend --> API
    API --> Auth
    API --> PostgreSQL
    API --> Redis
    API --> Workers
    Workers --> PostgreSQL
    Workers --> Redis
    API --> MTC
    API --> SUNARP
    VehicleSystem --> API
```

### Patrones de Arquitectura

1. **Arquitectura en Capas**: Separación clara entre presentación, lógica de negocio y datos
2. **Repository Pattern**: Abstracción de acceso a datos
3. **Service Layer**: Lógica de negocio encapsulada en servicios
4. **Dependency Injection**: FastAPI's Depends para gestión de dependencias
5. **CQRS Ligero**: Separación de operaciones de lectura y escritura en casos complejos

## Componentes y Módulos

### Frontend (Astro + React)

#### Estructura de Directorios
```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   ├── conductores/
│   │   ├── empresas/
│   │   ├── habilitaciones/
│   │   ├── infracciones/
│   │   ├── reportes/
│   │   └── shared/
│   ├── layouts/
│   │   ├── MainLayout.astro
│   │   ├── AuthLayout.astro
│   │   └── DashboardLayout.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── login.astro
│   │   ├── dashboard/
│   │   ├── conductores/
│   │   ├── empresas/
│   │   ├── habilitaciones/
│   │   └── reportes/
│   ├── services/
│   │   └── api.ts
│   ├── stores/
│   │   └── authStore.ts
│   └── utils/
├── public/
└── astro.config.mjs
```

#### Componentes Principales

**1. Módulo de Autenticación**
- `LoginForm.tsx`: Formulario de inicio de sesión
- `AuthGuard.tsx`: Protección de rutas según rol
- `RoleBasedAccess.tsx`: Renderizado condicional por permisos

**2. Módulo de Conductores**
- `ConductorList.tsx`: Listado con filtros y búsqueda
- `ConductorForm.tsx`: Formulario de registro/edición
- `ConductorDetail.tsx`: Vista detallada con documentos
- `ConductorStatus.tsx`: Indicador visual de estado

**3. Módulo de Empresas**
- `EmpresaList.tsx`: Listado de empresas
- `EmpresaForm.tsx`: Registro de empresa con autorizaciones
- `EmpresaDetail.tsx`: Vista con conductores asociados

**4. Módulo de Habilitaciones**
- `HabilitacionQueue.tsx`: Cola de solicitudes pendientes
- `HabilitacionReview.tsx`: Interfaz de revisión
- `HabilitacionCertificate.tsx`: Generador de certificados

**5. Módulo de Infracciones**
- `InfraccionList.tsx`: Historial de infracciones
- `InfraccionForm.tsx`: Registro de infracciones
- `InfraccionTimeline.tsx`: Línea de tiempo visual

**6. Módulo de Reportes**
- `ReportBuilder.tsx`: Constructor de reportes
- `ReportViewer.tsx`: Visualizador con gráficos
- `ReportExport.tsx`: Exportación PDF/Excel

### Backend (FastAPI)

#### Estructura de Directorios
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── conductores.py
│   │   │   │   ├── empresas.py
│   │   │   │   ├── habilitaciones.py
│   │   │   │   ├── infracciones.py
│   │   │   │   ├── pagos.py
│   │   │   │   ├── reportes.py
│   │   │   │   └── configuracion.py
│   │   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── user.py
│   │   ├── empresa.py
│   │   ├── conductor.py
│   │   ├── habilitacion.py
│   │   ├── infraccion.py
│   │   ├── pago.py
│   │   └── auditoria.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── empresa.py
│   │   ├── conductor.py
│   │   └── ...
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── conductor_service.py
│   │   ├── habilitacion_service.py
│   │   ├── infraccion_service.py
│   │   ├── integracion_service.py
│   │   └── reporte_service.py
│   ├── repositories/
│   │   ├── base.py
│   │   ├── conductor_repository.py
│   │   ├── empresa_repository.py
│   │   └── ...
│   ├── tasks/
│   │   ├── celery_app.py
│   │   ├── notificaciones.py
│   │   ├── sincronizacion.py
│   │   └── reportes.py
│   └── utils/
│       ├── validators.py
│       ├── pdf_generator.py
│       └── excel_generator.py
├── alembic/
├── tests/
└── main.py
```


## Modelo de Datos

### Diagrama Entidad-Relación

```mermaid
erDiagram
    Usuario ||--o{ Empresa : "gestiona"
    Usuario {
        uuid id PK
        string email UK
        string password_hash
        string nombres
        string apellidos
        enum rol
        boolean activo
        timestamp created_at
        timestamp updated_at
    }
    
    Empresa ||--o{ Conductor : "emplea"
    Empresa ||--o{ AutorizacionEmpresa : "tiene"
    Empresa {
        uuid id PK
        string ruc UK
        string razon_social
        string direccion
        string telefono
        string email
        uuid gerente_id FK
        boolean activo
        timestamp created_at
    }
    
    TipoAutorizacion ||--o{ AutorizacionEmpresa : "clasifica"
    TipoAutorizacion {
        uuid id PK
        string codigo UK
        string nombre
        string descripcion
        json requisitos_especiales
    }
    
    AutorizacionEmpresa {
        uuid id PK
        uuid empresa_id FK
        uuid tipo_autorizacion_id FK
        string numero_resolucion
        date fecha_emision
        date fecha_vencimiento
        boolean vigente
    }
    
    Conductor ||--o{ Habilitacion : "solicita"
    Conductor ||--o{ Infraccion : "comete"
    Conductor ||--o{ AsignacionVehiculo : "opera"
    Conductor {
        uuid id PK
        string dni UK
        string nombres
        string apellidos
        date fecha_nacimiento
        string direccion
        string telefono
        string email
        string licencia_numero
        string licencia_categoria
        date licencia_emision
        date licencia_vencimiento
        uuid empresa_id FK
        enum estado
        timestamp created_at
        timestamp updated_at
    }
    
    Habilitacion ||--|| Pago : "requiere"
    Habilitacion {
        uuid id PK
        uuid conductor_id FK
        string codigo_habilitacion UK
        enum estado
        text observaciones
        uuid revisado_por FK
        timestamp fecha_solicitud
        timestamp fecha_revision
        timestamp fecha_habilitacion
        date vigencia_hasta
    }
    
    Pago ||--|| ConceptoTUPA : "corresponde"
    Pago {
        uuid id PK
        uuid habilitacion_id FK
        uuid concepto_tupa_id FK
        string numero_recibo
        decimal monto
        date fecha_pago
        string entidad_bancaria
        enum estado
        uuid registrado_por FK
        timestamp created_at
    }
    
    ConceptoTUPA {
        uuid id PK
        string codigo UK
        string descripcion
        decimal monto
        date vigencia_desde
        date vigencia_hasta
        boolean activo
    }
    
    Infraccion ||--|| TipoInfraccion : "clasifica"
    Infraccion {
        uuid id PK
        uuid conductor_id FK
        uuid tipo_infraccion_id FK
        date fecha_infraccion
        string descripcion
        string entidad_fiscalizadora
        string numero_acta
        enum estado
        text resolucion
        uuid registrado_por FK
        timestamp created_at
    }
    
    TipoInfraccion {
        uuid id PK
        string codigo UK
        string descripcion
        enum gravedad
        integer puntos
        boolean activo
    }
    
    AsignacionVehiculo {
        uuid id PK
        uuid conductor_id FK
        string placa_vehiculo
        date fecha_asignacion
        date fecha_desasignacion
        boolean activo
        text observaciones
    }
    
    Auditoria {
        uuid id PK
        uuid usuario_id FK
        string tabla
        string accion
        json datos_anteriores
        json datos_nuevos
        string ip_address
        timestamp created_at
    }
    
    Notificacion {
        uuid id PK
        uuid usuario_id FK
        string tipo
        string asunto
        text mensaje
        boolean leida
        timestamp enviada_at
        timestamp leida_at
    }
```

### Descripción de Entidades Principales

**Usuario**
- Almacena todos los usuarios del sistema (Superusuario, Directores, Subdirectores, Operarios, Gerentes)
- El campo `rol` es un enum: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE
- Relación con Empresa para Gerentes (un gerente gestiona una empresa)

**Empresa**
- Representa empresas de transporte registradas
- Tiene múltiples autorizaciones (mercancías, turismo, etc.)
- Relación uno-a-muchos con Conductores

**Conductor**
- Información completa del conductor según normativa MTC
- Estado: PENDIENTE, HABILITADO, OBSERVADO, SUSPENDIDO, REVOCADO
- Validación de categoría de licencia según tipo de autorización de empresa

**Habilitacion**
- Proceso de aprobación de conductores
- Estados: PENDIENTE, EN_REVISION, APROBADO, OBSERVADO, RECHAZADO, HABILITADO
- Vinculado a pago TUPA

**Infraccion**
- Historial de infracciones del conductor
- Gravedad: LEVE, GRAVE, MUY_GRAVE
- Integración con sistemas externos (MTC, SUNARP)

**AsignacionVehiculo**
- Registro de qué conductor opera qué vehículo
- Permite integración con sistema de vehículos DRTC

## Interfaces y Contratos

### API REST Endpoints

#### Autenticación
```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
```

#### Usuarios
```
GET    /api/v1/usuarios
POST   /api/v1/usuarios
GET    /api/v1/usuarios/{id}
PUT    /api/v1/usuarios/{id}
DELETE /api/v1/usuarios/{id}
```

#### Empresas
```
GET    /api/v1/empresas
POST   /api/v1/empresas
GET    /api/v1/empresas/{id}
PUT    /api/v1/empresas/{id}
DELETE /api/v1/empresas/{id}
GET    /api/v1/empresas/{id}/conductores
GET    /api/v1/empresas/{id}/autorizaciones
POST   /api/v1/empresas/{id}/autorizaciones
```

#### Conductores
```
GET    /api/v1/conductores
POST   /api/v1/conductores
GET    /api/v1/conductores/{id}
PUT    /api/v1/conductores/{id}
DELETE /api/v1/conductores/{id}
GET    /api/v1/conductores/{dni}
GET    /api/v1/conductores/{dni}/habilitacion
GET    /api/v1/conductores/{dni}/infracciones
GET    /api/v1/conductores/{dni}/vehiculos-asignados
POST   /api/v1/conductores/{id}/documentos
GET    /api/v1/conductores/{id}/documentos/{doc_id}
```

#### Habilitaciones
```
GET    /api/v1/habilitaciones
GET    /api/v1/habilitaciones/pendientes
GET    /api/v1/habilitaciones/{id}
POST   /api/v1/habilitaciones/{id}/revisar
POST   /api/v1/habilitaciones/{id}/aprobar
POST   /api/v1/habilitaciones/{id}/observar
POST   /api/v1/habilitaciones/{id}/habilitar
POST   /api/v1/habilitaciones/{id}/suspender
GET    /api/v1/habilitaciones/{id}/certificado
```

#### Pagos
```
GET    /api/v1/pagos
POST   /api/v1/pagos
GET    /api/v1/pagos/{id}
PUT    /api/v1/pagos/{id}
GET    /api/v1/pagos/habilitacion/{habilitacion_id}
GET    /api/v1/pagos/{id}/orden-pago
```

#### Infracciones
```
GET    /api/v1/infracciones
POST   /api/v1/infracciones
GET    /api/v1/infracciones/{id}
PUT    /api/v1/infracciones/{id}
DELETE /api/v1/infracciones/{id}
GET    /api/v1/infracciones/conductor/{conductor_id}
POST   /api/v1/infracciones/sincronizar
```

#### Asignaciones (Integración con Sistema de Vehículos)
```
POST   /api/v1/asignaciones
GET    /api/v1/asignaciones
GET    /api/v1/asignaciones/{id}
PUT    /api/v1/asignaciones/{id}
DELETE /api/v1/asignaciones/{id}
POST   /api/v1/validar-asignacion
```

#### Reportes
```
GET    /api/v1/reportes/conductores-habilitados
GET    /api/v1/reportes/solicitudes-pendientes
GET    /api/v1/reportes/infracciones
GET    /api/v1/reportes/ingresos-tupa
POST   /api/v1/reportes/personalizado
GET    /api/v1/reportes/{id}/export/pdf
GET    /api/v1/reportes/{id}/export/excel
```

#### Configuración
```
GET    /api/v1/configuracion/tupa
PUT    /api/v1/configuracion/tupa
GET    /api/v1/configuracion/tipos-infraccion
POST   /api/v1/configuracion/tipos-infraccion
PUT    /api/v1/configuracion/tipos-infraccion/{id}
GET    /api/v1/configuracion/integraciones
PUT    /api/v1/configuracion/integraciones
```

#### Auditoría
```
GET    /api/v1/auditoria
GET    /api/v1/auditoria/usuario/{usuario_id}
GET    /api/v1/auditoria/export
```


### Schemas Pydantic (Ejemplos)

```python
# schemas/conductor.py
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
from enum import Enum

class EstadoConductor(str, Enum):
    PENDIENTE = "pendiente"
    HABILITADO = "habilitado"
    OBSERVADO = "observado"
    SUSPENDIDO = "suspendido"
    REVOCADO = "revocado"

class ConductorBase(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8)
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    fecha_nacimiento: date
    direccion: str
    telefono: str = Field(..., pattern=r'^\d{9}$')
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    licencia_numero: str
    licencia_categoria: str
    licencia_emision: date
    licencia_vencimiento: date

    @validator('licencia_vencimiento')
    def validar_licencia_vigente(cls, v, values):
        if v < date.today():
            raise ValueError('La licencia está vencida')
        return v

class ConductorCreate(ConductorBase):
    empresa_id: str

class ConductorUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

class ConductorResponse(ConductorBase):
    id: str
    empresa_id: str
    estado: EstadoConductor
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## Servicios y Lógica de Negocio

### Servicio de Habilitación

**Responsabilidades:**
- Gestionar el flujo completo de habilitación de conductores
- Validar requisitos según tipo de autorización
- Verificar pagos TUPA
- Generar certificados de habilitación
- Notificar cambios de estado

**Flujo de Habilitación:**

```mermaid
stateDiagram-v2
    [*] --> Pendiente: Gerente registra conductor
    Pendiente --> EnRevision: Operario toma solicitud
    EnRevision --> Observado: Faltan documentos
    EnRevision --> Aprobado: Documentos válidos
    Observado --> EnRevision: Gerente corrige
    Aprobado --> Habilitado: Pago confirmado
    Habilitado --> Suspendido: Infracción grave
    Habilitado --> Revocado: Decisión administrativa
    Suspendido --> Habilitado: Resolución favorable
    Revocado --> [*]
```

**Métodos Principales:**
```python
class HabilitacionService:
    async def crear_solicitud(self, conductor_id: str) -> Habilitacion
    async def revisar_solicitud(self, habilitacion_id: str, usuario_id: str) -> Habilitacion
    async def aprobar_solicitud(self, habilitacion_id: str, usuario_id: str) -> Habilitacion
    async def observar_solicitud(self, habilitacion_id: str, observaciones: str, usuario_id: str) -> Habilitacion
    async def habilitar_conductor(self, habilitacion_id: str, usuario_id: str) -> Habilitacion
    async def suspender_habilitacion(self, habilitacion_id: str, motivo: str, usuario_id: str) -> Habilitacion
    async def generar_certificado(self, habilitacion_id: str) -> bytes
    async def verificar_vigencia(self, conductor_id: str) -> bool
```

### Servicio de Integración Externa

**Responsabilidades:**
- Comunicación con APIs del MTC, SUNARP
- Validación de licencias de conducir
- Sincronización de infracciones
- Manejo de errores y reintentos

**Métodos Principales:**
```python
class IntegracionService:
    async def validar_licencia_mtc(self, licencia_numero: str) -> dict
    async def consultar_infracciones_mtc(self, dni: str) -> list
    async def consultar_antecedentes_sunarp(self, dni: str) -> dict
    async def sincronizar_infracciones(self, conductor_id: str) -> int
    async def notificar_sistema_vehiculos(self, asignacion: dict) -> bool
```

### Servicio de Reportes

**Responsabilidades:**
- Generación de reportes predefinidos y personalizados
- Exportación a PDF y Excel
- Cálculo de estadísticas
- Generación de gráficos

**Métodos Principales:**
```python
class ReporteService:
    async def generar_reporte_conductores_habilitados(self, filtros: dict) -> dict
    async def generar_reporte_infracciones(self, fecha_inicio: date, fecha_fin: date) -> dict
    async def generar_reporte_ingresos_tupa(self, periodo: str) -> dict
    async def exportar_pdf(self, reporte_id: str) -> bytes
    async def exportar_excel(self, reporte_id: str) -> bytes
    async def calcular_estadisticas_dashboard(self, usuario_id: str) -> dict
```

### Servicio de Notificaciones

**Responsabilidades:**
- Envío de notificaciones por email
- Notificaciones en aplicación
- Gestión de plantillas
- Cola de envío con Celery

**Métodos Principales:**
```python
class NotificacionService:
    async def notificar_solicitud_observada(self, habilitacion_id: str) -> None
    async def notificar_conductor_habilitado(self, habilitacion_id: str) -> None
    async def notificar_licencia_proxima_vencer(self, conductor_id: str) -> None
    async def notificar_infraccion_grave(self, infraccion_id: str) -> None
    async def enviar_email(self, destinatario: str, asunto: str, contenido: str) -> bool
```

## Seguridad

### Autenticación y Autorización

**JWT (JSON Web Tokens):**
- Access Token: 30 minutos de validez
- Refresh Token: 7 días de validez
- Almacenamiento en httpOnly cookies
- Rotación de refresh tokens

**Estructura del Token:**
```json
{
  "sub": "user_id",
  "email": "usuario@example.com",
  "rol": "DIRECTOR",
  "empresa_id": "empresa_id_si_aplica",
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Control de Acceso Basado en Roles (RBAC):**

| Rol | Permisos |
|-----|----------|
| SUPERUSUARIO | Acceso completo, configuración del sistema |
| DIRECTOR | Visualización completa, habilitación, cambios importantes, reportes globales |
| SUBDIRECTOR | Similar a Director con restricciones en configuración |
| OPERARIO | Procesamiento de solicitudes, validación, sin autorización para cambios críticos |
| GERENTE | Solo gestión de conductores de su empresa |

**Implementación:**
```python
# core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Usuario:
    token = credentials.credentials
    payload = verify_token(token)
    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no válido")
    return user

def require_roles(allowed_roles: list[str]):
    def decorator(func):
        async def wrapper(*args, user: Usuario = Depends(get_current_user), **kwargs):
            if user.rol not in allowed_roles:
                raise HTTPException(status_code=403, detail="Acceso denegado")
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

# Uso en endpoints
@router.post("/habilitaciones/{id}/habilitar")
@require_roles(["SUPERUSUARIO", "DIRECTOR", "SUBDIRECTOR"])
async def habilitar_conductor(id: str, user: Usuario = Depends(get_current_user)):
    ...
```

### Validación de Datos

- Validación en frontend con formularios React
- Validación en backend con Pydantic schemas
- Sanitización de inputs para prevenir SQL injection
- Validación de tipos de archivo en uploads
- Límites de tamaño en archivos adjuntos (10MB)

### Protección contra Ataques

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginSchema):
    ...
```

**CORS:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://drtc-puno.gob.pe"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Encriptación:**
- Contraseñas hasheadas con bcrypt (cost factor 12)
- Datos sensibles encriptados en base de datos
- Comunicación HTTPS obligatoria en producción
- Variables de entorno para secrets


## Manejo de Errores

### Estrategia de Manejo de Errores

**Jerarquía de Excepciones Personalizadas:**
```python
# core/exceptions.py
class DRTCException(Exception):
    """Excepción base del sistema"""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)

class RecursoNoEncontrado(DRTCException):
    def __init__(self, recurso: str, id: str):
        super().__init__(
            message=f"{recurso} con id {id} no encontrado",
            code="RECURSO_NO_ENCONTRADO"
        )

class PermisosDenegados(DRTCException):
    def __init__(self, accion: str):
        super().__init__(
            message=f"No tiene permisos para {accion}",
            code="PERMISOS_DENEGADOS"
        )

class ValidacionError(DRTCException):
    def __init__(self, campo: str, mensaje: str):
        super().__init__(
            message=f"Error de validación en {campo}: {mensaje}",
            code="VALIDACION_ERROR"
        )

class IntegracionExternaError(DRTCException):
    def __init__(self, servicio: str, detalle: str):
        super().__init__(
            message=f"Error al comunicarse con {servicio}: {detalle}",
            code="INTEGRACION_ERROR"
        )
```

**Handler Global de Excepciones:**
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(DRTCException)
async def drtc_exception_handler(request: Request, exc: DRTCException):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log del error
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "ERROR_INTERNO",
                "message": "Ha ocurrido un error interno. Por favor contacte al administrador.",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

### Códigos de Error Estándar

| Código HTTP | Código Interno | Descripción |
|-------------|----------------|-------------|
| 400 | VALIDACION_ERROR | Error en validación de datos |
| 401 | NO_AUTENTICADO | Usuario no autenticado |
| 403 | PERMISOS_DENEGADOS | Usuario sin permisos |
| 404 | RECURSO_NO_ENCONTRADO | Recurso no existe |
| 409 | CONFLICTO | Conflicto con estado actual |
| 422 | DATOS_INVALIDOS | Datos no procesables |
| 429 | LIMITE_EXCEDIDO | Rate limit excedido |
| 500 | ERROR_INTERNO | Error interno del servidor |
| 502 | INTEGRACION_ERROR | Error en servicio externo |
| 503 | SERVICIO_NO_DISPONIBLE | Servicio temporalmente no disponible |

### Logging

**Configuración de Logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Configuración
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Niveles de log
# DEBUG: Información detallada para diagnóstico
# INFO: Confirmación de operaciones normales
# WARNING: Algo inesperado pero el sistema continúa
# ERROR: Error que impide una función específica
# CRITICAL: Error grave que puede detener el sistema
```

## Estrategia de Testing

### Pirámide de Testing

```
        /\
       /  \
      / E2E \
     /--------\
    /          \
   / Integration \
  /--------------\
 /                \
/   Unit Tests     \
--------------------
```

### Tests Unitarios (70%)

**Backend:**
```python
# tests/services/test_habilitacion_service.py
import pytest
from app.services.habilitacion_service import HabilitacionService
from app.models.habilitacion import EstadoHabilitacion

@pytest.mark.asyncio
async def test_crear_solicitud_habilitacion(db_session, conductor_factory):
    # Arrange
    conductor = await conductor_factory.create()
    service = HabilitacionService(db_session)
    
    # Act
    habilitacion = await service.crear_solicitud(conductor.id)
    
    # Assert
    assert habilitacion.conductor_id == conductor.id
    assert habilitacion.estado == EstadoHabilitacion.PENDIENTE
    assert habilitacion.codigo_habilitacion is not None

@pytest.mark.asyncio
async def test_habilitar_sin_pago_debe_fallar(db_session, habilitacion_factory):
    # Arrange
    habilitacion = await habilitacion_factory.create(estado=EstadoHabilitacion.APROBADO)
    service = HabilitacionService(db_session)
    
    # Act & Assert
    with pytest.raises(ValidacionError) as exc:
        await service.habilitar_conductor(habilitacion.id, "user_id")
    
    assert "pago no confirmado" in str(exc.value).lower()
```

**Frontend:**
```typescript
// tests/components/ConductorForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ConductorForm } from '@/components/conductores/ConductorForm';

describe('ConductorForm', () => {
  it('debe validar DNI de 8 dígitos', async () => {
    render(<ConductorForm />);
    
    const dniInput = screen.getByLabelText('DNI');
    fireEvent.change(dniInput, { target: { value: '123' } });
    fireEvent.blur(dniInput);
    
    await waitFor(() => {
      expect(screen.getByText('DNI debe tener 8 dígitos')).toBeInTheDocument();
    });
  });
  
  it('debe validar que licencia no esté vencida', async () => {
    render(<ConductorForm />);
    
    const fechaVencimiento = screen.getByLabelText('Fecha Vencimiento Licencia');
    const fechaPasada = new Date();
    fechaPasada.setFullYear(fechaPasada.getFullYear() - 1);
    
    fireEvent.change(fechaVencimiento, { target: { value: fechaPasada.toISOString().split('T')[0] } });
    fireEvent.blur(fechaVencimiento);
    
    await waitFor(() => {
      expect(screen.getByText('La licencia está vencida')).toBeInTheDocument();
    });
  });
});
```

### Tests de Integración (20%)

```python
# tests/integration/test_habilitacion_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_flujo_completo_habilitacion(client: AsyncClient, auth_headers):
    # 1. Crear empresa
    empresa_data = {
        "ruc": "20123456789",
        "razon_social": "Transportes Test SAC",
        "direccion": "Av. Test 123",
        "telefono": "987654321",
        "email": "test@transportes.com"
    }
    response = await client.post("/api/v1/empresas", json=empresa_data, headers=auth_headers)
    assert response.status_code == 201
    empresa_id = response.json()["id"]
    
    # 2. Crear conductor
    conductor_data = {
        "dni": "12345678",
        "nombres": "Juan",
        "apellidos": "Pérez",
        "fecha_nacimiento": "1990-01-01",
        "direccion": "Jr. Test 456",
        "telefono": "987654321",
        "email": "juan@example.com",
        "licencia_numero": "Q12345678",
        "licencia_categoria": "A-IIIb",
        "licencia_emision": "2023-01-01",
        "licencia_vencimiento": "2028-01-01",
        "empresa_id": empresa_id
    }
    response = await client.post("/api/v1/conductores", json=conductor_data, headers=auth_headers)
    assert response.status_code == 201
    conductor_id = response.json()["id"]
    
    # 3. Verificar que se creó solicitud de habilitación
    response = await client.get(f"/api/v1/habilitaciones?conductor_id={conductor_id}", headers=auth_headers)
    assert response.status_code == 200
    habilitaciones = response.json()
    assert len(habilitaciones) == 1
    assert habilitaciones[0]["estado"] == "pendiente"
```

### Tests E2E (10%)

```typescript
// e2e/habilitacion.spec.ts
import { test, expect } from '@playwright/test';

test('flujo completo de habilitación de conductor', async ({ page }) => {
  // Login como gerente
  await page.goto('/login');
  await page.fill('[name="email"]', 'gerente@empresa.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Registrar conductor
  await page.goto('/conductores/nuevo');
  await page.fill('[name="dni"]', '12345678');
  await page.fill('[name="nombres"]', 'Juan');
  await page.fill('[name="apellidos"]', 'Pérez');
  // ... llenar resto de campos
  await page.click('button[type="submit"]');
  
  // Verificar mensaje de éxito
  await expect(page.locator('.success-message')).toContainText('Conductor registrado exitosamente');
  
  // Login como operario
  await page.goto('/logout');
  await page.goto('/login');
  await page.fill('[name="email"]', 'operario@drtc.gob.pe');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // Revisar solicitud
  await page.goto('/habilitaciones/pendientes');
  await page.click('text=Juan Pérez');
  await page.click('button:has-text("Aprobar")');
  
  // Verificar estado
  await expect(page.locator('.estado-badge')).toContainText('Aprobado');
});
```


## Configuración Docker

### Estructura de Contenedores

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Base de datos PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: drtc-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - drtc-network

  # Redis para caché y colas
  redis:
    image: redis:7-alpine
    container_name: drtc-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - drtc-network

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: drtc-backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: ${ENVIRONMENT}
    volumes:
      - ./backend:/app
      - backend_uploads:/app/uploads
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - drtc-network

  # Celery Worker para tareas asíncronas
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: drtc-celery-worker
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    command: celery -A app.tasks.celery_app worker --loglevel=info
    networks:
      - drtc-network

  # Celery Beat para tareas programadas
  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: drtc-celery-beat
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    command: celery -A app.tasks.celery_app beat --loglevel=info
    networks:
      - drtc-network

  # Frontend Astro
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: drtc-frontend
    environment:
      PUBLIC_API_URL: ${PUBLIC_API_URL}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "4321:4321"
    depends_on:
      - backend
    command: npm run dev -- --host
    networks:
      - drtc-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: drtc-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    networks:
      - drtc-network

volumes:
  postgres_data:
  redis_data:
  backend_uploads:

networks:
  drtc-network:
    driver: bridge
```

### Dockerfile Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorio para uploads
RUN mkdir -p /app/uploads

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile Frontend

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 4321

# Comando por defecto
CMD ["npm", "run", "dev", "--", "--host"]
```

### Configuración Nginx

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:4321;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

    server {
        listen 80;
        server_name localhost;

        # Redirigir a HTTPS en producción
        # return 301 https://$server_name$request_uri;

        client_max_body_size 10M;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API Backend
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        }

        # Login endpoint con rate limiting más estricto
        location /api/v1/auth/login {
            limit_req zone=login_limit burst=3 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Documentación API
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }
    }

    # Configuración HTTPS (producción)
    # server {
    #     listen 443 ssl http2;
    #     server_name drtc-puno.gob.pe;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     # ... resto de configuración
    # }
}
```

### Variables de Entorno

```bash
# .env.example
# Base de datos
POSTGRES_DB=drtc_nomina
POSTGRES_USER=drtc_user
POSTGRES_PASSWORD=secure_password_here

# Backend
SECRET_KEY=your-secret-key-here-min-32-chars
ENVIRONMENT=development
DATABASE_URL=postgresql://drtc_user:secure_password_here@postgres:5432/drtc_nomina
REDIS_URL=redis://redis:6379/0

# Frontend
PUBLIC_API_URL=http://localhost/api

# Integraciones externas
MTC_API_URL=https://api.mtc.gob.pe
MTC_API_KEY=your-mtc-api-key
SUNARP_API_URL=https://api.sunarp.gob.pe
SUNARP_API_KEY=your-sunarp-api-key

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notificaciones@drtc-puno.gob.pe
SMTP_PASSWORD=your-email-password
SMTP_FROM=notificaciones@drtc-puno.gob.pe

# Configuración de archivos
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf,jpg,jpeg,png

# Seguridad
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
```

## Performance y Optimización

### Estrategias de Caché

**Redis para Caché de Consultas:**
```python
from redis import asyncio as aioredis
import json

class CacheService:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: any, expire: int = 300):
        await self.redis.setex(key, expire, json.dumps(value))
    
    async def delete(self, key: str):
        await self.redis.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# Uso en servicios
async def get_conductor_by_id(conductor_id: str, cache: CacheService):
    cache_key = f"conductor:{conductor_id}"
    
    # Intentar obtener de caché
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Si no está en caché, consultar BD
    conductor = await db.query(Conductor).filter(Conductor.id == conductor_id).first()
    
    # Guardar en caché por 5 minutos
    await cache.set(cache_key, conductor.dict(), expire=300)
    
    return conductor
```

### Paginación y Filtrado

```python
from fastapi import Query
from typing import Optional

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size

@router.get("/conductores")
async def listar_conductores(
    pagination: PaginationParams = Depends(),
    empresa_id: Optional[str] = None,
    estado: Optional[str] = None,
    search: Optional[str] = None
):
    query = db.query(Conductor)
    
    # Aplicar filtros
    if empresa_id:
        query = query.filter(Conductor.empresa_id == empresa_id)
    if estado:
        query = query.filter(Conductor.estado == estado)
    if search:
        query = query.filter(
            or_(
                Conductor.nombres.ilike(f"%{search}%"),
                Conductor.apellidos.ilike(f"%{search}%"),
                Conductor.dni.ilike(f"%{search}%")
            )
        )
    
    # Contar total
    total = await query.count()
    
    # Aplicar paginación
    conductores = await query.offset(pagination.skip).limit(pagination.page_size).all()
    
    return {
        "items": conductores,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size
    }
```

### Índices de Base de Datos

```python
# models/conductor.py
from sqlalchemy import Index

class Conductor(Base):
    __tablename__ = "conductores"
    
    # ... campos
    
    __table_args__ = (
        Index('idx_conductor_dni', 'dni'),
        Index('idx_conductor_empresa', 'empresa_id'),
        Index('idx_conductor_estado', 'estado'),
        Index('idx_conductor_licencia', 'licencia_numero'),
        Index('idx_conductor_search', 'nombres', 'apellidos', postgresql_using='gin'),
    )
```

### Tareas Asíncronas con Celery

```python
# tasks/sincronizacion.py
from celery import shared_task
from app.services.integracion_service import IntegracionService

@shared_task
def sincronizar_infracciones_mtc():
    """Tarea programada para sincronizar infracciones desde MTC"""
    service = IntegracionService()
    conductores_habilitados = get_conductores_habilitados()
    
    for conductor in conductores_habilitados:
        try:
            infracciones = service.consultar_infracciones_mtc(conductor.dni)
            for infraccion in infracciones:
                registrar_infraccion(conductor.id, infraccion)
        except Exception as e:
            logger.error(f"Error sincronizando conductor {conductor.dni}: {str(e)}")

@shared_task
def notificar_licencias_por_vencer():
    """Notificar conductores con licencias próximas a vencer"""
    fecha_limite = date.today() + timedelta(days=30)
    conductores = get_conductores_licencia_vence_antes(fecha_limite)
    
    for conductor in conductores:
        enviar_notificacion_vencimiento(conductor)

# Configuración de tareas programadas
from celery.schedules import crontab

app.conf.beat_schedule = {
    'sincronizar-infracciones-diario': {
        'task': 'tasks.sincronizacion.sincronizar_infracciones_mtc',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM diario
    },
    'notificar-licencias-semanal': {
        'task': 'tasks.sincronizacion.notificar_licencias_por_vencer',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Lunes 8:00 AM
    },
}
```

## Monitoreo y Observabilidad

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    checks = {
        "database": await check_database(db),
        "redis": await check_redis(),
        "external_apis": await check_external_apis()
    }
    
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Métricas

```python
from prometheus_client import Counter, Histogram, generate_latest

# Contadores
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
habilitaciones_count = Counter('habilitaciones_total', 'Total habilitaciones', ['estado'])

# Histogramas
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Decisiones de Diseño y Justificaciones

### 1. FastAPI vs Django

**Decisión:** FastAPI

**Justificación:**
- Performance superior (async/await nativo)
- Documentación automática con OpenAPI
- Validación de datos con Pydantic
- Mejor para APIs REST modernas
- Type hints nativos de Python

### 2. PostgreSQL vs MongoDB

**Decisión:** PostgreSQL

**Justificación:**
- Datos altamente relacionales (conductores, empresas, habilitaciones)
- Integridad referencial crítica
- Transacciones ACID necesarias
- Consultas complejas con JOINs
- Madurez y soporte en sector gubernamental

### 3. Astro vs Next.js/Nuxt

**Decisión:** Astro

**Justificación:**
- Mejor performance (menos JavaScript al cliente)
- SSR/SSG híbrido flexible
- Integración con múltiples frameworks (React, Vue, Svelte)
- Ideal para aplicaciones con mucho contenido estático
- Menor complejidad que frameworks full-stack

### 4. Monolito vs Microservicios

**Decisión:** Monolito modular

**Justificación:**
- Menor complejidad operacional
- Más fácil de desarrollar y mantener inicialmente
- Suficiente para escala esperada
- Posibilidad de migrar a microservicios si es necesario
- Mejor para equipos pequeños

