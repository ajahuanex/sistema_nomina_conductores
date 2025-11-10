# Configuración de Base de Datos y Migraciones

Este documento describe la configuración de SQLAlchemy 2.0, Alembic y el sistema de migraciones para el proyecto.

## Stack de Base de Datos

- **ORM**: SQLAlchemy 2.0 (async)
- **Driver**: asyncpg (PostgreSQL async)
- **Migraciones**: Alembic
- **Base de Datos**: PostgreSQL 15+

## Estructura de Archivos

```
backend/
├── alembic/
│   ├── versions/          # Archivos de migración
│   ├── env.py            # Configuración de Alembic
│   └── script.py.mako    # Template para migraciones
├── alembic.ini           # Configuración principal de Alembic
├── app/
│   ├── core/
│   │   ├── database.py   # Configuración de SQLAlchemy
│   │   └── config.py     # Variables de entorno
│   └── models/
│       ├── base.py       # Modelo base con campos comunes
│       └── ...           # Otros modelos
└── scripts/
    ├── run_migrations.sh     # Script para aplicar migraciones (Linux/Mac)
    ├── run_migrations.bat    # Script para aplicar migraciones (Windows)
    ├── create_migration.sh   # Script para crear migraciones (Linux/Mac)
    └── create_migration.bat  # Script para crear migraciones (Windows)
```

## Configuración

### Variables de Entorno

La URL de conexión se configura en `.env`:

```env
DATABASE_URL=postgresql+asyncpg://usuario:password@host:puerto/database
```

### BaseModel

Todos los modelos heredan de `BaseModel` que proporciona:

- `id`: UUID como clave primaria
- `created_at`: Timestamp de creación (UTC)
- `updated_at`: Timestamp de última actualización (UTC)

```python
from app.models.base import BaseModel
from sqlalchemy import Column, String

class MiModelo(BaseModel):
    __tablename__ = "mi_tabla"
    
    nombre = Column(String(100), nullable=False)
```

## Uso de Alembic

### 1. Crear una Nueva Migración

Después de crear o modificar modelos:

**Linux/Mac:**
```bash
cd backend
./scripts/create_migration.sh "Descripción del cambio"
```

**Windows:**
```cmd
cd backend
scripts\create_migration.bat "Descripción del cambio"
```

**Manualmente:**
```bash
cd backend
alembic revision --autogenerate -m "Descripción del cambio"
```

### 2. Revisar la Migración Generada

Alembic genera un archivo en `alembic/versions/`. **Siempre revisa el archivo** antes de aplicarlo para asegurarte de que los cambios son correctos.

### 3. Aplicar Migraciones

**Linux/Mac:**
```bash
cd backend
./scripts/run_migrations.sh
```

**Windows:**
```cmd
cd backend
scripts\run_migrations.bat
```

**Manualmente:**
```bash
cd backend
alembic upgrade head
```

### 4. Revertir Migraciones

Revertir la última migración:
```bash
alembic downgrade -1
```

Revertir a una versión específica:
```bash
alembic downgrade <revision_id>
```

Revertir todas las migraciones:
```bash
alembic downgrade base
```

### 5. Ver Historial de Migraciones

```bash
alembic history
```

Ver migración actual:
```bash
alembic current
```

## Uso con Docker

### Ejecutar Migraciones en Contenedor

```bash
docker-compose exec backend alembic upgrade head
```

### Crear Migración en Contenedor

```bash
docker-compose exec backend alembic revision --autogenerate -m "Descripción"
```

### Iniciar Base de Datos Limpia

```bash
# Detener contenedores
docker-compose down -v

# Iniciar de nuevo
docker-compose up -d

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head
```

## Flujo de Trabajo Típico

1. **Crear/Modificar Modelo**
   ```python
   # app/models/mi_modelo.py
   from app.models.base import BaseModel
   from sqlalchemy import Column, String
   
   class MiModelo(BaseModel):
       __tablename__ = "mi_tabla"
       nombre = Column(String(100), nullable=False)
   ```

2. **Importar en alembic/env.py**
   ```python
   from app.models.mi_modelo import MiModelo
   ```

3. **Crear Migración**
   ```bash
   alembic revision --autogenerate -m "Agregar tabla mi_tabla"
   ```

4. **Revisar Archivo Generado**
   - Abrir `alembic/versions/XXXX_agregar_tabla_mi_tabla.py`
   - Verificar que `upgrade()` y `downgrade()` sean correctos

5. **Aplicar Migración**
   ```bash
   alembic upgrade head
   ```

6. **Verificar en Base de Datos**
   ```bash
   # Conectarse a PostgreSQL
   psql -U usuario -d database
   
   # Ver tablas
   \dt
   
   # Ver estructura de tabla
   \d mi_tabla
   ```

## Comandos Útiles de Alembic

| Comando | Descripción |
|---------|-------------|
| `alembic upgrade head` | Aplicar todas las migraciones pendientes |
| `alembic upgrade +1` | Aplicar la siguiente migración |
| `alembic downgrade -1` | Revertir la última migración |
| `alembic downgrade base` | Revertir todas las migraciones |
| `alembic current` | Ver migración actual |
| `alembic history` | Ver historial de migraciones |
| `alembic history --verbose` | Ver historial detallado |
| `alembic show <revision>` | Ver detalles de una migración |
| `alembic stamp head` | Marcar base de datos como actualizada sin ejecutar migraciones |

## Solución de Problemas

### Error: "Can't locate revision identified by 'XXXX'"

La base de datos no está sincronizada con las migraciones. Solución:

```bash
# Opción 1: Marcar como actualizada
alembic stamp head

# Opción 2: Recrear base de datos
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

### Error: "Target database is not up to date"

Hay migraciones pendientes:

```bash
alembic upgrade head
```

### Error: "FAILED: Multiple head revisions are present"

Hay múltiples ramas de migración. Solución:

```bash
# Ver las cabezas
alembic heads

# Fusionar las ramas
alembic merge -m "Merge branches" <rev1> <rev2>
```

### Migración Autogenerada Vacía

Alembic no detectó cambios. Posibles causas:

1. El modelo no está importado en `alembic/env.py`
2. El modelo no hereda de `Base`
3. Los cambios ya están aplicados en la base de datos

## Testing

Los tests usan SQLite en memoria para velocidad:

```python
# tests/conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

Para ejecutar tests:

```bash
pytest tests/test_database.py -v
```

## Mejores Prácticas

1. **Siempre revisar migraciones autogeneradas** antes de aplicarlas
2. **Usar nombres descriptivos** para las migraciones
3. **Probar migraciones** en entorno de desarrollo antes de producción
4. **Hacer backup** de la base de datos antes de migraciones en producción
5. **Importar todos los modelos** en `alembic/env.py` para autogenerate
6. **No modificar migraciones aplicadas** - crear una nueva migración para cambios
7. **Usar transacciones** - Alembic las maneja automáticamente
8. **Documentar cambios complejos** en el archivo de migración

## Referencias

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
