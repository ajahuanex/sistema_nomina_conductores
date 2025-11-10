# Sistema RBAC - Guía de Uso

## Descripción General

El sistema de Control de Acceso Basado en Roles (RBAC) proporciona una forma estructurada de controlar el acceso a los recursos del sistema según el rol del usuario.

## Roles del Sistema

El sistema define 5 roles con diferentes niveles de permisos:

1. **SUPERUSUARIO**: Acceso completo al sistema, incluyendo configuración
2. **DIRECTOR**: Acceso completo a operaciones, puede habilitar conductores y acceder a configuración
3. **SUBDIRECTOR**: Similar a Director pero con restricciones en configuración
4. **OPERARIO**: Puede revisar solicitudes pero no habilitar conductores
5. **GERENTE**: Solo puede gestionar conductores de su propia empresa

## Uso Básico

### 1. Proteger Endpoints por Rol

```python
from fastapi import APIRouter, Depends
from app.core.rbac import require_roles
from app.core.dependencies import get_current_user
from app.models.user import Usuario, RolUsuario

router = APIRouter()

# Endpoint solo para Superusuarios
@router.get("/admin/config")
async def get_config(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != RolUsuario.SUPERUSUARIO:
        raise PermissionDenied()
    return {"config": "data"}

# Mejor forma: usando decoradores
from app.core.rbac import require_superuser

@router.get("/admin/config")
@require_superuser()
async def get_config(current_user: Usuario = Depends(get_current_user)):
    return {"config": "data"}
```

### 2. Decoradores Disponibles

#### `require_roles(*roles)`
Permite especificar múltiples roles permitidos:

```python
from app.core.rbac import require_roles
from app.models.user import RolUsuario

@router.post("/habilitaciones/{id}/habilitar")
@require_roles(RolUsuario.SUPERUSUARIO, RolUsuario.DIRECTOR, RolUsuario.SUBDIRECTOR)
async def habilitar_conductor(
    id: str,
    current_user: Usuario = Depends(get_current_user)
):
    # Solo Superusuarios, Directores y Subdirectores pueden acceder
    return {"message": "Conductor habilitado"}
```

#### `require_admin()`
Atajo para roles administrativos (Superusuario, Director, Subdirector):

```python
from app.core.rbac import require_admin

@router.get("/reportes/completos")
@require_admin()
async def get_reportes_completos(current_user: Usuario = Depends(get_current_user)):
    # Solo administradores pueden acceder
    return {"reportes": []}
```

#### `require_superuser()`
Solo permite acceso a Superusuarios:

```python
from app.core.rbac import require_superuser

@router.put("/configuracion/sistema")
@require_superuser()
async def update_config(
    config: ConfigSchema,
    current_user: Usuario = Depends(get_current_user)
):
    # Solo Superusuarios pueden modificar configuración
    return {"message": "Configuración actualizada"}
```

### 3. Verificar Acceso a Recursos

#### Verificar Acceso a Empresa

```python
from uuid import UUID
from app.core.rbac import verify_empresa_access, PermissionDenied

@router.get("/empresas/{empresa_id}/conductores")
async def get_conductores_empresa(
    empresa_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verificar que el usuario tenga acceso a esta empresa
    has_access = await verify_empresa_access(empresa_id, current_user, db)
    if not has_access:
        raise PermissionDenied("No tiene acceso a esta empresa")
    
    # Continuar con la lógica...
    return {"conductores": []}
```

#### Usar Dependency para Verificar Acceso

```python
from app.core.rbac import require_empresa_access

@router.get("/empresas/{empresa_id}/conductores")
async def get_conductores_empresa(
    empresa_id: UUID,
    current_user: Usuario = Depends(require_empresa_access),
    db: AsyncSession = Depends(get_db)
):
    # Si llegamos aquí, el usuario tiene acceso a la empresa
    return {"conductores": []}
```

### 4. Funciones de Verificación de Permisos

#### `can_habilitar_conductor(user)`
Verifica si el usuario puede habilitar conductores:

```python
from app.core.rbac import can_habilitar_conductor, PermissionDenied

@router.post("/habilitaciones/{id}/habilitar")
async def habilitar_conductor(
    id: str,
    current_user: Usuario = Depends(get_current_user)
):
    if not can_habilitar_conductor(current_user):
        raise PermissionDenied("No tiene permisos para habilitar conductores")
    
    # Lógica de habilitación...
    return {"message": "Conductor habilitado"}
```

#### `can_revisar_solicitud(user)`
Verifica si el usuario puede revisar solicitudes:

```python
from app.core.rbac import can_revisar_solicitud

@router.get("/habilitaciones/pendientes")
async def get_solicitudes_pendientes(
    current_user: Usuario = Depends(get_current_user)
):
    if not can_revisar_solicitud(current_user):
        raise PermissionDenied("No tiene permisos para revisar solicitudes")
    
    # Obtener solicitudes...
    return {"solicitudes": []}
```

#### `can_modify_user(current_user, target_user)`
Verifica si un usuario puede modificar a otro:

```python
from app.core.rbac import can_modify_user

@router.put("/usuarios/{user_id}")
async def update_user(
    user_id: UUID,
    user_data: UserUpdateSchema,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Obtener usuario objetivo
    target_user = await get_user_by_id(db, user_id)
    
    if not can_modify_user(current_user, target_user):
        raise PermissionDenied("No tiene permisos para modificar este usuario")
    
    # Actualizar usuario...
    return {"message": "Usuario actualizado"}
```

#### `can_create_user_with_role(current_user, target_role)`
Verifica si un usuario puede crear otro con un rol específico:

```python
from app.core.rbac import can_create_user_with_role

@router.post("/usuarios")
async def create_user(
    user_data: UserCreateSchema,
    current_user: Usuario = Depends(get_current_user)
):
    if not can_create_user_with_role(current_user, user_data.rol):
        raise PermissionDenied(
            f"No tiene permisos para crear usuarios con rol {user_data.rol}"
        )
    
    # Crear usuario...
    return {"message": "Usuario creado"}
```

### 5. Filtrar Datos por Acceso

#### Filtrar Empresas según Rol

```python
from app.core.rbac import filter_empresas_by_access

@router.get("/conductores")
async def get_conductores(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Obtener filtro de empresa según rol
    empresa_filter = await filter_empresas_by_access(current_user, db)
    
    # Construir query
    query = select(Conductor)
    
    # Si es Gerente, filtrar por su empresa
    if empresa_filter:
        query = query.where(Conductor.empresa_id == empresa_filter)
    
    # Ejecutar query
    result = await db.execute(query)
    conductores = result.scalars().all()
    
    return {"conductores": conductores}
```

## Matriz de Permisos

| Acción | Superusuario | Director | Subdirector | Operario | Gerente |
|--------|--------------|----------|-------------|----------|---------|
| Acceder a cualquier empresa | ✅ | ✅ | ✅ | ✅ | ❌ (solo su empresa) |
| Acceder a cualquier conductor | ✅ | ✅ | ✅ | ✅ | ❌ (solo su empresa) |
| Habilitar conductores | ✅ | ✅ | ✅ | ❌ | ❌ |
| Revisar solicitudes | ✅ | ✅ | ✅ | ✅ | ❌ |
| Acceder a configuración | ✅ | ✅ | ❌ | ❌ | ❌ |
| Acceder a auditoría | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crear Superusuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Crear Directores | ✅ | ❌ | ❌ | ❌ | ❌ |
| Crear Subdirectores | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crear Operarios | ✅ | ✅ | ✅ | ❌ | ❌ |
| Crear Gerentes | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modificar Superusuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modificar Directores | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modificar Subdirectores | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modificar Operarios | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modificar Gerentes | ✅ | ✅ | ✅ | ❌ | ❌ |

## Ejemplos Completos

### Ejemplo 1: Endpoint de Habilitación con RBAC

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rbac import can_habilitar_conductor, PermissionDenied
from app.models.user import Usuario
from app.services.habilitacion_service import HabilitacionService

router = APIRouter()

@router.post("/habilitaciones/{habilitacion_id}/habilitar")
async def habilitar_conductor(
    habilitacion_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Habilita un conductor después de verificar pago
    
    Requiere rol: Superusuario, Director o Subdirector
    """
    # Verificar permisos
    if not can_habilitar_conductor(current_user):
        raise PermissionDenied(
            "Solo Superusuarios, Directores y Subdirectores pueden habilitar conductores"
        )
    
    # Ejecutar lógica de negocio
    service = HabilitacionService(db)
    habilitacion = await service.habilitar_conductor(
        habilitacion_id,
        str(current_user.id)
    )
    
    return {
        "message": "Conductor habilitado exitosamente",
        "habilitacion": habilitacion
    }
```

### Ejemplo 2: Endpoint con Filtro por Empresa

```python
from typing import List, Optional
from app.core.rbac import filter_empresas_by_access
from app.schemas.conductor import ConductorResponse

@router.get("/conductores", response_model=List[ConductorResponse])
async def list_conductores(
    estado: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista conductores según permisos del usuario
    
    - Administradores y Operarios ven todos los conductores
    - Gerentes solo ven conductores de su empresa
    """
    # Obtener filtro de empresa
    empresa_filter = await filter_empresas_by_access(current_user, db)
    
    # Construir query
    query = select(Conductor)
    
    # Aplicar filtro de empresa si es necesario
    if empresa_filter:
        query = query.where(Conductor.empresa_id == empresa_filter)
    
    # Aplicar filtro de estado si se proporciona
    if estado:
        query = query.where(Conductor.estado == estado)
    
    # Ejecutar query
    result = await db.execute(query)
    conductores = result.scalars().all()
    
    return conductores
```

### Ejemplo 3: Endpoint de Creación de Usuario con Validación de Rol

```python
from app.core.rbac import can_create_user_with_role
from app.schemas.user import UserCreate, UserResponse

@router.post("/usuarios", response_model=UserResponse)
async def create_usuario(
    user_data: UserCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crea un nuevo usuario
    
    Permisos:
    - Superusuarios pueden crear cualquier rol
    - Directores pueden crear Subdirectores, Operarios y Gerentes
    - Subdirectores pueden crear Operarios y Gerentes
    """
    # Verificar que el usuario actual puede crear el rol solicitado
    if not can_create_user_with_role(current_user, user_data.rol):
        raise PermissionDenied(
            f"No tiene permisos para crear usuarios con rol {user_data.rol.value}"
        )
    
    # Si es Gerente, debe tener empresa_id
    if user_data.rol == RolUsuario.GERENTE and not user_data.empresa_id:
        raise HTTPException(
            status_code=400,
            detail="Los Gerentes deben estar asociados a una empresa"
        )
    
    # Crear usuario
    from app.services.user_service import UserService
    service = UserService(db)
    new_user = await service.create_user(user_data)
    
    return new_user
```

## Manejo de Errores

El sistema RBAC utiliza la excepción `PermissionDenied` que hereda de `HTTPException`:

```python
from app.core.rbac import PermissionDenied

try:
    if not can_habilitar_conductor(user):
        raise PermissionDenied("No puede habilitar conductores")
except PermissionDenied as e:
    # Se retorna automáticamente HTTP 403 Forbidden
    # con el mensaje de error
    pass
```

## Mejores Prácticas

1. **Usar decoradores cuando sea posible**: Son más limpios y declarativos
2. **Verificar permisos temprano**: Fallar rápido si no hay permisos
3. **Mensajes de error claros**: Indicar qué roles tienen acceso
4. **Filtrar datos en queries**: No retornar datos que el usuario no debe ver
5. **Auditar acciones críticas**: Registrar quién hace qué
6. **Testear todos los niveles de permisos**: Asegurar que cada rol funciona correctamente

## Testing

Ejemplo de test para verificar permisos:

```python
import pytest
from app.core.rbac import can_habilitar_conductor
from app.models.user import RolUsuario

def test_solo_administradores_pueden_habilitar(superusuario, director, operario, gerente):
    assert can_habilitar_conductor(superusuario) is True
    assert can_habilitar_conductor(director) is True
    assert can_habilitar_conductor(operario) is False
    assert can_habilitar_conductor(gerente) is False
```

Ver `tests/core/test_rbac.py` para más ejemplos de tests.
