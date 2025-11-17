# Actualizaciones a Versiones Modernas

## ✅ Cambios Realizados

### 1. Docker Compose (Formato Moderno)
- ❌ **Antes:** `version: '3.8'` (obsoleto desde Docker Compose v2)
- ✅ **Ahora:** Sin línea `version` (formato moderno)

**Archivos actualizados:**
- `docker-compose.yml`
- `docker-compose.dev.yml`

### 2. Imágenes Docker Actualizadas

| Servicio | Antes | Ahora |
|----------|-------|-------|
| PostgreSQL | `postgres:16-alpine` | `postgres:17-alpine` |
| Redis | `redis:7-alpine` | `redis:7.4-alpine` |
| Python | `python:3.12-slim` | `python:3.13-slim` |

### 3. Dependencias Python Actualizadas

#### Framework Principal
- FastAPI: `0.109.0` → `0.115.5`
- Uvicorn: `0.27.0` → `0.32.1`
- Pydantic: `2.5.3` → `2.10.3`

#### Base de Datos
- SQLAlchemy: `2.0.25` → `2.0.36`
- AsyncPG: `0.29.0` → `0.30.0`
- Alembic: `1.13.1` → `1.14.0`

#### Seguridad
- Bcrypt: `4.1.2` → `4.2.1`

#### Redis
- Redis: `5.0.1` → `5.2.1`
- Hiredis: `2.3.2` → `3.0.0`

#### Celery
- Celery: `5.3.6` → `5.4.0`

#### HTTP Client
- HTTPX: `0.26.0` → `0.28.1`

#### Generación de PDFs
- ReportLab: `4.0.9` → `4.2.5`
- WeasyPrint: `60.2` → `63.1`
- QRCode: `7.4.2` → `8.0`
- Pillow: (agregado) → `11.0.0`

#### Excel
- OpenPyXL: `3.1.2` → `3.1.5`
- XlsxWriter: `3.1.9` → `3.2.0`

#### Testing
- Pytest: `7.4.4` → `8.3.4`
- Pytest-AsyncIO: `0.23.3` → `0.24.0`
- Pytest-Cov: `4.1.0` → `6.0.0`
- Faker: `22.6.0` → `33.1.0`

#### Logging
- Python-JSON-Logger: `2.0.7` → `3.2.1`

#### Métricas
- Prometheus-Client: `0.19.0` → `0.21.0`

## 🔧 Cómo Aplicar los Cambios

### 1. Reconstruir Contenedores

```bash
# Detener contenedores actuales
docker compose down

# Reconstruir con nuevas versiones
docker compose build --no-cache

# Iniciar servicios
docker compose up -d
```

### 2. Actualizar Dependencias Python (si no usas Docker)

```bash
cd backend
pip install --upgrade -r requirements.txt
```

## 📝 Crear Usuarios de Prueba

### Opción 1: Script PowerShell (Recomendado)

```powershell
.\crear-usuarios.ps1
```

### Opción 2: Manualmente vía API

1. Inicia el sistema:
```powershell
.\start-windows.ps1
```

2. Ve a http://localhost:8000/docs

3. Haz login con `admin@drtc.gob.pe` / `Admin123!`

4. Usa el endpoint `POST /api/v1/usuarios` para crear:
   - Director: `director@drtc.gob.pe` / `Director123!`
   - Subdirector: `subdirector@drtc.gob.pe` / `Subdirector123!`
   - Operario: `operario@drtc.gob.pe` / `Operario123!`

## ✅ Verificación

### Verificar versiones de Docker:

```bash
docker --version
# Debe ser Docker version 24.0+ o superior

docker compose version
# Debe ser Docker Compose version v2.20+ o superior
```

### Verificar que los servicios funcionan:

```bash
# Ver logs
docker compose logs -f backend

# Verificar salud de servicios
docker compose ps
```

### Probar login de usuarios:

```bash
# Probar Director
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=director@drtc.gob.pe&password=Director123!"
```

## 🚀 Beneficios de las Actualizaciones

### Seguridad
- ✅ Parches de seguridad más recientes
- ✅ Vulnerabilidades conocidas corregidas

### Performance
- ✅ Mejoras de rendimiento en FastAPI 0.115
- ✅ Optimizaciones en SQLAlchemy 2.0.36
- ✅ Mejor manejo de conexiones en AsyncPG 0.30

### Características Nuevas
- ✅ Soporte completo para Python 3.13
- ✅ Mejoras en validación de Pydantic 2.10
- ✅ Nuevas características de PostgreSQL 17

### Compatibilidad
- ✅ Docker Compose v2 (formato moderno sin `version`)
- ✅ Mejor integración con Docker Desktop
- ✅ Soporte para Apple Silicon (M1/M2/M3)

## ⚠️ Notas Importantes

1. **Backup de Base de Datos:** Si tienes datos importantes, haz backup antes de actualizar:
   ```bash
   docker exec drtc-postgres pg_dump -U drtc_user drtc_nomina > backup.sql
   ```

2. **Migraciones:** Después de actualizar, ejecuta las migraciones:
   ```bash
   docker exec drtc-backend alembic upgrade head
   ```

3. **Caché de Docker:** Si tienes problemas, limpia el caché:
   ```bash
   docker system prune -a
   ```

## 📚 Referencias

- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
- [FastAPI 0.115 Release Notes](https://fastapi.tiangolo.com/release-notes/)
- [PostgreSQL 17 Release Notes](https://www.postgresql.org/docs/17/release-17.html)
- [Python 3.13 What's New](https://docs.python.org/3.13/whatsnew/3.13.html)

---

**Fecha de actualización:** 2024-11-16
**Versión del sistema:** 2.0 (Moderna)
