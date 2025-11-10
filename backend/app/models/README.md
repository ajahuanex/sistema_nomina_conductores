# Modelos de Base de Datos

Este directorio contiene todos los modelos SQLAlchemy del sistema.

## Estructura

- `base.py`: Modelo base con campos comunes (id, created_at, updated_at)
- `user.py`: Modelo de Usuario con roles
- Otros modelos se agregarán según el plan de implementación

## Uso de BaseModel

Todos los modelos deben heredar de `BaseModel` para obtener automáticamente:
- `id`: UUID único como clave primaria
- `created_at`: Timestamp de creación
- `updated_at`: Timestamp de última actualización

### Ejemplo:

```python
from app.models.base import BaseModel
from sqlalchemy import Column, String

class MiModelo(BaseModel):
    __tablename__ = "mi_tabla"
    
    nombre = Column(String(100), nullable=False)
```

## Migraciones con Alembic

### Crear una nueva migración:

```bash
cd backend
alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar migraciones:

```bash
alembic upgrade head
```

### Revertir última migración:

```bash
alembic downgrade -1
```

### Ver historial de migraciones:

```bash
alembic history
```

## Importante

Cuando crees un nuevo modelo, asegúrate de importarlo en `backend/alembic/env.py` para que Alembic lo detecte en las migraciones automáticas.
