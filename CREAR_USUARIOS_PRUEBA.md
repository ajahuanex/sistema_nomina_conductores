# Crear Usuarios de Prueba

## Problema
Los usuarios de ejemplo (director, operario, subdirector) no existen en la base de datos.

## Solución Rápida

### Paso 1: Asegúrate que Docker esté corriendo

```powershell
# Verificar que Docker Desktop esté corriendo
docker ps
```

### Paso 2: Inicia los contenedores

```powershell
# Desde la raíz del proyecto
docker-compose up -d
```

O usa el script de inicio:
```powershell
.\start-windows.ps1
```

### Paso 3: Espera 10 segundos para que PostgreSQL inicie

### Paso 4: Ejecuta el script para crear usuarios

```powershell
cd backend
python scripts/add_test_users.py
```

## Usuarios Creados

Después de ejecutar el script, tendrás estos usuarios:

### 🔴 DIRECTOR
- **Email:** director@drtc.gob.pe
- **Password:** Director123!
- **Permisos:** Aprobar, habilitar, suspender habilitaciones

### 🟡 SUBDIRECTOR
- **Email:** subdirector@drtc.gob.pe
- **Password:** Subdirector123!
- **Permisos:** Aprobar, habilitar habilitaciones

### 🟢 OPERARIO
- **Email:** operario@drtc.gob.pe
- **Password:** Operario123!
- **Permisos:** Revisar, observar solicitudes

### 🔵 ADMIN (ya existe)
- **Email:** admin@drtc.gob.pe
- **Password:** Admin123!
- **Permisos:** Acceso completo

## Verificar que funcionan

1. Ve a http://localhost:3000/login
2. Prueba con cualquiera de los usuarios de arriba
3. Deberías poder iniciar sesión

## Si sigue sin funcionar

Ejecuta este comando para ver los logs:
```powershell
docker-compose logs backend
```

O reinicia todo:
```powershell
docker-compose down
docker-compose up -d
# Espera 10 segundos
cd backend
python scripts/add_test_users.py
```
