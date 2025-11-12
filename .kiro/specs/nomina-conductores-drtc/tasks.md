# Plan de Implementación - Sistema de Nómina de Conductores DRTC Puno

## Tareas de Implementación

- [x] 1. Configurar infraestructura base del proyecto


  - Crear estructura de directorios para frontend (Astro), backend (FastAPI) y configuración Docker
  - Configurar archivos Docker (Dockerfile para backend, Dockerfile para frontend, docker-compose.yml)
  - Crear archivo .env.example con todas las variables de entorno necesarias
  - Configurar Nginx como reverse proxy con rate limiting
  - _Requirements: 14.1, 14.2, 14.3, 14.4_



- [x] 2. Configurar base de datos PostgreSQL y modelos base






  - [x] 2.1 Configurar SQLAlchemy y Alembic para migraciones


    - Instalar dependencias (SQLAlchemy 2.0, Alembic, asyncpg)
    - Crear configuración de conexión a base de datos
    - Configurar Alembic para migraciones automáticas



    - Crear modelo base con campos comunes (id, created_at, updated_at)
    - _Requirements: 14.3_

  - [x] 2.2 Implementar modelo Usuario con roles

    - Crear modelo Usuario con campos: email, password_hash, nombres, apellidos, rol, activo
    - Implementar enum para roles (SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE)
    - Crear índices en email para búsquedas rápidas
    - Escribir tests unitarios para modelo Usuario
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_


  - [x] 2.3 Implementar modelos Empresa y TipoAutorizacion

    - Crear modelo Empresa con campos: ruc, razon_social, direccion, telefono, email, gerente_id, activo
    - Crear modelo TipoAutorizacion con tipos predefinidos (mercancías, turismo, trabajadores, especiales, estudiantes, residuos peligrosos)
    - Crear modelo AutorizacionEmpresa para relación muchos-a-muchos
    - Implementar validación de RUC (11 dígitos)
    - Escribir tests unitarios para modelos de Empresa
    - _Requirements: 2.1, 2.2, 2.3, 2.7_


  - [x] 2.4 Implementar modelo Conductor con validaciones

    - Crear modelo Conductor con todos los campos requeridos por MTC
    - Implementar enum para estados (PENDIENTE, HABILITADO, OBSERVADO, SUSPENDIDO, REVOCADO)
    - Crear validaciones para DNI (8 dígitos), licencia, fechas de vencimiento
    - Implementar índices en dni, licencia_numero, empresa_id, estado
    - Escribir tests unitarios incluyendo validaciones de categoría de licencia
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [x] 2.5 Implementar modelos Habilitacion y Pago



    - Crear modelo Habilitacion con estados del flujo de aprobación
    - Crear modelo Pago vinculado a Habilitacion
    - Crear modelo ConceptoTUPA con montos y vigencias
    - Implementar relaciones entre modelos
    - Escribir tests unitarios para flujo de habilitación
    - _Requirements: 4.1, 4.2, 4.8, 5.1, 5.2, 5.3_

  - [x] 2.6 Implementar modelos Infraccion y AsignacionVehiculo


    - Crear modelo Infraccion con tipo, gravedad y entidad fiscalizadora
    - Crear modelo TipoInfraccion con clasificación (LEVE, GRAVE, MUY_GRAVE)
    - Crear modelo AsignacionVehiculo para integración con sistema de vehículos
    - Implementar índices para consultas de historial
    - Escribir tests unitarios para infracciones
    - _Requirements: 6.1, 6.2, 6.3, 6.8, 12.7, 12.8_


  - [x] 2.7 Implementar modelos Auditoria y Notificacion

    - Crear modelo Auditoria para registro de todas las acciones críticas
    - Crear modelo Notificacion para alertas del sistema
    - Implementar triggers o listeners para auditoría automática
    - Escribir tests unitarios para auditoría
    - _Requirements: 10.1, 10.2, 10.3, 11.1, 11.2_

  - [x] 2.8 Crear migración inicial y poblar datos base


    - Generar migración inicial con todos los modelos
    - Crear script de seed para tipos de autorización predefinidos
    - Crear script de seed para tipos de infracción según normativa MTC
    - Crear usuario superusuario inicial
    - Ejecutar migraciones y verificar estructura de BD
    - _Requirements: 9.3_

- [x] 3. Implementar sistema de autenticación y autorización








  - [x] 3.1 Configurar JWT y seguridad



    - Instalar dependencias (python-jose, passlib, bcrypt)
    - Implementar funciones de hashing de contraseñas con bcrypt
    - Crear funciones para generar y verificar tokens JWT
    - Configurar tiempos de expiración (access: 30min, refresh: 7 días)
    - Escribir tests unitarios para funciones de seguridad
    - _Requirements: 1.1, 1.7_



  - [x] 3.2 Implementar endpoints de autenticación















    - Crear endpoint POST /api/v1/auth/login con validación de credenciales
    - Crear endpoint POST /api/v1/auth/refresh para renovar tokens
    - Crear endpoint POST /api/v1/auth/logout
    - Crear endpoint GET /api/v1/auth/me para obtener usuario actual
    - Implementar rate limiting en login (5 intentos por minuto)
    - Escribir tests de integración para flujo de autenticación


    - _Requirements: 1.1, 1.7_

  - [x] 3.3 Implementar sistema de control de acceso basado en roles (RBAC)





    - Crear decorador require_roles para proteger endpoints
    - Implementar dependency get_current_user con validación de token
    - Crear middleware para verificar permisos según rol
    - Implementar lógica para que Gerentes solo accedan a su empresa
    - Escribir tests unitarios para cada nivel de permisos
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 4. Implementar repositorios y servicios base




  - [x] 4.1 Crear patrón Repository base


    - Implementar clase BaseRepository con operaciones CRUD genéricas
    - Crear métodos: get_by_id, get_all, create, update, delete, exists
    - Implementar paginación y filtrado genérico
    - Escribir tests unitarios para BaseRepository
    - _Requirements: 12.4, 12.5_

  - [x] 4.2 Implementar repositorios específicos



    - Crear UsuarioRepository con método get_by_email
    - Crear EmpresaRepository con método get_by_ruc
    - Crear ConductorRepository con métodos de búsqueda avanzada
    - Crear HabilitacionRepository con filtros por estado
    - Crear InfraccionRepository con consultas de historial
    - Escribir tests unitarios para cada repositorio
    - _Requirements: 12.4_

- [x] 5. Implementar módulo de gestión de usuarios




  - [x] 5.1 Crear schemas Pydantic para Usuario


    - Crear UsuarioBase, UsuarioCreate, UsuarioUpdate, UsuarioResponse
    - Implementar validaciones de email, contraseña fuerte
    - Crear schema para cambio de contraseña
    - _Requirements: 1.2_

  - [x] 5.2 Implementar servicio UsuarioService


    - Crear método crear_usuario con hashing de contraseña
    - Crear método actualizar_usuario
    - Crear método cambiar_contraseña
    - Crear método activar/desactivar usuario
    - Escribir tests unitarios para UsuarioService
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_


  - [x] 5.3 Crear endpoints CRUD de usuarios

    - Implementar GET /api/v1/usuarios (solo SUPERUSUARIO, DIRECTOR)
    - Implementar POST /api/v1/usuarios (solo SUPERUSUARIO)
    - Implementar GET /api/v1/usuarios/{id}
    - Implementar PUT /api/v1/usuarios/{id}
    - Implementar DELETE /api/v1/usuarios/{id} (soft delete)
    - Escribir tests de integración para endpoints de usuarios
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 6. Implementar módulo de gestión de empresas







  - [x] 6.1 Crear schemas Pydantic para Empresa


    - Crear EmpresaBase, EmpresaCreate, EmpresaUpdate, EmpresaResponse
    - Implementar validación de RUC (11 dígitos)
    - Crear schema para AutorizacionEmpresa
    - _Requirements: 2.1, 2.2_

  - [x] 6.2 Implementar servicio EmpresaService


    - Crear método registrar_empresa con validación de RUC único
    - Crear método agregar_autorizacion con validación de tipo
    - Crear método obtener_empresas con filtros
    - Crear método obtener_conductores_empresa
    - Escribir tests unitarios para EmpresaService
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 6.3 Crear endpoints CRUD de empresas


    - Implementar GET /api/v1/empresas con paginación y filtros
    - Implementar POST /api/v1/empresas
    - Implementar GET /api/v1/empresas/{id}
    - Implementar PUT /api/v1/empresas/{id}
    - Implementar GET /api/v1/empresas/{id}/conductores
    - Implementar POST /api/v1/empresas/{id}/autorizaciones
    - Escribir tests de integración para endpoints de empresas
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_


- [-] 7. Implementar módulo de gestión de conductores




  - [x] 7.1 Crear schemas Pydantic para Conductor

    - Crear ConductorBase, ConductorCreate, ConductorUpdate, ConductorResponse
    - Implementar validaciones de DNI, licencia, fechas
    - Crear validator para verificar que licencia no esté vencida
    - Crear validator para categoría de licencia según tipo de autorización
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_


  - [x] 7.2 Implementar servicio ConductorService

    - Crear método registrar_conductor con validaciones completas
    - Crear método validar_categoria_licencia según tipo de autorización de empresa
    - Crear método actualizar_conductor
    - Crear método cambiar_estado_conductor
    - Crear método buscar_conductores con filtros múltiples
    - Escribir tests unitarios para ConductorService incluyendo validaciones
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_


  - [x] 7.3 Crear endpoints CRUD de conductores






    - Implementar GET /api/v1/conductores con paginación, filtros y búsqueda
    - Implementar POST /api/v1/conductores (solo Gerente de su empresa)
    - Implementar GET /api/v1/conductores/{id}
    - Implementar PUT /api/v1/conductores/{id}
    - Implementar DELETE /api/v1/conductores/{id} (soft delete)
    - Implementar GET /api/v1/conductores/{dni} para consulta por DNI
    - Escribir tests de integración para endpoints de conductores
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [ ] 7.4 Implementar gestión de documentos de conductores
    - Crear modelo DocumentoConductor para almacenar archivos adjuntos
    - Implementar endpoint POST /api/v1/conductores/{id}/documentos para subir archivos
    - Implementar validación de tipos de archivo (PDF, JPG, PNG)
    - Implementar límite de tamaño de archivo (10MB)
    - Implementar endpoint GET /api/v1/conductores/{id}/documentos/{doc_id} para descargar
    - Escribir tests para upload y download de documentos
    - _Requirements: 3.6, 3.7_

- [ ] 8. Implementar módulo de habilitaciones
  - [ ] 8.1 Crear schemas Pydantic para Habilitacion
    - Crear HabilitacionBase, HabilitacionCreate, HabilitacionResponse
    - Crear schema para revisión (HabilitacionReview)
    - Crear schema para observaciones (HabilitacionObservacion)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 8.2 Implementar servicio HabilitacionService
    - Crear método crear_solicitud que se ejecuta automáticamente al registrar conductor
    - Crear método obtener_solicitudes_pendientes
    - Crear método revisar_solicitud (cambiar a EN_REVISION)
    - Crear método aprobar_solicitud con validación de documentos
    - Crear método observar_solicitud con comentarios
    - Crear método habilitar_conductor con verificación de pago
    - Crear método suspender_habilitacion con justificación
    - Crear método revocar_habilitacion
    - Escribir tests unitarios para cada método del flujo
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

  - [ ] 8.3 Implementar generación de certificados de habilitación
    - Instalar librería para generación de PDFs (reportlab o weasyprint)
    - Crear plantilla HTML/CSS para certificado de habilitación
    - Implementar método generar_certificado en HabilitacionService
    - Incluir código QR con código de habilitación para verificación
    - Implementar endpoint GET /api/v1/habilitaciones/{id}/certificado
    - Escribir tests para generación de certificados
    - _Requirements: 4.9_

  - [ ] 8.4 Crear endpoints de habilitaciones
    - Implementar GET /api/v1/habilitaciones con filtros por estado
    - Implementar GET /api/v1/habilitaciones/pendientes (solo Operarios/Directores)
    - Implementar GET /api/v1/habilitaciones/{id}
    - Implementar POST /api/v1/habilitaciones/{id}/revisar
    - Implementar POST /api/v1/habilitaciones/{id}/aprobar
    - Implementar POST /api/v1/habilitaciones/{id}/observar
    - Implementar POST /api/v1/habilitaciones/{id}/habilitar
    - Implementar POST /api/v1/habilitaciones/{id}/suspender
    - Escribir tests de integración para flujo completo de habilitación
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

- [ ] 9. Implementar módulo de pagos TUPA
  - [ ] 9.1 Crear schemas Pydantic para Pago y ConceptoTUPA
    - Crear ConceptoTUPABase, ConceptoTUPACreate, ConceptoTUPAResponse
    - Crear PagoBase, PagoCreate, PagoResponse
    - Crear schema para orden de pago
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ] 9.2 Implementar servicio PagoService
    - Crear método calcular_monto_tupa según tipo de trámite
    - Crear método generar_orden_pago con código único
    - Crear método registrar_pago con validación de monto
    - Crear método verificar_pago_confirmado
    - Crear método generar_reporte_ingresos
    - Escribir tests unitarios para PagoService
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [ ] 9.3 Crear endpoints de pagos
    - Implementar GET /api/v1/pagos con filtros
    - Implementar POST /api/v1/pagos para registrar pago
    - Implementar GET /api/v1/pagos/{id}
    - Implementar GET /api/v1/pagos/habilitacion/{habilitacion_id}
    - Implementar GET /api/v1/pagos/{id}/orden-pago para descargar orden
    - Escribir tests de integración para endpoints de pagos
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 10. Implementar módulo de infracciones
  - [ ] 10.1 Crear schemas Pydantic para Infraccion
    - Crear TipoInfraccionBase, TipoInfraccionCreate
    - Crear InfraccionBase, InfraccionCreate, InfraccionUpdate, InfraccionResponse
    - Crear schema para historial de infracciones
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 10.2 Implementar servicio InfraccionService
    - Crear método registrar_infraccion con validaciones
    - Crear método obtener_historial_conductor
    - Crear método calcular_gravedad_acumulada
    - Crear método sugerir_sancion según infracciones acumuladas
    - Crear método actualizar_infraccion
    - Escribir tests unitarios para InfraccionService
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7, 6.8, 6.9_

  - [ ] 10.3 Crear endpoints de infracciones
    - Implementar GET /api/v1/infracciones con filtros
    - Implementar POST /api/v1/infracciones
    - Implementar GET /api/v1/infracciones/{id}
    - Implementar PUT /api/v1/infracciones/{id}
    - Implementar DELETE /api/v1/infracciones/{id}
    - Implementar GET /api/v1/infracciones/conductor/{conductor_id}
    - Escribir tests de integración para endpoints de infracciones
    - _Requirements: 6.1, 6.2, 6.3, 6.7, 6.8_

- [ ] 11. Implementar integración con sistemas externos
  - [ ] 11.1 Crear servicio IntegracionService base
    - Configurar cliente HTTP asíncrono (httpx)
    - Implementar manejo de errores y reintentos con exponential backoff
    - Implementar timeout y circuit breaker para APIs externas
    - Crear método base para autenticación con APIs externas
    - Escribir tests unitarios con mocks de APIs externas
    - _Requirements: 7.5, 7.6_

  - [ ] 11.2 Implementar integración con API del MTC
    - Crear método validar_licencia_mtc para verificar vigencia de licencia
    - Crear método consultar_infracciones_mtc
    - Implementar caché de respuestas para reducir llamadas
    - Implementar fallback a validación manual si API falla
    - Escribir tests con mocks de respuestas del MTC
    - _Requirements: 7.1, 7.2, 7.5_

  - [ ] 11.3 Implementar integración con API de SUNARP
    - Crear método consultar_antecedentes_sunarp
    - Implementar caché de consultas
    - Escribir tests con mocks de respuestas de SUNARP
    - _Requirements: 7.3, 7.5_

  - [ ] 11.4 Implementar sincronización periódica de infracciones
    - Crear tarea Celery para sincronizar infracciones diariamente
    - Implementar método sincronizar_infracciones que consulta MTC/SUNARP
    - Crear endpoint POST /api/v1/infracciones/sincronizar para sincronización manual
    - Implementar notificación cuando se detectan nuevas infracciones
    - Escribir tests para tarea de sincronización
    - _Requirements: 6.6, 7.4, 7.6_

- [ ] 12. Implementar endpoints para integración con sistema de vehículos
  - [ ] 12.1 Crear schemas para asignaciones vehículo-conductor
    - Crear AsignacionVehiculoBase, AsignacionVehiculoCreate, AsignacionVehiculoResponse
    - Crear schema para validación de compatibilidad
    - _Requirements: 12.1, 12.6, 12.7_

  - [ ] 12.2 Implementar servicio AsignacionService
    - Crear método validar_compatibilidad_conductor_vehiculo
    - Crear método crear_asignacion
    - Crear método obtener_asignaciones_conductor
    - Crear método desasignar_vehiculo
    - Escribir tests unitarios para AsignacionService
    - _Requirements: 12.6, 12.7, 12.8_

  - [ ] 12.3 Crear endpoints de asignaciones para sistema de vehículos
    - Implementar POST /api/v1/asignaciones
    - Implementar GET /api/v1/asignaciones
    - Implementar GET /api/v1/asignaciones/{id}
    - Implementar PUT /api/v1/asignaciones/{id}
    - Implementar DELETE /api/v1/asignaciones/{id}
    - Implementar POST /api/v1/validar-asignacion
    - Escribir tests de integración para endpoints de asignaciones
    - _Requirements: 12.6, 12.7, 12.8_

  - [ ] 12.4 Crear endpoints de consulta para sistema de vehículos
    - Implementar GET /api/v1/conductores/{dni}/habilitacion con estado y vigencia
    - Implementar GET /api/v1/conductores/{dni}/infracciones con historial completo
    - Implementar GET /api/v1/conductores/{dni}/vehiculos-asignados
    - Implementar GET /api/v1/empresas/{ruc}/conductores
    - Escribir tests de integración para endpoints de consulta
    - _Requirements: 12.2, 12.3, 12.4, 12.5, 12.8_

  - [ ] 12.5 Implementar autenticación JWT para API externa
    - Configurar autenticación con tokens JWT para sistema de vehículos
    - Implementar rate limiting específico (100 requests/minuto)
    - Crear documentación OpenAPI/Swagger para endpoints de integración
    - Escribir tests de autenticación y rate limiting
    - _Requirements: 12.1, 12.9, 12.10, 12.12_

- [ ] 13. Implementar módulo de reportes
  - [ ] 13.1 Crear schemas para reportes
    - Crear ReporteRequest con filtros personalizables
    - Crear ReporteResponse con datos y metadatos
    - Crear schemas para diferentes tipos de reportes
    - _Requirements: 8.1, 8.2_

  - [ ] 13.2 Implementar servicio ReporteService
    - Crear método generar_reporte_conductores_habilitados
    - Crear método generar_reporte_solicitudes_pendientes
    - Crear método generar_reporte_infracciones con estadísticas
    - Crear método generar_reporte_ingresos_tupa
    - Crear método calcular_estadisticas_dashboard
    - Escribir tests unitarios para ReporteService
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.6_

  - [ ] 13.3 Implementar exportación de reportes a PDF
    - Instalar librería para generación de PDFs
    - Crear plantillas HTML/CSS para diferentes tipos de reportes
    - Implementar método exportar_pdf en ReporteService
    - Incluir gráficos y tablas en PDFs
    - Escribir tests para exportación PDF
    - _Requirements: 8.3_

  - [ ] 13.4 Implementar exportación de reportes a Excel
    - Instalar librería para generación de Excel (openpyxl)
    - Implementar método exportar_excel en ReporteService
    - Incluir múltiples hojas para datos relacionados
    - Aplicar formato y estilos a celdas
    - Escribir tests para exportación Excel
    - _Requirements: 8.3_

  - [ ] 13.5 Crear endpoints de reportes
    - Implementar GET /api/v1/reportes/conductores-habilitados
    - Implementar GET /api/v1/reportes/solicitudes-pendientes
    - Implementar GET /api/v1/reportes/infracciones
    - Implementar GET /api/v1/reportes/ingresos-tupa
    - Implementar POST /api/v1/reportes/personalizado
    - Implementar GET /api/v1/reportes/{id}/export/pdf
    - Implementar GET /api/v1/reportes/{id}/export/excel
    - Escribir tests de integración para endpoints de reportes
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 14. Implementar módulo de configuración
  - [ ] 14.1 Crear schemas para configuración
    - Crear ConfiguracionTUPAUpdate
    - Crear TipoInfraccionCreate, TipoInfraccionUpdate
    - Crear ConfiguracionIntegracionUpdate
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ] 14.2 Implementar servicio ConfiguracionService
    - Crear método actualizar_tupa con validación de vigencia
    - Crear método gestionar_tipos_infraccion
    - Crear método configurar_integraciones con encriptación de credenciales
    - Crear método configurar_notificaciones
    - Escribir tests unitarios para ConfiguracionService
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [ ] 14.3 Crear endpoints de configuración
    - Implementar GET /api/v1/configuracion/tupa (solo SUPERUSUARIO, DIRECTOR)
    - Implementar PUT /api/v1/configuracion/tupa
    - Implementar GET /api/v1/configuracion/tipos-infraccion
    - Implementar POST /api/v1/configuracion/tipos-infraccion
    - Implementar PUT /api/v1/configuracion/tipos-infraccion/{id}
    - Implementar GET /api/v1/configuracion/integraciones
    - Implementar PUT /api/v1/configuracion/integraciones
    - Escribir tests de integración para endpoints de configuración
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_


- [ ] 15. Implementar módulo de auditoría
  - [ ] 15.1 Implementar servicio AuditoriaService
    - Crear método registrar_accion con captura automática de contexto
    - Crear método obtener_auditoria con filtros
    - Crear método exportar_logs_auditoria
    - Implementar middleware para auditoría automática de acciones críticas
    - Escribir tests unitarios para AuditoriaService
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ] 15.2 Crear endpoints de auditoría
    - Implementar GET /api/v1/auditoria (solo SUPERUSUARIO, DIRECTOR)
    - Implementar GET /api/v1/auditoria/usuario/{usuario_id}
    - Implementar GET /api/v1/auditoria/export
    - Escribir tests de integración para endpoints de auditoría
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [ ] 16. Implementar sistema de notificaciones
  - [ ] 16.1 Configurar Celery para tareas asíncronas
    - Instalar Celery y configurar con Redis como broker
    - Crear configuración de Celery con tareas programadas
    - Configurar Celery Beat para tareas periódicas
    - Escribir tests para configuración de Celery
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

  - [ ] 16.2 Implementar servicio NotificacionService
    - Configurar cliente SMTP para envío de emails
    - Crear método enviar_email con plantillas HTML
    - Crear método crear_notificacion_interna
    - Crear método marcar_notificacion_leida
    - Implementar cola de envío con Celery
    - Escribir tests unitarios para NotificacionService
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8_

  - [ ] 16.3 Crear plantillas de notificaciones
    - Crear plantilla para solicitud observada
    - Crear plantilla para conductor habilitado
    - Crear plantilla para licencia próxima a vencer
    - Crear plantilla para certificado médico vencido
    - Crear plantilla para infracción grave registrada
    - Crear plantilla para actualización de TUPA
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.7_

  - [ ] 16.4 Implementar tareas Celery de notificaciones
    - Crear tarea para notificar solicitud observada
    - Crear tarea para notificar conductor habilitado
    - Crear tarea programada para verificar licencias por vencer (semanal)
    - Crear tarea programada para verificar certificados vencidos (diario)
    - Crear tarea para notificar infracciones graves (inmediata)
    - Escribir tests para tareas de notificaciones
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

  - [ ] 16.5 Crear endpoints de notificaciones
    - Implementar GET /api/v1/notificaciones para usuario actual
    - Implementar PUT /api/v1/notificaciones/{id}/leer
    - Implementar GET /api/v1/notificaciones/no-leidas/count
    - Escribir tests de integración para endpoints de notificaciones
    - _Requirements: 11.8_

- [ ] 17. Implementar caché con Redis
  - [ ] 17.1 Configurar cliente Redis
    - Instalar redis-py con soporte async
    - Crear servicio CacheService con métodos get, set, delete, invalidate_pattern
    - Configurar tiempos de expiración por tipo de dato
    - Escribir tests unitarios para CacheService
    - _Requirements: Performance y optimización_

  - [ ] 17.2 Implementar caché en servicios críticos
    - Agregar caché a consultas de conductores por ID
    - Agregar caché a consultas de empresas
    - Agregar caché a respuestas de APIs externas (MTC, SUNARP)
    - Implementar invalidación de caché al actualizar datos
    - Escribir tests para verificar funcionamiento de caché
    - _Requirements: Performance y optimización_

- [ ] 18. Implementar manejo de errores y logging
  - [ ] 18.1 Crear jerarquía de excepciones personalizadas
    - Crear clase base DRTCException
    - Crear excepciones específicas: RecursoNoEncontrado, PermisosDenegados, ValidacionError, IntegracionExternaError
    - Implementar handler global de excepciones en FastAPI
    - Escribir tests para manejo de excepciones
    - _Requirements: Manejo de errores_

  - [ ] 18.2 Configurar sistema de logging
    - Configurar logging con RotatingFileHandler
    - Implementar diferentes niveles de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Crear logs estructurados con contexto (usuario, IP, timestamp)
    - Configurar logging en todos los servicios
    - _Requirements: Manejo de errores, 10.5_

- [ ] 19. Implementar seguridad adicional
  - [ ] 19.1 Configurar CORS
    - Implementar middleware CORS con orígenes permitidos
    - Configurar métodos y headers permitidos
    - Escribir tests para verificar CORS
    - _Requirements: Seguridad_

  - [ ] 19.2 Implementar rate limiting
    - Instalar slowapi para rate limiting
    - Configurar límites globales (10 req/s)
    - Configurar límites específicos para login (5 req/min)
    - Configurar límites para API externa (100 req/min)
    - Escribir tests para rate limiting
    - _Requirements: 12.12, Seguridad_

  - [ ] 19.3 Implementar validación y sanitización de inputs
    - Configurar validación automática con Pydantic
    - Implementar sanitización de strings para prevenir XSS
    - Validar tipos de archivo en uploads
    - Implementar límites de tamaño en requests
    - Escribir tests de seguridad
    - _Requirements: Seguridad_

- [ ] 20. Crear frontend con Astro
  - [ ] 20.1 Configurar proyecto Astro
    - Inicializar proyecto Astro con TypeScript
    - Instalar dependencias: React, TailwindCSS, Axios
    - Configurar TailwindCSS con tema personalizado
    - Crear estructura de directorios (components, layouts, pages, services, stores)
    - _Requirements: 13.1, 13.2_

  - [ ] 20.2 Crear layouts base
    - Crear MainLayout con header, sidebar y footer
    - Crear AuthLayout para páginas de autenticación
    - Crear DashboardLayout con navegación por roles
    - Implementar responsive design
    - _Requirements: 13.1, 13.2, 13.6_

  - [ ] 20.3 Implementar servicio API cliente
    - Crear servicio api.ts con configuración de Axios
    - Implementar interceptores para agregar token JWT
    - Implementar manejo de errores global
    - Implementar refresh automático de tokens
    - _Requirements: 13.3_

  - [ ] 20.4 Implementar store de autenticación
    - Crear authStore con Zustand o Context API
    - Implementar métodos login, logout, refreshToken
    - Implementar persistencia de sesión
    - Crear hook useAuth para acceso al store
    - _Requirements: 1.1, 1.7_

- [ ] 21. Implementar módulo de autenticación en frontend
  - [ ] 21.1 Crear componentes de autenticación
    - Crear LoginForm.tsx con validación de formulario
    - Crear AuthGuard.tsx para protección de rutas
    - Crear RoleBasedAccess.tsx para renderizado condicional
    - Implementar redirección según rol después de login
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [ ] 21.2 Crear páginas de autenticación
    - Crear página /login con formulario de inicio de sesión
    - Implementar validación en tiempo real
    - Mostrar mensajes de error claros
    - Implementar loading states
    - _Requirements: 1.1, 13.3_

- [ ] 22. Implementar módulo de conductores en frontend
  - [ ] 22.1 Crear componentes de conductores
    - Crear ConductorList.tsx con tabla paginada
    - Crear ConductorForm.tsx con validaciones
    - Crear ConductorDetail.tsx con tabs para información
    - Crear ConductorStatus.tsx con badges de estado
    - Crear DocumentUpload.tsx para subir archivos
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 13.3, 13.4, 13.5_

  - [ ] 22.2 Crear páginas de conductores
    - Crear página /conductores con listado y filtros
    - Crear página /conductores/nuevo con formulario
    - Crear página /conductores/{id} con detalle completo
    - Crear página /conductores/{id}/editar
    - Implementar búsqueda en tiempo real
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 13.4_

- [ ] 23. Implementar módulo de empresas en frontend
  - [ ] 23.1 Crear componentes de empresas
    - Crear EmpresaList.tsx con tabla
    - Crear EmpresaForm.tsx con selección de autorizaciones
    - Crear EmpresaDetail.tsx con conductores asociados
    - Crear AutorizacionSelector.tsx para múltiples autorizaciones
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ] 23.2 Crear páginas de empresas
    - Crear página /empresas con listado
    - Crear página /empresas/nueva con formulario
    - Crear página /empresas/{id} con detalle
    - Crear página /empresas/{id}/editar
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [ ] 24. Implementar módulo de habilitaciones en frontend
  - [ ] 24.1 Crear componentes de habilitaciones
    - Crear HabilitacionQueue.tsx con cola de solicitudes
    - Crear HabilitacionReview.tsx con interfaz de revisión
    - Crear HabilitacionTimeline.tsx con historial de estados
    - Crear ObservacionModal.tsx para agregar observaciones
    - Crear CertificadoViewer.tsx para visualizar certificados
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

  - [ ] 24.2 Crear páginas de habilitaciones
    - Crear página /habilitaciones con listado
    - Crear página /habilitaciones/pendientes para Operarios
    - Crear página /habilitaciones/{id} con detalle y acciones
    - Implementar flujo completo de revisión y aprobación
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10_

- [ ] 25. Implementar módulo de infracciones en frontend
  - [ ] 25.1 Crear componentes de infracciones
    - Crear InfraccionList.tsx con filtros por gravedad
    - Crear InfraccionForm.tsx con clasificación
    - Crear InfraccionTimeline.tsx con historial visual
    - Crear GravedadBadge.tsx con colores según gravedad
    - _Requirements: 6.1, 6.2, 6.3, 6.7, 6.8_

  - [ ] 25.2 Crear páginas de infracciones
    - Crear página /infracciones con listado
    - Crear página /infracciones/nueva con formulario
    - Crear página /infracciones/{id} con detalle
    - Integrar historial en página de detalle de conductor
    - _Requirements: 6.1, 6.2, 6.3, 6.7, 6.8_

- [ ] 26. Implementar módulo de reportes en frontend
  - [ ] 26.1 Crear componentes de reportes
    - Crear ReportBuilder.tsx con filtros personalizables
    - Crear ReportViewer.tsx con tablas y gráficos
    - Crear ChartComponent.tsx con Chart.js o Recharts
    - Crear ExportButtons.tsx para PDF/Excel
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 26.2 Crear páginas de reportes
    - Crear página /reportes con reportes predefinidos
    - Crear página /reportes/personalizado con constructor
    - Crear página /dashboard con estadísticas principales
    - Implementar gráficos interactivos
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 27. Implementar módulo de configuración en frontend
  - [ ] 27.1 Crear componentes de configuración
    - Crear TUPAConfig.tsx para gestionar montos
    - Crear InfraccionTypeConfig.tsx para tipos de infracciones
    - Crear IntegracionConfig.tsx para APIs externas
    - Crear NotificacionConfig.tsx para plantillas
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.6_

  - [ ] 27.2 Crear páginas de configuración
    - Crear página /configuracion con tabs por sección
    - Implementar solo acceso para SUPERUSUARIO y DIRECTOR
    - Agregar confirmaciones para cambios críticos
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [ ] 28. Implementar notificaciones en frontend
  - [ ] 28.1 Crear componentes de notificaciones
    - Crear NotificationBell.tsx con contador de no leídas
    - Crear NotificationList.tsx con dropdown
    - Crear NotificationItem.tsx con acciones
    - Implementar actualización en tiempo real con polling o WebSockets
    - _Requirements: 11.8_

  - [ ] 28.2 Integrar notificaciones en layout
    - Agregar NotificationBell en header
    - Implementar sonido/vibración para notificaciones importantes
    - Crear página /notificaciones con historial completo
    - _Requirements: 11.8_

- [ ] 29. Implementar accesibilidad y UX
  - [ ] 29.1 Implementar accesibilidad WCAG 2.1 AA
    - Agregar atributos ARIA en componentes interactivos
    - Implementar navegación por teclado
    - Asegurar contraste de colores adecuado
    - Agregar textos alternativos en imágenes
    - Probar con lectores de pantalla
    - _Requirements: 13.6_

  - [ ] 29.2 Mejorar experiencia de usuario
    - Implementar loading skeletons
    - Agregar animaciones suaves con Framer Motion
    - Implementar confirmaciones para acciones destructivas
    - Agregar tooltips informativos
    - Optimizar formularios con autocompletado
    - _Requirements: 13.3, 13.7, 13.8_

- [ ] 30. Escribir tests para frontend
  - [ ] 30.1 Configurar entorno de testing
    - Instalar Vitest y Testing Library
    - Configurar mocks para API
    - Crear utilities de testing
    - _Requirements: Testing_

  - [ ] 30.2 Escribir tests unitarios de componentes
    - Escribir tests para componentes de formularios
    - Escribir tests para componentes de listados
    - Escribir tests para validaciones
    - Alcanzar cobertura mínima del 70%
    - _Requirements: Testing_

  - [ ] 30.3 Escribir tests E2E con Playwright
    - Escribir test para flujo de login
    - Escribir test para flujo de registro de conductor
    - Escribir test para flujo de habilitación completo
    - Escribir test para generación de reportes
    - _Requirements: Testing_

- [ ] 31. Optimizar y finalizar backend
  - [ ] 31.1 Implementar health checks
    - Crear endpoint /health básico
    - Crear endpoint /health/detailed con verificación de servicios
    - Implementar verificación de BD, Redis, APIs externas
    - _Requirements: 14.9_

  - [ ] 31.2 Implementar métricas con Prometheus
    - Instalar prometheus-client
    - Crear contadores para requests, habilitaciones, errores
    - Crear histogramas para duración de requests
    - Exponer endpoint /metrics
    - _Requirements: Monitoreo_

  - [ ] 31.3 Optimizar queries de base de datos
    - Revisar y optimizar queries N+1
    - Agregar eager loading donde sea necesario
    - Verificar uso correcto de índices
    - Implementar paginación en todas las listas
    - _Requirements: Performance_

  - [ ] 31.4 Generar documentación OpenAPI completa
    - Agregar descripciones detalladas en todos los endpoints
    - Documentar schemas con ejemplos
    - Agregar tags para organización
    - Documentar códigos de error
    - Verificar documentación en /docs
    - _Requirements: 12.10_

- [ ] 32. Finalizar configuración Docker
  - [ ] 32.1 Optimizar Dockerfiles
    - Implementar multi-stage builds
    - Minimizar tamaño de imágenes
    - Configurar .dockerignore
    - _Requirements: 14.11_

  - [ ] 32.2 Crear docker-compose para desarrollo
    - Crear docker-compose.dev.yml con hot-reload
    - Configurar volúmenes para desarrollo
    - Agregar servicios de desarrollo (pgAdmin, Redis Commander)
    - _Requirements: 14.10_

  - [ ] 32.3 Crear docker-compose para producción
    - Configurar variables de entorno de producción
    - Implementar health checks en todos los servicios
    - Configurar restart policies
    - Configurar límites de recursos
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8, 14.9_

  - [ ] 32.4 Crear scripts de despliegue
    - Crear script de inicialización de BD
    - Crear script de seed de datos iniciales
    - Crear script de backup de BD
    - Documentar proceso de despliegue en README
    - _Requirements: 14.12_

- [ ] 33. Documentación y entrega
  - [ ] 33.1 Crear documentación técnica
    - Documentar arquitectura del sistema
    - Documentar modelos de datos
    - Documentar flujos principales
    - Documentar APIs y endpoints
    - _Requirements: Todos_

  - [ ] 33.2 Crear documentación de usuario
    - Crear manual de usuario para Gerentes
    - Crear manual de usuario para Operarios
    - Crear manual de usuario para Directores
    - Crear guía de configuración para Superusuarios
    - _Requirements: Todos_

  - [ ] 33.3 Crear README completo
    - Documentar requisitos del sistema
    - Documentar instalación con Docker
    - Documentar configuración de variables de entorno
    - Documentar comandos útiles
    - Agregar troubleshooting común
    - _Requirements: 14.12_

  - [ ] 33.4 Preparar entrega
    - Verificar que todos los tests pasen
    - Verificar que la aplicación funcione end-to-end
    - Crear release notes
    - Preparar demo del sistema
    - _Requirements: Todos_

