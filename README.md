# Sistema de Nómina de Conductores DRTC Puno

Sistema de gestión de nómina de conductores para la Dirección Regional de Transportes y Comunicaciones de Puno, Perú.

## 🚀 Características

- **Gestión Multi-Nivel de Usuarios**: Superusuario, Directores, Subdirectores, Operarios y Gerentes de Empresa
- **Registro de Conductores**: Conforme a normativas del MTC
- **Proceso de Habilitación**: Flujo completo de aprobación y validación
- **Gestión de Pagos TUPA**: Control de pagos y habilitaciones
- **Historial de Infracciones**: Seguimiento completo de sanciones
- **Integración Externa**: Conexión con MTC, SUNARP y sistema de vehículos
- **Reportes y Estadísticas**: Análisis y exportación en PDF/Excel
- **API REST Completa**: Para integración con otros sistemas
- **Dockerizado**: Despliegue fácil y escalable

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI 0.109+** - Framework web moderno y rápido
- **Python 3.12** - Lenguaje de programación
- **PostgreSQL 16** - Base de datos relacional
- **SQLAlchemy 2.0** - ORM
- **Alembic** - Migraciones de base de datos
- **Redis 7** - Caché y cola de tareas
- **Celery** - Tareas asíncronas
- **JWT** - Autenticación

### Frontend
- **Astro 4.2+** - Framework web moderno
- **React 18** - Componentes interactivos
- **TypeScript** - Type safety
- **TailwindCSS 3.4** - Estilos
- **Zustand** - State management

### Infraestructura
- **Docker & Docker Compose** - Contenedorización
- **Nginx** - Reverse proxy
- **Gunicorn/Uvicorn** - Servidor ASGI

## 📋 Requisitos Previos

- Docker 24.0+
- Docker Compose 2.20+
- Git

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd nomina-conductores-drtc
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` y configurar las variables necesarias:

```env
# Base de datos
POSTGRES_DB=drtc_nomina
POSTGRES_USER=drtc_user
POSTGRES_PASSWORD=tu_password_seguro

# Backend
SECRET_KEY=tu_secret_key_de_al_menos_32_caracteres
ENVIRONMENT=development

# Email (opcional para desarrollo)
SMTP_HOST=smtp.gmail.com
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password

# APIs externas (opcional para desarrollo)
MTC_API_KEY=tu_api_key_mtc
SUNARP_API_KEY=tu_api_key_sunarp
```

### 3. Iniciar servicios con Docker

#### Desarrollo

```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

#### Producción

```bash
docker-compose up -d
```

### 4. Ejecutar migraciones de base de datos

```bash
# Entrar al contenedor del backend
docker exec -it drtc-backend bash

# Ejecutar migraciones
alembic upgrade head

# Crear usuario superusuario inicial
python -m app.scripts.create_superuser
```

Para más información sobre migraciones y configuración de base de datos, ver [DATABASE_SETUP.md](backend/DATABASE_SETUP.md)

## 🌐 Acceso a la Aplicación

Una vez iniciados los servicios:

- **Frontend**: http://localhost (puerto 80)
- **Backend API**: http://localhost/api
- **Documentación API**: http://localhost/docs
- **PgAdmin** (dev): http://localhost:5050
- **Redis Commander** (dev): http://localhost:8081

### Credenciales por defecto (desarrollo)

- **Superusuario**: 
  - Email: admin@drtc-puno.gob.pe
  - Password: admin123 (cambiar en producción)

- **PgAdmin**:
  - Email: admin@drtc.local
  - Password: admin

## 📁 Estructura del Proyecto

```
nomina-conductores-drtc/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints API
│   │   ├── core/           # Configuración y utilidades
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Schemas Pydantic
│   │   ├── services/       # Lógica de negocio
│   │   ├── repositories/   # Acceso a datos
│   │   ├── tasks/          # Tareas Celery
│   │   └── utils/          # Utilidades
│   ├── alembic/            # Migraciones
│   ├── tests/              # Tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Frontend Astro
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── layouts/       # Layouts Astro
│   │   ├── pages/         # Páginas
│   │   ├── services/      # Servicios API
│   │   ├── stores/        # State management
│   │   └── utils/         # Utilidades
│   ├── public/            # Archivos estáticos
│   ├── Dockerfile
│   └── package.json
├── nginx/                 # Configuración Nginx
│   └── nginx.conf
├── .kiro/                 # Especificaciones del proyecto
│   └── specs/
├── docker-compose.yml     # Configuración Docker
├── docker-compose.dev.yml # Configuración desarrollo
└── README.md
```

## 🧪 Testing

### Backend

```bash
# Entrar al contenedor
docker exec -it drtc-backend bash

# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/services/test_conductor_service.py
```

### Frontend

```bash
# Entrar al contenedor
docker exec -it drtc-frontend sh

# Ejecutar tests
npm test

# Tests E2E
npm run test:e2e
```

## 📚 Documentación

- **API Documentation**: Disponible en `/docs` (Swagger UI)
- **Especificaciones**: Ver carpeta `.kiro/specs/`
- **Requisitos**: `.kiro/specs/nomina-conductores-drtc/requirements.md`
- **Diseño**: `.kiro/specs/nomina-conductores-drtc/design.md`
- **Tareas**: `.kiro/specs/nomina-conductores-drtc/tasks.md`

## 🔧 Comandos Útiles

### Docker

```bash
# Reconstruir imágenes
docker-compose build

# Ver logs de un servicio específico
docker-compose logs -f backend

# Reiniciar un servicio
docker-compose restart backend

# Limpiar todo (¡cuidado en producción!)
docker-compose down -v
```

### Base de Datos

```bash
# Backup
docker exec drtc-postgres pg_dump -U drtc_user drtc_nomina > backup.sql

# Restore
docker exec -i drtc-postgres psql -U drtc_user drtc_nomina < backup.sql

# Acceder a PostgreSQL
docker exec -it drtc-postgres psql -U drtc_user -d drtc_nomina
```

### Celery

```bash
# Ver tareas activas
docker exec -it drtc-celery-worker celery -A app.tasks.celery_app inspect active

# Ver tareas programadas
docker exec -it drtc-celery-beat celery -A app.tasks.celery_app inspect scheduled
```

## 🐛 Troubleshooting

### El backend no inicia

1. Verificar que PostgreSQL esté corriendo: `docker-compose ps`
2. Ver logs: `docker-compose logs backend`
3. Verificar variables de entorno en `.env`

### Error de conexión a base de datos

1. Verificar que el servicio postgres esté healthy: `docker-compose ps`
2. Verificar credenciales en `.env`
3. Reiniciar servicios: `docker-compose restart`

### Frontend no carga

1. Verificar que el backend esté corriendo
2. Verificar `PUBLIC_API_URL` en `.env`
3. Ver logs: `docker-compose logs frontend`

### Problemas con migraciones

```bash
# Resetear migraciones (¡cuidado!)
docker exec -it drtc-backend alembic downgrade base
docker exec -it drtc-backend alembic upgrade head
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Licencia

Este proyecto es propiedad de la Dirección Regional de Transportes y Comunicaciones de Puno.

## 👥 Contacto

DRTC Puno - [@drtcpuno](https://twitter.com/drtcpuno)

Proyecto Link: [https://github.com/drtc-puno/nomina-conductores](https://github.com/drtc-puno/nomina-conductores)

## 🙏 Agradecimientos

- Ministerio de Transportes y Comunicaciones (MTC)
- SUNARP
- Gobierno Regional de Puno
