# Estado de Actualización en Docker - DRTC Puno

## ✅ Completado

1. **Migración de permisos creada**: `backend/alembic/versions/20241117_0000_add_permisos_usuario_table.py`
2. **Script de datos de prueba corregido**: Usa `hash_password` en lugar de `get_password_hash`
3. **Dependencia greenlet agregada**: En `requirements.txt`
4. **Contenedores Docker construidos**: Backend, frontend, base de datos, redis, nginx

## ❌ Problema Actual

Hay un conflicto con tipos ENUM de PostgreSQL que ya existen en la base de datos. La migración `20251112_0000_add_documento_conductor_table.py` intenta crear el tipo `tipodocumento` que ya existe.

## 🔧 Solución Recomendada

### Opción 1: Usar el Sistema Localmente (Recomendado para desarrollo)

Ya tienes la base de datos corriendo en Docker y puedes ejecutar el backend localmente:

```bash
# 1. Asegúrate de que solo la base de datos esté corriendo
docker compose up -d db

# 2. Ejecuta las migraciones localmente
cd backend
alembic upgrade head

# 3. Carga los datos de prueba
python scripts/init_complete_test_data.py

# 4. Inicia el backend localmente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. En otra terminal, inicia el frontend
cd frontend
npm run dev
```

### Opción 2: Corregir la Migración y Usar Docker Completo

1. **Modificar la migración problemática** para que verifique si el tipo ya existe:

```python
# En backend/alembic/versions/20251112_0000_add_documento_conductor_table.py
# Cambiar la creación del ENUM para que use checkfirst=True

def upgrade() -> None:
    # Crear el tipo ENUM solo si no existe
    from sqlalchemy.dialects.postgresql import ENUM
    tipo_documento_enum = ENUM(
        'licencia_conducir', 'certificado_medico', 'antecedentes_penales',
        'antecedentes_policiales', 'antecedentes_judiciales', 'foto_conductor', 'otro',
        name='tipodocumento',
        create_type=False  # No crear el tipo automáticamente
    )
    
    # Crear el tipo manualmente con IF NOT EXISTS
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipodocumento AS ENUM (
                'licencia_conducir', 'certificado_medico', 'antecedentes_penales',
                'antecedentes_policiales', 'antecedentes_judiciales', 'foto_conductor', 'otro'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Luego crear la tabla...
    op.create_table('documentos_conductor', ...)
```

2. **Reconstruir y reiniciar**:

```bash
docker compose down -v
docker compose build backend
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/init_complete_test_data.py
```

### Opción 3: Limpiar Base de Datos y Empezar de Cero

```bash
# 1. Detener y limpiar todo
docker compose down -v

# 2. Iniciar solo la base de datos
docker compose up -d db

# 3. Conectar y limpiar tipos ENUM manualmente
docker compose exec db psql -U postgres -d nomina_conductores -c "DROP TYPE IF EXISTS tipodocumento CASCADE;"
docker compose exec db psql -U postgres -d nomina_conductores -c "DROP TYPE IF EXISTS estadoconductor CASCADE;"
docker compose exec db psql -U postgres -d nomina_conductores -c "DROP TYPE IF EXISTS rolusuario CASCADE;"

# 4. Iniciar todos los servicios
docker compose up -d

# 5. Aplicar migraciones
docker compose exec backend alembic upgrade head

# 6. Cargar datos
docker compose exec backend python scripts/init_complete_test_data.py
```

## 📊 Estado de los Servicios

```bash
# Verificar estado
docker compose ps

# Ver logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Verificar salud
curl http://localhost:8000/api/health
curl http://localhost:3000
```

## 🔑 Credenciales de Prueba

Una vez que los datos estén cargados:

```
Admin:
  Email: admin@drtc.gob.pe
  Password: Admin123!

Director:
  Email: director@drtc.gob.pe
  Password: Director123!

Operario:
  Email: operario@drtc.gob.pe
  Password: Operario123!

Gerentes:
  - gerente.puno@transportes.com / Gerente123!
  - gerente.juliaca@transportes.com / Gerente123!
  - gerente.altiplano@transportes.com / Gerente123!
```

## 📝 Archivos Modificados en Esta Sesión

1. `backend/requirements.txt` - Agregado greenlet
2. `backend/scripts/init_complete_test_data.py` - Corregido hash_password
3. `backend/alembic/versions/20241117_0000_add_permisos_usuario_table.py` - Nueva migración
4. `INSTRUCCIONES_ACTUALIZACION_DOCKER.md` - Guía completa
5. `PRUEBA_SISTEMA_ACTUALIZADO.md` - Guía de pruebas

## 🎯 Próximos Pasos

1. Elegir una de las opciones anteriores para resolver el problema de migraciones
2. Cargar los datos de prueba
3. Verificar que todas las funcionalidades nuevas funcionen:
   - Módulo de pagos TUPA
   - Control de acceso para gerentes
   - Sistema de autorizaciones
   - Permisos granulares (modelo creado, endpoints pendientes)

## 💡 Recomendación

Para desarrollo, **usa la Opción 1** (sistema local con solo DB en Docker). Es más rápido y fácil de depurar. Para producción o pruebas completas, usa la Opción 3 (limpiar y empezar de cero).
