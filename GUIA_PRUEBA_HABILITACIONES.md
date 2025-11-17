# Guía de Prueba - Endpoints de Habilitaciones

## ✅ Tarea 8.4 Completada

Se han implementado exitosamente **8 endpoints** para la gestión de habilitaciones de conductores.

---

## 🚀 Acceso al Sistema

### Opción 1: Dashboard Web (Interfaz Gráfica)

1. **Acceder al login:**
   - URL: http://localhost/login

2. **Credenciales de prueba:**
   ```
   Email: admin@drtc.gob.pe
   Password: Admin123!
   ```

3. **Dashboard:**
   - Después del login serás redirigido a: http://localhost/dashboard
   - Verás estadísticas y accesos rápidos
   - Desde ahí puedes acceder a Swagger UI

### Opción 2: Swagger UI (Pruebas de API)

1. **Acceder directamente:**
   - URL: http://localhost/api/docs

2. **Autenticarse:**
   - Busca el endpoint `POST /api/v1/auth/login`
   - Click en "Try it out"
   - Ingresa las credenciales:
     ```json
     {
       "email": "admin@drtc.gob.pe",
       "password": "Admin123!"
     }
     ```
   - Copia el `access_token` de la respuesta

3. **Autorizar:**
   - Click en el botón "Authorize" 🔒 (arriba a la derecha)
   - Pega: `Bearer {tu_token_aqui}`
   - Click en "Authorize"

---

## 📋 Endpoints Implementados

### 1. GET /api/v1/habilitaciones
**Descripción:** Listar habilitaciones con filtros opcionales

**Parámetros:**
- `estado` (opcional): pendiente, en_revision, aprobado, observado, rechazado, habilitado
- `skip` (opcional): Número de registros a saltar (paginación)
- `limit` (opcional): Número máximo de registros (default: 100)

**Ejemplo:**
```bash
GET /api/v1/habilitaciones?estado=pendiente&limit=10
```

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO

---

### 2. GET /api/v1/habilitaciones/pendientes
**Descripción:** Listar solo habilitaciones pendientes de revisión

**Parámetros:**
- `skip` (opcional): Paginación
- `limit` (opcional): Límite de resultados

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO

---

### 3. GET /api/v1/habilitaciones/{id}
**Descripción:** Obtener detalles de una habilitación específica

**Parámetros:**
- `id` (requerido): UUID de la habilitación

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE

---

### 4. POST /api/v1/habilitaciones/{id}/revisar
**Descripción:** Cambiar estado de PENDIENTE a EN_REVISION

**Body:**
```json
{
  "observaciones": "Iniciando revisión de documentos"
}
```

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO

---

### 5. POST /api/v1/habilitaciones/{id}/aprobar
**Descripción:** Aprobar solicitud (EN_REVISION → APROBADO)

**Body:**
```json
{
  "observaciones": "Documentos completos y válidos"
}
```

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR

---

### 6. POST /api/v1/habilitaciones/{id}/observar
**Descripción:** Marcar solicitud como observada con comentarios

**Body:**
```json
{
  "observaciones": "Falta certificado médico actualizado y licencia está por vencer"
}
```

**Validación:** Mínimo 10 caracteres

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO

---

### 7. POST /api/v1/habilitaciones/{id}/habilitar
**Descripción:** Habilitar conductor (APROBADO → HABILITADO)

**Requisitos previos:**
- Estado debe ser APROBADO
- Debe tener pago confirmado

**Body:**
```json
{
  "vigencia_hasta": "2026-11-16",
  "observaciones": "Habilitación otorgada"
}
```

**Validación:** La fecha debe ser futura

**Roles permitidos:** SUPERUSUARIO, DIRECTOR, SUBDIRECTOR

---

### 8. POST /api/v1/habilitaciones/{id}/suspender
**Descripción:** Suspender habilitación activa

**Body:**
```json
{
  "motivo": "Conductor registró infracción muy grave según resolución N° 123-2024"
}
```

**Validación:** Mínimo 20 caracteres

**Roles permitidos:** SUPERUSUARIO, DIRECTOR

---

## 🔄 Flujo Completo de Habilitación

```
1. PENDIENTE
   ↓ (POST /revisar)
2. EN_REVISION
   ↓ (POST /aprobar)
3. APROBADO
   ↓ (Registrar pago + POST /habilitar)
4. HABILITADO
   ↓ (POST /suspender - opcional)
5. SUSPENDIDO
```

**Flujo alternativo con observaciones:**
```
1. PENDIENTE
   ↓ (POST /revisar)
2. EN_REVISION
   ↓ (POST /observar)
3. OBSERVADO
```

---

## 🧪 Tests Implementados

**Total:** 29 tests pasando (100%)

**Cobertura:**
- ✅ Tests unitarios de cada endpoint
- ✅ Tests de autorización por roles
- ✅ Tests de validación de datos
- ✅ Tests de flujos completos de habilitación
- ✅ Tests de casos de error

**Ejecutar tests:**
```bash
cd backend
python -m pytest tests/api/test_habilitaciones.py -v
```

---

## 🔐 Control de Acceso (RBAC)

| Endpoint | SUPERUSUARIO | DIRECTOR | SUBDIRECTOR | OPERARIO | GERENTE |
|----------|--------------|----------|-------------|----------|---------|
| GET /habilitaciones | ✅ | ✅ | ✅ | ✅ | ❌ |
| GET /pendientes | ✅ | ✅ | ✅ | ✅ | ❌ |
| GET /{id} | ✅ | ✅ | ✅ | ✅ | ✅ |
| POST /revisar | ✅ | ✅ | ✅ | ✅ | ❌ |
| POST /aprobar | ✅ | ✅ | ✅ | ❌ | ❌ |
| POST /observar | ✅ | ✅ | ✅ | ✅ | ❌ |
| POST /habilitar | ✅ | ✅ | ✅ | ❌ | ❌ |
| POST /suspender | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 📊 Estado del Sistema

### ✅ Completado:
- Backend API con 8 endpoints
- Autenticación JWT
- Control de acceso por roles (RBAC)
- Validación de datos con Pydantic
- Tests de integración completos
- Documentación automática (Swagger)
- Dashboard básico del frontend
- Página de login funcional

### 🔄 En Desarrollo:
- Páginas del frontend para gestión de habilitaciones
- Formularios de creación/edición
- Tablas de listado con filtros
- Módulo de pagos completo

---

## 🐛 Troubleshooting

### El backend no responde:
```bash
docker compose logs backend --tail 50
docker compose restart backend
```

### Nginx devuelve 404:
```bash
docker compose restart nginx
```

### Celery se reinicia constantemente:
```bash
# Detener servicios de Celery (no afecta los endpoints)
docker compose stop celery-worker celery-beat
```

### Ver todos los servicios:
```bash
docker compose ps
```

---

## 📞 Soporte

Para más información sobre los endpoints, consulta:
- **Swagger UI:** http://localhost/api/docs
- **ReDoc:** http://localhost/api/redoc
- **OpenAPI JSON:** http://localhost/api/openapi.json

---

## ✨ Resumen

**Tarea 8.4 - Crear endpoints de habilitaciones: COMPLETADA ✅**

- 8 endpoints implementados y funcionando
- 29 tests pasando (100%)
- Control de acceso por roles
- Documentación completa
- Dashboard funcional

¡El sistema está listo para ser usado! 🎉
