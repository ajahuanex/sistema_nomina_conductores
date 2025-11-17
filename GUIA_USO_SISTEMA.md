# Guía de Uso del Sistema - Nómina de Conductores DRTC Puno

## 🚀 Inicio Rápido

### 1. Iniciar el Sistema

```bash
# Windows
./start-windows.ps1

# Linux/Mac
./start.sh
```

El sistema estará disponible en:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/api/docs

### 2. Inicializar Datos de Prueba

```bash
cd backend
python scripts/init_complete_test_data.py
```

## 👥 Usuarios del Sistema

### Roles y Permisos

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **SUPERUSUARIO** | Administrador total del sistema | Acceso completo a todas las funcionalidades |
| **DIRECTOR** | Director de DRTC | Gestión completa, aprobación de habilitaciones |
| **SUBDIRECTOR** | Subdirector de DRTC | Similar a Director |
| **OPERARIO** | Personal operativo | Registro y gestión de conductores |
| **GERENTE** | Gerente de empresa | Solo su empresa y conductores |

### Credenciales de Prueba

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

Gerente Transportes Puno:
  Email: gerente.puno@transportes.com
  Password: Gerente123!

Gerente Transportes Juliaca:
  Email: gerente.juliaca@transportes.com
  Password: Gerente123!

Gerente Transportes Altiplano:
  Email: gerente.altiplano@transportes.com
  Password: Gerente123!
```

## 📋 Flujos de Trabajo

### Flujo 1: Gerente Registra Nuevo Conductor

1. **Login como Gerente**
   ```http
   POST /api/v1/auth/login
   {
     "email": "gerente.puno@transportes.com",
     "password": "Gerente123!"
   }
   ```

2. **Obtener Información de su Empresa**
   ```http
   GET /api/v1/empresas/mi-empresa
   ```
   
   Respuesta incluye:
   - Datos de la empresa
   - Autorizaciones vigentes
   - Tipos de transporte permitidos

3. **Verificar Categorías de Licencia Permitidas**
   
   Según las autorizaciones de la empresa:
   - **TURISMO**: A-IIb, A-IIIa, A-IIIb, A-IIIc
   - **AUTOCOLECTIVO**: A-IIb, A-IIIa, A-IIIb, A-IIIc
   - **MERCANCIAS**: A-IIIb, A-IIIc
   - **TRABAJADORES**: A-IIb, A-IIIa, A-IIIb, A-IIIc
   - **ESTUDIANTES**: A-IIb, A-IIIa, A-IIIb, A-IIIc

4. **Registrar Conductor**
   ```http
   POST /api/v1/conductores
   {
     "empresa_id": "{su_empresa_id}",
     "dni": "87654321",
     "nombres": "Carlos",
     "apellidos": "Pérez López",
     "fecha_nacimiento": "1992-05-15",
     "direccion": "Jr. Arequipa 123",
     "telefono": "987654325",
     "email": "carlos.perez@email.com",
     "licencia_numero": "L87654321",
     "licencia_categoria": "A-IIIb",
     "licencia_emision": "2022-01-15",
     "licencia_vencimiento": "2027-01-15"
   }
   ```

5. **Ver Conductores de su Empresa**
   ```http
   GET /api/v1/conductores?page=1&page_size=10
   ```
   
   Automáticamente filtrado por su empresa.

### Flujo 2: Proceso de Habilitación

1. **Conductor Registrado** (estado: PENDIENTE)
   - Sistema crea automáticamente solicitud de habilitación

2. **Operario Revisa Documentación**
   ```http
   PUT /api/v1/habilitaciones/{id}/revisar
   {
     "observaciones": "Documentación completa"
   }
   ```
   Estado: PENDIENTE → EN_REVISION

3. **Director Aprueba**
   ```http
   PUT /api/v1/habilitaciones/{id}/aprobar
   ```
   Estado: EN_REVISION → APROBADO

4. **Generar Orden de Pago**
   ```http
   POST /api/v1/pagos/habilitacion/{id}/generar-orden
   ```
   
   Respuesta:
   ```json
   {
     "codigo_orden": "OP-HAB-20241117-001",
     "monto_total": 50.00,
     "concepto_tupa": {
       "codigo": "HAB-CONDUCTOR",
       "descripcion": "Habilitación de Conductor",
       "monto": 50.00
     },
     "fecha_vencimiento": "2024-12-17"
   }
   ```

5. **Registrar Pago**
   ```http
   POST /api/v1/pagos
   {
     "habilitacion_id": "{id}",
     "concepto_tupa_id": "{concepto_id}",
     "numero_recibo": "REC-001-2024",
     "monto": 50.00,
     "fecha_pago": "2024-11-17",
     "entidad_bancaria": "Banco de la Nación"
   }
   ```

6. **Operario Confirma Pago**
   ```http
   POST /api/v1/pagos/{pago_id}/confirmar
   ```

7. **Director Habilita Conductor**
   ```http
   PUT /api/v1/habilitaciones/{id}/habilitar
   ```
   Estado: APROBADO → HABILITADO
   Conductor: PENDIENTE → HABILITADO

### Flujo 3: Gestión de Autorizaciones de Empresa

1. **Admin Lista Tipos de Autorización**
   ```http
   GET /api/v1/empresas/tipos-autorizacion
   ```

2. **Admin Agrega Autorización a Empresa**
   ```http
   POST /api/v1/empresas/{empresa_id}/autorizaciones
   {
     "tipo_autorizacion_id": "{tipo_id}",
     "numero_resolucion": "RD-2024-004-DRTC-PUNO",
     "fecha_emision": "2024-11-17",
     "fecha_vencimiento": "2025-12-31",
     "vigente": true
   }
   ```

3. **Ver Autorizaciones de Empresa**
   ```http
   GET /api/v1/empresas/{empresa_id}/autorizaciones
   ```

4. **Revocar Autorización**
   ```http
   DELETE /api/v1/empresas/{empresa_id}/autorizaciones/{auth_id}
   ```

### Flujo 4: Reportes

1. **Reporte de Ingresos por Período**
   ```http
   GET /api/v1/pagos/reportes/ingresos?fecha_inicio=2024-01-01&fecha_fin=2024-12-31
   ```
   
   Respuesta:
   ```json
   {
     "fecha_inicio": "2024-01-01",
     "fecha_fin": "2024-12-31",
     "total_pagos": 150,
     "total_confirmados": 145,
     "total_pendientes": 5,
     "monto_total": 7500.00,
     "monto_confirmado": 7250.00,
     "monto_pendiente": 250.00,
     "pagos_por_concepto": [...],
     "pagos_por_mes": [...]
   }
   ```

2. **Conductores con Documentos por Vencer**
   ```http
   GET /api/v1/conductores?licencia_proxima_vencer=true
   ```

3. **Estadísticas de Habilitaciones**
   ```http
   GET /api/v1/habilitaciones/estadisticas
   ```

## 🔐 Seguridad

### Autenticación

Todos los endpoints (excepto login) requieren token JWT:

```http
Authorization: Bearer {access_token}
```

### Tokens

- **Access Token**: Válido por 30 minutos
- **Refresh Token**: Válido por 7 días

### Renovar Token

```http
POST /api/v1/auth/refresh
{
  "refresh_token": "{refresh_token}"
}
```

## 📊 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Renovar token
- `POST /api/v1/auth/logout` - Cerrar sesión
- `GET /api/v1/auth/me` - Usuario actual

### Empresas
- `GET /api/v1/empresas` - Listar empresas
- `GET /api/v1/empresas/mi-empresa` - Empresa del gerente
- `POST /api/v1/empresas` - Crear empresa
- `GET /api/v1/empresas/{id}` - Obtener empresa
- `PUT /api/v1/empresas/{id}` - Actualizar empresa
- `POST /api/v1/empresas/{id}/autorizaciones` - Agregar autorización

### Conductores
- `GET /api/v1/conductores` - Listar conductores (filtrado automático para gerentes)
- `POST /api/v1/conductores` - Crear conductor
- `GET /api/v1/conductores/{id}` - Obtener conductor
- `PUT /api/v1/conductores/{id}` - Actualizar conductor
- `POST /api/v1/conductores/{id}/cambiar-estado` - Cambiar estado

### Habilitaciones
- `GET /api/v1/habilitaciones` - Listar habilitaciones
- `GET /api/v1/habilitaciones/{id}` - Obtener habilitación
- `PUT /api/v1/habilitaciones/{id}/revisar` - Revisar solicitud
- `PUT /api/v1/habilitaciones/{id}/aprobar` - Aprobar solicitud
- `PUT /api/v1/habilitaciones/{id}/observar` - Observar solicitud
- `PUT /api/v1/habilitaciones/{id}/habilitar` - Habilitar conductor
- `GET /api/v1/habilitaciones/{id}/certificado` - Descargar certificado

### Pagos
- `GET /api/v1/pagos` - Listar pagos
- `POST /api/v1/pagos` - Registrar pago
- `GET /api/v1/pagos/{id}` - Obtener pago
- `POST /api/v1/pagos/{id}/confirmar` - Confirmar pago
- `POST /api/v1/pagos/{id}/rechazar` - Rechazar pago
- `POST /api/v1/pagos/habilitacion/{id}/generar-orden` - Generar orden
- `GET /api/v1/pagos/reportes/ingresos` - Reporte de ingresos

### Documentos
- `POST /api/v1/conductores/{id}/documentos` - Subir documento
- `GET /api/v1/conductores/{id}/documentos` - Listar documentos
- `GET /api/v1/documentos/{id}/descargar` - Descargar documento

## 🛠️ Comandos Útiles

### Desarrollo

```bash
# Ejecutar tests
cd backend
python -m pytest -v

# Tests con cobertura
python -m pytest --cov=app --cov-report=html

# Tests específicos
python -m pytest tests/services/test_pago_service.py -v

# Crear migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

### Producción

```bash
# Iniciar con Docker
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener
docker-compose down

# Reiniciar
docker-compose restart
```

## 📝 Validaciones Importantes

### Conductor

- DNI: 8 dígitos numéricos
- Licencia: Categoría válida según autorizaciones de empresa
- Fechas: Licencia no vencida
- Email: Formato válido
- Teléfono: Mínimo 7 dígitos

### Empresa

- RUC: 11 dígitos numéricos
- Email: Formato válido
- Debe tener al menos una autorización vigente para registrar conductores

### Pago

- Monto: Debe coincidir con concepto TUPA
- Número de recibo: Único en el sistema
- Fecha: No puede ser futura
- Habilitación: No debe tener pago previo

## 🚨 Errores Comunes

### 401 Unauthorized
- Token expirado o inválido
- Solución: Renovar token o hacer login nuevamente

### 403 Forbidden
- Usuario sin permisos para la acción
- Gerente intentando acceder a otra empresa
- Solución: Verificar rol y permisos

### 400 Bad Request
- Datos inválidos en la solicitud
- Validaciones fallidas
- Solución: Revisar mensaje de error y corregir datos

### 409 Conflict
- DNI o licencia duplicados
- Número de recibo duplicado
- Solución: Usar valores únicos

## 📞 Soporte

Para soporte técnico o reportar problemas:
- Email: soporte@drtc.gob.pe
- Teléfono: 051-XXXXXX

---

**Sistema desarrollado para**: Dirección Regional de Transportes y Comunicaciones - Puno
**Versión**: 1.0.0
**Fecha**: Noviembre 2024
