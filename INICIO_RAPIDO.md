# 🚀 Guía de Inicio Rápido - Windows

## Prerrequisitos

1. **Docker Desktop** instalado y corriendo
   - Descarga: https://www.docker.com/products/docker-desktop
   - Asegúrate de que esté iniciado (ícono en la bandeja del sistema)

2. **Git** instalado (opcional, si clonaste el repo)

## Pasos para Iniciar

### Opción 1: Script Automático (Recomendado)

#### PowerShell:
```powershell
.\start-windows.ps1
```

#### CMD:
```cmd
start-windows.cmd
```

### Opción 2: Manual

1. **Verificar que Docker esté corriendo:**
```cmd
docker info
```

2. **Construir las imágenes:**
```cmd
docker-compose build
```

3. **Iniciar servicios en modo desarrollo:**
```cmd
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

4. **Ver logs:**
```cmd
docker-compose logs -f
```

5. **Ejecutar migraciones (después de que inicie):**
```cmd
docker exec drtc-backend alembic upgrade head
```

6. **Verificar setup:**
```cmd
docker exec drtc-backend python scripts/verify_setup.py
```

## 🌐 Accesos

Una vez iniciado, accede a:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Frontend** | http://localhost:4321 | - |
| **Backend API** | http://localhost:8002 | - |
| **API Docs (Swagger)** | http://localhost:8002/docs | - |
| **Nginx Proxy** | http://localhost:8082 | - |
| **PgAdmin** | http://localhost:5051 | admin@drtc.local / admin |
| **Redis Commander** | http://localhost:8083 | - |

## 🔍 Verificar que Todo Funciona

### 1. Ver estado de contenedores:
```cmd
docker-compose ps
```

Deberías ver todos los servicios como "Up" o "running".

### 2. Probar el backend:
```cmd
curl http://localhost:8002/health
```

O abre en el navegador: http://localhost:8002/docs

### 3. Ver logs de un servicio específico:
```cmd
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

## 🛠️ Comandos Útiles

### Ver logs en tiempo real:
```cmd
docker-compose logs -f
docker-compose logs -f backend
```

### Reiniciar un servicio:
```cmd
docker-compose restart backend
docker-compose restart frontend
```

### Detener todos los servicios:
```cmd
docker-compose down
```

### Detener y eliminar volúmenes (¡cuidado, borra la BD!):
```cmd
docker-compose down -v
```

### Reconstruir imágenes:
```cmd
docker-compose build --no-cache
docker-compose up -d
```

### Acceder a un contenedor:
```cmd
docker exec -it drtc-backend bash
docker exec -it drtc-frontend sh
docker exec -it drtc-postgres psql -U drtc_dev -d drtc_nomina_dev
```

## 🧪 Ejecutar Tests

### Backend:
```cmd
docker exec -it drtc-backend pytest
docker exec -it drtc-backend pytest --cov=app
docker exec -it drtc-backend pytest tests/models/
```

### Ver cobertura:
```cmd
docker exec -it drtc-backend pytest --cov=app --cov-report=html
```

## 📊 Base de Datos

### Conectar a PostgreSQL:
```cmd
docker exec -it drtc-postgres psql -U drtc_dev -d drtc_nomina_dev
```

### Ver tablas:
```sql
\dt
```

### Ver usuarios:
```sql
SELECT email, rol, activo FROM usuarios;
```

### Backup:
```cmd
docker exec drtc-postgres pg_dump -U drtc_dev drtc_nomina_dev > backup.sql
```

### Restore:
```cmd
type backup.sql | docker exec -i drtc-postgres psql -U drtc_dev -d drtc_nomina_dev
```

## 🐛 Solución de Problemas

### Docker no está corriendo
- Inicia Docker Desktop desde el menú de inicio
- Espera a que el ícono en la bandeja del sistema muestre "Docker Desktop is running"

### Error "port is already allocated"
Otro servicio está usando el puerto. Opciones:
1. Detén el otro servicio
2. Cambia el puerto en `docker-compose.yml`

### Backend no inicia
```cmd
# Ver logs
docker-compose logs backend

# Verificar PostgreSQL
docker-compose ps postgres

# Reiniciar
docker-compose restart backend
```

### Frontend no carga
```cmd
# Ver logs
docker-compose logs frontend

# Verificar que el backend esté corriendo
curl http://localhost:8002/health

# Reiniciar
docker-compose restart frontend
```

### Error de migraciones
```cmd
# Ver estado actual
docker exec -it drtc-backend alembic current

# Ver historial
docker exec -it drtc-backend alembic history

# Resetear (¡cuidado!)
docker exec -it drtc-backend alembic downgrade base
docker exec -it drtc-backend alembic upgrade head
```

### Limpiar todo y empezar de nuevo
```cmd
docker-compose down -v
docker-compose build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## 📝 Próximos Pasos

1. **Explorar la API**: http://localhost:8002/docs
2. **Ver PgAdmin**: http://localhost:5051
3. **Revisar logs**: `docker-compose logs -f`
4. **Ejecutar tests**: `docker exec -it drtc-backend pytest`
5. **Desarrollar**: Los cambios en el código se reflejan automáticamente (hot reload)

## 🚀 Preparar para Producción

Cuando estés listo para producción:

1. **Actualizar .env con valores de producción**
2. **Cambiar ENVIRONMENT=production**
3. **Usar solo docker-compose.yml**:
   ```cmd
   docker-compose up -d
   ```

## 📞 Ayuda

- Ver README.md para documentación completa
- Ver ESTADO_PROYECTO.md para el progreso actual
- Ver .kiro/specs/ para especificaciones técnicas
