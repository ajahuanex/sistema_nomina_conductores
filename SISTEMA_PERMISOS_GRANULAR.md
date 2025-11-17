# Sistema de Permisos Granular por Módulo

## 📋 Descripción

Sistema que permite al Superusuario otorgar permisos específicos a usuarios para acceder a diferentes módulos del sistema con acciones granulares (leer, crear, editar, eliminar).

## 🏗️ Arquitectura

### Modelo de Permisos

```python
class PermisoUsuario:
    usuario_id: UUID
    modulo: str  # usuarios, empresas, conductores, etc.
    puede_leer: bool
    puede_crear: bool
    puede_editar: bool
    puede_eliminar: bool
    permisos_especiales: JSON  # Permisos adicionales específicos
    activo: bool
```

### Módulos del Sistema

```python
class Modulo(Enum):
    USUARIOS = "usuarios"
    EMPRESAS = "empresas"
    CONDUCTORES = "conductores"
    HABILITACIONES = "habilitaciones"
    PAGOS = "pagos"
    DOCUMENTOS = "documentos"
    INFRACCIONES = "infracciones"
    REPORTES = "reportes"
    AUDITORIA = "auditoria"
```

## 🔐 Reglas de Permisos

### Superusuario
- ✅ Acceso completo a TODOS los módulos
- ✅ Puede otorgar/revocar permisos a otros usuarios
- ✅ No requiere permisos explícitos en la tabla

### Otros Roles
- ⚠️ Requieren permisos explícitos otorgados por Superusuario
- ⚠️ Sin permisos = Sin acceso al módulo
- ✅ Permisos granulares por acción (CRUD)

## 📊 Matriz de Permisos por Defecto

### Director (Sugerido)
| Módulo | Leer | Crear | Editar | Eliminar |
|--------|------|-------|--------|----------|
| Usuarios | ✅ | ✅ | ✅ | ❌ |
| Empresas | ✅ | ✅ | ✅ | ❌ |
| Conductores | ✅ | ✅ | ✅ | ❌ |
| Habilitaciones | ✅ | ✅ | ✅ | ❌ |
| Pagos | ✅ | ✅ | ✅ | ❌ |
| Reportes | ✅ | ❌ | ❌ | ❌ |
| Auditoría | ✅ | ❌ | ❌ | ❌ |

### Subdirector (Sugerido)
| Módulo | Leer | Crear | Editar | Eliminar |
|--------|------|-------|--------|----------|
| Usuarios | ✅ | ❌ | ❌ | ❌ |
| Empresas | ✅ | ✅ | ✅ | ❌ |
| Conductores | ✅ | ✅ | ✅ | ❌ |
| Habilitaciones | ✅ | ✅ | ✅ | ❌ |
| Pagos | ✅ | ✅ | ✅ | ❌ |
| Reportes | ✅ | ❌ | ❌ | ❌ |

### Operario (Sugerido)
| Módulo | Leer | Crear | Editar | Eliminar |
|--------|------|-------|--------|----------|
| Conductores | ✅ | ✅ | ✅ | ❌ |
| Habilitaciones | ✅ | ✅ | ✅ | ❌ |
| Pagos | ✅ | ✅ | ❌ | ❌ |
| Documentos | ✅ | ✅ | ❌ | ❌ |

### Gerente (Automático)
| Módulo | Leer | Crear | Editar | Eliminar |
|--------|------|-------|--------|----------|
| Conductores | ✅* | ✅* | ✅* | ❌ |
| Habilitaciones | ✅* | ❌ | ❌ | ❌ |
| Pagos | ✅* | ✅* | ❌ | ❌ |
| Documentos | ✅* | ✅* | ❌ | ❌ |

*Solo de su empresa

## 🔧 Implementación

### 1. Modelo de Datos

Archivo: `backend/app/models/permiso.py`

```python
class PermisoUsuario(BaseModel):
    __tablename__ = "permisos_usuario"
    
    usuario_id = Column(UUID, ForeignKey("usuarios.id"))
    modulo = Column(String(50), nullable=False)
    puede_leer = Column(Boolean, default=True)
    puede_crear = Column(Boolean, default=False)
    puede_editar = Column(Boolean, default=False)
    puede_eliminar = Column(Boolean, default=False)
    permisos_especiales = Column(JSON, nullable=True)
    activo = Column(Boolean, default=True)
```

### 2. Método en Usuario

```python
class Usuario:
    def tiene_permiso_modulo(self, modulo: str, accion: str = "leer") -> bool:
        # Superusuario siempre tiene acceso
        if self.rol == RolUsuario.SUPERUSUARIO:
            return True
        
        # Buscar permiso específico
        for permiso in self.permisos:
            if permiso.modulo == modulo and permiso.activo:
                if accion == "leer":
                    return permiso.puede_leer
                elif accion == "crear":
                    return permiso.puede_crear
                elif accion == "editar":
                    return permiso.puede_editar
                elif accion == "eliminar":
                    return permiso.puede_eliminar
        
        return False
```

### 3. Dependency para Endpoints

```python
def require_module_permission(modulo: str, accion: str = "leer"):
    async def _validate(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol == RolUsuario.SUPERUSUARIO:
            return current_user
        
        if not current_user.tiene_permiso_modulo(modulo, accion):
            raise HTTPException(
                status_code=403,
                detail=f"No tiene permisos para {accion} en el módulo {modulo}"
            )
        
        return current_user
    
    return _validate
```

### 4. Uso en Endpoints

```python
@router.get("/usuarios")
async def listar_usuarios(
    current_user: Usuario = Depends(require_module_permission("usuarios", "leer"))
):
    # Solo usuarios con permiso de lectura en módulo usuarios
    ...

@router.post("/usuarios")
async def crear_usuario(
    current_user: Usuario = Depends(require_module_permission("usuarios", "crear"))
):
    # Solo usuarios con permiso de creación en módulo usuarios
    ...
```

## 📝 Endpoints de Gestión de Permisos

### Listar Permisos de Usuario
```http
GET /api/v1/usuarios/{usuario_id}/permisos
Authorization: Bearer {token}

Response:
[
  {
    "id": "uuid",
    "modulo": "usuarios",
    "puede_leer": true,
    "puede_crear": true,
    "puede_editar": true,
    "puede_eliminar": false,
    "activo": true
  }
]
```

### Otorgar Permiso
```http
POST /api/v1/usuarios/{usuario_id}/permisos
Authorization: Bearer {token}
Content-Type: application/json

{
  "modulo": "usuarios",
  "puede_leer": true,
  "puede_crear": true,
  "puede_editar": false,
  "puede_eliminar": false
}
```

### Actualizar Permiso
```http
PUT /api/v1/usuarios/{usuario_id}/permisos/{permiso_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "puede_editar": true
}
```

### Revocar Permiso
```http
DELETE /api/v1/usuarios/{usuario_id}/permisos/{permiso_id}
Authorization: Bearer {token}
```

## 🎯 Casos de Uso

### Caso 1: Director con Acceso a Usuarios

El Superusuario otorga al Director permisos completos en el módulo de usuarios:

```python
# Crear permiso
permiso = PermisoUsuario(
    usuario_id=director.id,
    modulo="usuarios",
    puede_leer=True,
    puede_crear=True,
    puede_editar=True,
    puede_eliminar=False  # No puede eliminar usuarios
)
```

Ahora el Director puede:
- ✅ Ver lista de usuarios
- ✅ Crear nuevos usuarios
- ✅ Editar usuarios existentes
- ❌ Eliminar usuarios

### Caso 2: Operario con Acceso Limitado

El Superusuario otorga al Operario solo permisos de lectura y creación en conductores:

```python
permiso = PermisoUsuario(
    usuario_id=operario.id,
    modulo="conductores",
    puede_leer=True,
    puede_crear=True,
    puede_editar=False,
    puede_eliminar=False
)
```

### Caso 3: Permisos Especiales

Para permisos más específicos, usar el campo `permisos_especiales`:

```python
permiso = PermisoUsuario(
    usuario_id=usuario.id,
    modulo="habilitaciones",
    puede_leer=True,
    puede_editar=True,
    permisos_especiales={
        "puede_aprobar": True,
        "puede_rechazar": False,
        "puede_habilitar": True,
        "solo_su_region": True
    }
)
```

## 🔄 Migración

### Crear Tabla de Permisos

```sql
CREATE TABLE permisos_usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    modulo VARCHAR(50) NOT NULL,
    puede_leer BOOLEAN DEFAULT TRUE,
    puede_crear BOOLEAN DEFAULT FALSE,
    puede_editar BOOLEAN DEFAULT FALSE,
    puede_eliminar BOOLEAN DEFAULT FALSE,
    permisos_especiales JSONB,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_permiso_usuario_modulo (usuario_id, modulo, activo)
);
```

### Script de Migración de Permisos Existentes

```python
# Otorgar permisos a Directores existentes
directores = session.query(Usuario).filter(Usuario.rol == RolUsuario.DIRECTOR).all()

for director in directores:
    modulos = ["usuarios", "empresas", "conductores", "habilitaciones", "pagos"]
    for modulo in modulos:
        permiso = PermisoUsuario(
            usuario_id=director.id,
            modulo=modulo,
            puede_leer=True,
            puede_crear=True,
            puede_editar=True,
            puede_eliminar=False
        )
        session.add(permiso)

session.commit()
```

## 📊 Ventajas del Sistema

1. **Flexibilidad**: El Superusuario decide exactamente qué puede hacer cada usuario
2. **Granularidad**: Permisos por acción (CRUD) en cada módulo
3. **Escalabilidad**: Fácil agregar nuevos módulos o permisos
4. **Auditoría**: Registro completo de quién tiene qué permisos
5. **Seguridad**: Principio de mínimo privilegio por defecto
6. **Extensibilidad**: Campo JSON para permisos especiales

## 🚨 Consideraciones de Seguridad

1. **Solo Superusuario** puede otorgar/revocar permisos
2. **Validación en Backend**: Nunca confiar en el frontend
3. **Auditoría**: Registrar todos los cambios de permisos
4. **Revisión Periódica**: Revisar permisos regularmente
5. **Principio de Mínimo Privilegio**: Otorgar solo lo necesario

## 📝 Próximos Pasos

1. ✅ Crear modelo PermisoUsuario
2. ✅ Agregar método tiene_permiso_modulo en Usuario
3. ✅ Crear dependency require_module_permission
4. ⏳ Crear migración de base de datos
5. ⏳ Implementar endpoints de gestión de permisos
6. ⏳ Actualizar todos los endpoints para usar el nuevo sistema
7. ⏳ Crear interfaz de administración de permisos en frontend
8. ⏳ Documentar permisos requeridos por cada endpoint

---

**Sistema desarrollado para**: DRTC Puno
**Fecha**: Noviembre 2024
**Estado**: Diseñado - Pendiente de Implementación Completa
