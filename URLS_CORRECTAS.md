# URLs Correctas del Sistema

## ✅ Arquitectura

El sistema usa **Nginx como reverse proxy** en el puerto 80, que redirige las peticiones a:
- **Frontend (Astro):** Puerto interno 4321
- **Backend (FastAPI):** Puerto interno 8000

## 🌐 URLs Públicas (A través de Nginx - Puerto 80)

### Frontend
- **Página principal:** http://localhost
- **Login:** http://localhost/login
- **Dashboard:** http://localhost/dashboard

### API Backend
- **Base URL:** http://localhost/api/v1/
- **Login:** http://localhost/api/v1/auth/login
- **Habilitaciones:** http://localhost/api/v1/habilitaciones
- **Usuarios:** http://localhost/api/v1/usuarios
- **Empresas:** http://localhost/api/v1/empresas
- **Conductores:** http://localhost/api/v1/conductores

### Documentación
- **Swagger UI:** http://localhost/api/docs
- **ReDoc:** http://localhost/api/redoc
- **OpenAPI JSON:** http://localhost/api/openapi.json

### Utilidades
- **Health Check:** http://localhost/health
- **Metrics:** http://localhost/metrics

## 🔧 URLs Directas (Sin Nginx - Para desarrollo)

### Frontend Directo
- **Astro Dev Server:** http://localhost:4321

### Backend Directo
- **FastAPI:** http://localhost:8002
- **Swagger UI:** http://localhost:8002/docs
- **ReDoc:** http://localhost:8002/redoc

### Base de Datos
- **PostgreSQL:** localhost:5434
  - Usuario: drtc_user
  - Base de datos: drtc_nomina

### Redis
- **Redis:** localhost:6381

## 📝 Configuración de Nginx

Nginx está configurado para:

1. **Frontend (`/`):** Proxy a `frontend:4321`
   - Incluye soporte para WebSocket (HMR en desarrollo)

2. **API (`/api/`):** Proxy a `backend:8000`
   - Rate limiting: 10 req/s
   - CORS habilitado

3. **Login (`/api/v1/auth/login`):** Rate limiting estricto
   - 5 req/min para prevenir ataques de fuerza bruta

4. **Docs (`/docs`, `/redoc`):** Proxy a backend
   - Documentación interactiva de la API

## 🧪 Cómo Probar

### 1. Verificar que Nginx esté corriendo

```powershell
docker-compose ps nginx
```

Deberías ver:
```
NAME         STATUS        PORTS
drtc-nginx   Up X minutes  0.0.0.0:80->80/tcp
```

### 2. Probar el Frontend

```powershell
# Abrir en el navegador
start http://localhost
```

### 3. Probar la API

```powershell
# Health check
curl http://localhost/health

# Login (PowerShell)
$body = @{
    username = "director@drtc.gob.pe"
    password = "Director123!"
}
Invoke-RestMethod -Uri "http://localhost/api/v1/auth/login" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
```

### 4. Probar Swagger

```powershell
start http://localhost/docs
```

## ⚠️ Errores Comunes

### Error: "Connection refused" o "Cannot connect"

**Causa:** Nginx no está corriendo

**Solución:**
```powershell
docker-compose up -d nginx
```

### Error: "404 Not Found" en /docs

**Causa:** Configuración de Nginx no actualizada

**Solución:**
```powershell
docker-compose restart nginx
```

### Error: "502 Bad Gateway"

**Causa:** Backend o Frontend no están corriendo

**Solución:**
```powershell
docker-compose ps
docker-compose up -d backend frontend
```

### Error: CORS en el navegador

**Causa:** Petición directa al backend (puerto 8002) en lugar de a través de Nginx

**Solución:** Usa `http://localhost/api/...` en lugar de `http://localhost:8002/api/...`

## 🔄 Flujo de Peticiones

```
Navegador
    ↓
http://localhost (Puerto 80)
    ↓
Nginx (Reverse Proxy)
    ↓
    ├─→ / → Frontend (Astro:4321)
    ├─→ /api/ → Backend (FastAPI:8000)
    └─→ /docs → Backend (FastAPI:8000)
```

## 📊 Puertos Resumen

| Servicio | Puerto Externo | Puerto Interno | Acceso |
|----------|----------------|----------------|--------|
| Nginx | 80 | 80 | ✅ Usar este |
| Frontend | 4321 | 4321 | ⚠️ Solo desarrollo |
| Backend | 8002 | 8000 | ⚠️ Solo desarrollo |
| PostgreSQL | 5434 | 5432 | ✅ Para conexiones DB |
| Redis | 6381 | 6379 | ✅ Para conexiones Redis |

## ✅ URLs Recomendadas para Usar

**En el código del frontend, usa URLs relativas:**
```javascript
// ✅ CORRECTO
fetch('/api/v1/habilitaciones')
fetch('/api/v1/auth/login')

// ❌ INCORRECTO
fetch('http://localhost:8002/api/v1/habilitaciones')
fetch('http://localhost:8002/api/v1/auth/login')
```

**Para acceder desde el navegador:**
- ✅ http://localhost (Frontend)
- ✅ http://localhost/docs (Swagger)
- ✅ http://localhost/api/v1/... (API)

**Para desarrollo/debugging:**
- ⚠️ http://localhost:4321 (Frontend directo)
- ⚠️ http://localhost:8002/docs (Backend directo)

---

**Última actualización:** 2024-11-16
**Configuración:** Nginx como reverse proxy
