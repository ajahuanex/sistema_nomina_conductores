# Prueba Rápida del Login

## ✅ El Backend Funciona

Acabo de probar y el backend responde correctamente:

```powershell
$body = @{email="director@drtc.gob.pe"; password="Director123!"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
```

**Resultado:** ✅ Retorna `access_token` y `refresh_token`

## 🧪 Prueba en Swagger

1. Ve a: http://localhost/api/docs
2. Busca el endpoint `POST /api/v1/auth/login`
3. Haz clic en "Try it out"
4. Usa este JSON:
```json
{
  "email": "director@drtc.gob.pe",
  "password": "Director123!"
}
```
5. Haz clic en "Execute"
6. Deberías ver una respuesta 200 con tokens

## 🔍 Problema Probable: CORS

El problema es que el navegador está bloqueando la petición por CORS. Abre la consola del navegador (F12) y verifica si ves errores de CORS.

## 🛠️ Solución Temporal: Usa el Puerto Directo

Mientras arreglamos CORS, puedes usar el backend directamente:

1. Ve a: http://localhost:8002/docs
2. Prueba el login ahí
3. Copia el `access_token`
4. Úsalo en las peticiones

## 📋 Usuarios Disponibles

| Email | Password | Rol |
|-------|----------|-----|
| admin@drtc.gob.pe | Admin123! | Superusuario |
| director@drtc.gob.pe | Director123! | Director |
| subdirector@drtc.gob.pe | Subdirector123! | Subdirector |
| operario@drtc.gob.pe | Operario123! | Operario |

## 🔧 Verificar CORS en el Backend

El backend debe tener esta configuración en `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Próximos Pasos

1. Verifica los logs del navegador (F12 → Console)
2. Verifica los logs del backend: `docker-compose logs backend --tail=50`
3. Si ves errores de CORS, necesitamos actualizar la configuración del backend

---

**Nota:** El backend está funcionando correctamente. El problema es la comunicación entre el frontend y el backend.
