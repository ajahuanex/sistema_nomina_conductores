# Mejoras para Módulo de Empresas y Control de Acceso de Gerentes

## Estado Actual

### Modelos Existentes
- ✅ `Empresa` - Modelo completo con autorizaciones
- ✅ `TipoAutorizacion` - Tipos de autorización (Turismo, Autocolectivo, etc.)
- ✅ `AutorizacionEmpresa` - Relación muchos-a-muchos entre Empresa y TipoAutorizacion
- ✅ `Usuario` - Tiene campo `empresa_id` pero sin relación definida
- ✅ `RolUsuario.GERENTE` - Rol ya existe

### Funcionalidades Implementadas
- ✅ CRUD básico de empresas
- ✅ Modelo de autorizaciones
- ✅ Validación de RUC

## Mejoras Necesarias

### 1. Corregir Relación Usuario-Empresa
**Problema**: El modelo Usuario tiene `empresa_id` pero no está relacionado correctamente con Empresa.

**Solución**:
- Agregar relación bidireccional entre Usuario y Empresa
- Un gerente puede gestionar UNA empresa
- Una empresa puede tener UN gerente

### 2. Implementar Control de Acceso para Gerentes

#### Reglas de Negocio:
1. **Gerente puede**:
   - Ver solo conductores de SU empresa
   - Crear conductores para SU empresa
   - Editar conductores de SU empresa
   - Ver habilitaciones de conductores de SU empresa
   - Registrar pagos para habilitaciones de SU empresa
   - Ver reportes de SU empresa

2. **Gerente NO puede**:
   - Ver/editar conductores de otras empresas
   - Ver/editar información de otras empresas
   - Acceder a funciones administrativas del sistema

#### Implementación:
- Crear middleware/dependency para filtrar por empresa del gerente
- Modificar servicios para aplicar filtros automáticos
- Actualizar endpoints para validar permisos

### 3. Gestión de Autorizaciones de Empresa

#### Funcionalidades:
- CRUD de tipos de autorización (solo admin)
- Asignar/revocar autorizaciones a empresas
- Validar que conductores solo trabajen en empresas con autorizaciones vigentes
- Alertas de vencimiento de autorizaciones

### 4. Endpoints Necesarios

#### Autorizaciones
- `GET /api/v1/autorizaciones/tipos` - Listar tipos de autorización
- `POST /api/v1/autorizaciones/tipos` - Crear tipo (admin)
- `GET /api/v1/empresas/{id}/autorizaciones` - Listar autorizaciones de empresa
- `POST /api/v1/empresas/{id}/autorizaciones` - Asignar autorización
- `PUT /api/v1/empresas/{id}/autorizaciones/{auth_id}` - Actualizar autorización
- `DELETE /api/v1/empresas/{id}/autorizaciones/{auth_id}` - Revocar autorización

#### Empresas (con filtro para gerentes)
- `GET /api/v1/empresas/mi-empresa` - Gerente obtiene su empresa
- `GET /api/v1/empresas/{id}/conductores` - Conductores de la empresa (filtrado)
- `GET /api/v1/empresas/{id}/estadisticas` - Estadísticas de la empresa

### 5. Servicios a Modificar

#### EmpresaService
- Agregar métodos para gestión de autorizaciones
- Agregar validaciones de permisos por rol
- Implementar filtros automáticos para gerentes

#### ConductorService
- Modificar `get_all` para filtrar por empresa si es gerente
- Validar que gerente solo cree conductores en su empresa
- Validar autorizaciones vigentes al crear conductor

#### HabilitacionService
- Filtrar habilitaciones por empresa del gerente
- Validar permisos al aprobar/rechazar

#### UsuarioService
- Validar que al asignar rol GERENTE se asigne empresa_id
- Validar que empresa_id solo se use con rol GERENTE

## Prioridades de Implementación

### Alta Prioridad
1. ✅ Corregir relación Usuario-Empresa en modelos
2. ✅ Implementar filtros en ConductorService para gerentes
3. ✅ Crear dependency `get_empresa_gerente` para validar acceso
4. ✅ Modificar endpoints de conductores para aplicar filtros

### Media Prioridad
5. Implementar CRUD completo de autorizaciones
6. Agregar validaciones de autorizaciones en creación de conductores
7. Crear endpoints específicos para gerentes

### Baja Prioridad
8. Dashboard específico para gerentes
9. Reportes por empresa
10. Alertas de vencimiento de autorizaciones

## Ejemplo de Uso

### Gerente accede al sistema
```python
# El gerente inicia sesión
POST /api/v1/auth/login
{
  "email": "gerente@empresa.com",
  "password": "***"
}

# Obtiene su empresa
GET /api/v1/empresas/mi-empresa
Response: {
  "id": "uuid",
  "razon_social": "Transportes ABC",
  "autorizaciones": [
    {
      "tipo": "Turismo",
      "numero_resolucion": "RES-001",
      "vigente": true
    }
  ]
}

# Lista conductores (solo de su empresa)
GET /api/v1/conductores
Response: [
  // Solo conductores de Transportes ABC
]

# Intenta ver conductor de otra empresa
GET /api/v1/conductores/{id_otra_empresa}
Response: 403 Forbidden
```

## Archivos a Modificar/Crear

### Modelos
- ✅ `backend/app/models/user.py` - Agregar relación con Empresa
- ✅ `backend/app/models/empresa.py` - Ya tiene todo lo necesario

### Servicios
- `backend/app/services/empresa_service.py` - Agregar gestión de autorizaciones
- `backend/app/services/conductor_service.py` - Agregar filtros por empresa
- `backend/app/services/habilitacion_service.py` - Agregar filtros por empresa
- `backend/app/services/usuario_service.py` - Validar asignación de empresa

### Dependencies
- `backend/app/core/dependencies.py` - Agregar `get_empresa_gerente`

### Endpoints
- `backend/app/api/v1/endpoints/empresas.py` - Agregar endpoints de autorizaciones
- `backend/app/api/v1/endpoints/conductores.py` - Modificar para aplicar filtros
- `backend/app/api/v1/endpoints/autorizaciones.py` - Nuevo archivo

### Schemas
- `backend/app/schemas/empresa.py` - Agregar schemas de autorizaciones
- `backend/app/schemas/autorizacion.py` - Nuevo archivo

### Tests
- Agregar tests para validar filtros por empresa
- Agregar tests para permisos de gerentes
- Agregar tests para gestión de autorizaciones
