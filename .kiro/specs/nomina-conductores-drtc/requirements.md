# Documento de Requisitos - Sistema de Nómina de Conductores DRTC Puno

## Introducción

El Sistema de Nómina de Conductores DRTC Puno es una aplicación web gubernamental diseñada para gestionar el registro, habilitación y seguimiento de conductores de transporte en la región de Puno, Perú. El sistema permite a empresas de transporte registrar sus conductores según normativas del MTC (Ministerio de Transportes y Comunicaciones), mientras que los administradores de la DRTC (Dirección Regional de Transportes y Comunicaciones) validan y habilitan estos registros conforme al TUPA vigente.

El sistema integra múltiples niveles de usuarios (Superusuario, Directores, Subdirectores, Operarios y Gerentes de Empresa), gestiona diferentes tipos de autorizaciones de transporte (mercancías, turismo, trabajadores, especiales, estudiantes, residuos peligrosos), y mantiene un historial completo de infracciones y sanciones de cada conductor basado en datos del MTC, SUNARP y otros entes fiscalizadores.

## Requisitos

### Requisito 1: Gestión de Autenticación y Autorización Multi-Nivel

**Historia de Usuario:** Como administrador del sistema, quiero un sistema de autenticación robusto con diferentes niveles de acceso, para que cada tipo de usuario tenga permisos específicos según su rol en la organización.

#### Criterios de Aceptación

1. CUANDO un usuario intenta acceder al sistema ENTONCES el sistema SHALL solicitar credenciales válidas (usuario y contraseña)
2. CUANDO un usuario se autentica exitosamente ENTONCES el sistema SHALL asignar permisos basados en su rol (Superusuario, Director, Subdirector, Operario, Gerente de Empresa)
3. IF el usuario es Superusuario THEN el sistema SHALL otorgar acceso completo a todas las funcionalidades incluyendo configuración del sistema
4. IF el usuario es Director o Subdirector THEN el sistema SHALL permitir visualización completa, habilitación de nóminas, y cambios importantes en registros
5. IF el usuario es Operario THEN el sistema SHALL permitir funciones de validación y procesamiento de solicitudes sin autorización para cambios críticos
6. IF el usuario es Gerente de Empresa THEN el sistema SHALL limitar el acceso únicamente a la gestión de conductores de su propia empresa
7. WHEN un usuario intenta acceder a una función no autorizada THEN el sistema SHALL denegar el acceso y registrar el intento
8. WHEN un usuario permanece inactivo por más de 30 minutos THEN el sistema SHALL cerrar la sesión automáticamente por seguridad

### Requisito 2: Registro de Empresas de Transporte

**Historia de Usuario:** Como Gerente de Empresa de transporte, quiero registrar mi empresa en el sistema con todas sus autorizaciones vigentes, para poder gestionar la nómina de mis conductores conforme a la normativa regional.

#### Criterios de Aceptación

1. WHEN un Gerente registra una empresa THEN el sistema SHALL solicitar RUC, razón social, dirección, representante legal, y datos de contacto
2. WHEN se registra una empresa THEN el sistema SHALL permitir seleccionar uno o múltiples tipos de autorización (mercancías, turismo, trabajadores, especiales, estudiantes, residuos peligrosos)
3. IF la empresa transporta residuos peligrosos THEN el sistema SHALL requerir certificaciones adicionales específicas
4. WHEN se completa el registro THEN el sistema SHALL asignar un código único de empresa
5. WHEN un Director o Operario revisa empresas THEN el sistema SHALL mostrar todas las empresas registradas con sus autorizaciones
6. WHEN un Gerente accede al sistema THEN el sistema SHALL mostrar únicamente la información de su empresa asignada
7. IF una empresa tiene múltiples autorizaciones THEN el sistema SHALL permitir gestionar conductores específicos para cada tipo de autorización

### Requisito 3: Registro de Conductores según Normativa MTC

**Historia de Usuario:** Como Gerente de Empresa, quiero registrar los datos completos de mis conductores según los reglamentos del MTC, para cumplir con la normativa de transporte regional.

#### Criterios de Aceptación

1. WHEN un Gerente registra un conductor THEN el sistema SHALL solicitar: DNI, nombres completos, fecha de nacimiento, dirección, teléfono, correo electrónico
2. WHEN se registra un conductor THEN el sistema SHALL requerir: número de licencia de conducir, categoría, fecha de emisión, fecha de vencimiento
3. WHEN se ingresa la licencia THEN el sistema SHALL validar que la categoría sea apropiada para el tipo de autorización de la empresa
4. IF el tipo de autorización es transporte de pasajeros THEN el sistema SHALL requerir licencia categoría A-IIb, A-IIIa, A-IIIb o A-IIIc
5. IF el tipo de autorización es transporte de carga THEN el sistema SHALL requerir licencia categoría A-IIIb o A-IIIc
6. WHEN se registra un conductor THEN el sistema SHALL solicitar certificado de antecedentes penales, policiales y judiciales
7. WHEN se registra un conductor THEN el sistema SHALL requerir certificado médico vigente (examen psicosomático)
8. WHEN se completa el registro THEN el sistema SHALL guardar el conductor en estado "Pendiente de Habilitación"
9. WHEN un Gerente visualiza sus conductores THEN el sistema SHALL mostrar el estado actual de cada conductor (Pendiente, Habilitado, Observado, Suspendido)

### Requisito 4: Proceso de Habilitación de Conductores por DRTC

**Historia de Usuario:** Como Director/Operario de DRTC, quiero revisar y habilitar las solicitudes de registro de conductores, para asegurar que cumplan con todos los requisitos legales antes de autorizar su operación.

#### Criterios de Aceptación

1. WHEN un Director u Operario accede al módulo de habilitación THEN el sistema SHALL mostrar todas las solicitudes pendientes de revisión
2. WHEN se selecciona una solicitud THEN el sistema SHALL mostrar todos los documentos y datos del conductor para verificación
3. WHEN se revisa una solicitud THEN el sistema SHALL permitir verificar la validez de la licencia de conducir contra base de datos del MTC
4. IF todos los documentos son válidos THEN el sistema SHALL permitir marcar la solicitud como "Aprobada"
5. IF faltan documentos o hay inconsistencias THEN el sistema SHALL permitir marcar la solicitud como "Observada" con comentarios específicos
6. WHEN una solicitud es observada THEN el sistema SHALL notificar al Gerente de Empresa sobre las observaciones
7. WHEN una solicitud es aprobada THEN el sistema SHALL verificar que el pago según TUPA esté registrado antes de habilitar
8. IF el pago está confirmado THEN el sistema SHALL cambiar el estado del conductor a "Habilitado" y generar un código de habilitación único
9. WHEN un conductor es habilitado THEN el sistema SHALL generar un certificado de habilitación en formato PDF descargable
10. WHEN un Director revisa habilitaciones THEN el sistema SHALL permitir suspender o revocar habilitaciones con justificación documentada

### Requisito 5: Gestión de Pagos según TUPA

**Historia de Usuario:** Como Operario de DRTC, quiero registrar y validar los pagos realizados por las empresas según el TUPA vigente, para controlar que las habilitaciones se otorguen solo cuando el pago esté confirmado.

#### Criterios de Aceptación

1. WHEN se accede al módulo de configuración THEN el sistema SHALL permitir al Superusuario o Director definir los montos del TUPA por tipo de trámite
2. WHEN una empresa solicita habilitar conductores THEN el sistema SHALL calcular automáticamente el monto a pagar según TUPA
3. WHEN se genera una solicitud de habilitación THEN el sistema SHALL generar un código de pago único y una orden de pago descargable
4. WHEN un Operario registra un pago THEN el sistema SHALL solicitar: número de recibo, fecha de pago, monto, entidad bancaria
5. WHEN se registra un pago THEN el sistema SHALL validar que el monto coincida con lo calculado según TUPA
6. IF el pago es válido THEN el sistema SHALL marcar la solicitud como "Pago Confirmado" y permitir la habilitación
7. WHEN un Director consulta pagos THEN el sistema SHALL generar reportes de ingresos por concepto de habilitaciones
8. WHEN se actualiza el TUPA THEN el sistema SHALL aplicar los nuevos montos solo a solicitudes posteriores a la fecha de actualización

### Requisito 6: Historial de Infracciones y Sanciones

**Historia de Usuario:** Como Director de DRTC, quiero consultar el historial completo de infracciones y sanciones de cada conductor, para tomar decisiones informadas sobre habilitaciones y renovaciones.

#### Criterios de Aceptación

1. WHEN se consulta un conductor THEN el sistema SHALL mostrar un historial completo de infracciones registradas
2. WHEN se registra una infracción THEN el sistema SHALL solicitar: fecha, tipo de infracción, gravedad (leve, grave, muy grave), descripción, entidad fiscalizadora
3. WHEN se registra una infracción THEN el sistema SHALL permitir adjuntar documentos de respaldo (actas, resoluciones)
4. IF la infracción es "muy grave" THEN el sistema SHALL alertar automáticamente a los Directores para revisión
5. WHEN se acumulan infracciones graves THEN el sistema SHALL sugerir suspensión temporal o revocación de habilitación
6. WHEN se integra con sistemas externos THEN el sistema SHALL permitir importar infracciones desde MTC, SUNARP y otros entes fiscalizadores
7. WHEN un Gerente consulta sus conductores THEN el sistema SHALL mostrar un indicador visual del estado de infracciones (sin infracciones, infracciones leves, infracciones graves)
8. WHEN se genera un reporte THEN el sistema SHALL incluir estadísticas de infracciones por empresa, tipo de transporte y período
9. IF un conductor tiene infracciones pendientes de sanción THEN el sistema SHALL impedir renovaciones hasta que se resuelvan

### Requisito 7: Integración con Sistemas Externos (MTC, SUNARP)

**Historia de Usuario:** Como Operario de DRTC, quiero que el sistema consulte automáticamente datos de conductores en sistemas del MTC y SUNARP, para validar información sin procesos manuales.

#### Criterios de Aceptación

1. WHEN se registra una licencia de conducir THEN el sistema SHALL consultar la API del MTC para validar vigencia y autenticidad
2. IF la licencia está vencida o suspendida en MTC THEN el sistema SHALL rechazar automáticamente el registro
3. WHEN se valida un conductor THEN el sistema SHALL consultar SUNARP para verificar antecedentes vehiculares si aplica
4. WHEN se consultan infracciones THEN el sistema SHALL sincronizar periódicamente con bases de datos de entes fiscalizadores
5. IF la integración falla THEN el sistema SHALL permitir validación manual con registro de auditoría
6. WHEN se detectan cambios en datos externos THEN el sistema SHALL notificar a los administradores sobre actualizaciones relevantes
7. WHEN se configura integración THEN el sistema SHALL permitir al Superusuario configurar endpoints, credenciales y frecuencia de sincronización

### Requisito 8: Reportes y Estadísticas

**Historia de Usuario:** Como Director de DRTC, quiero generar reportes detallados sobre conductores, empresas e infracciones, para análisis y toma de decisiones estratégicas.

#### Criterios de Aceptación

1. WHEN se accede al módulo de reportes THEN el sistema SHALL ofrecer reportes predefinidos: conductores habilitados, solicitudes pendientes, infracciones por período, ingresos por TUPA
2. WHEN se genera un reporte THEN el sistema SHALL permitir filtrar por: empresa, tipo de autorización, rango de fechas, estado de conductor
3. WHEN se solicita un reporte THEN el sistema SHALL generar el documento en formatos PDF y Excel
4. WHEN se consultan estadísticas THEN el sistema SHALL mostrar gráficos de: conductores por empresa, distribución por tipo de autorización, tendencia de infracciones
5. WHEN un Gerente accede a reportes THEN el sistema SHALL limitar los reportes únicamente a datos de su empresa
6. WHEN se genera un reporte de infracciones THEN el sistema SHALL incluir detalles de gravedad, frecuencia y conductores reincidentes
7. WHEN se solicita un reporte de auditoría THEN el sistema SHALL incluir todos los cambios realizados con usuario, fecha y hora

### Requisito 9: Módulo de Configuración del Sistema

**Historia de Usuario:** Como Superusuario, quiero configurar parámetros del sistema como TUPA, tipos de infracciones y integraciones, para mantener el sistema actualizado según cambios normativos.

#### Criterios de Aceptación

1. WHEN se accede a configuración THEN el sistema SHALL permitir solo a Superusuarios y Directores modificar parámetros críticos
2. WHEN se configura TUPA THEN el sistema SHALL permitir definir montos por tipo de trámite con fecha de vigencia
3. WHEN se configuran infracciones THEN el sistema SHALL permitir crear, editar y eliminar tipos de infracciones con su clasificación de gravedad
4. WHEN se configuran integraciones THEN el sistema SHALL permitir definir URLs, credenciales y parámetros de APIs externas
5. WHEN se modifica una configuración THEN el sistema SHALL registrar el cambio en auditoría con usuario y timestamp
6. WHEN se configuran notificaciones THEN el sistema SHALL permitir definir plantillas de correo y eventos que disparan notificaciones
7. WHEN se configura el sistema THEN el sistema SHALL permitir definir períodos de vigencia de documentos (licencias, certificados médicos)

### Requisito 10: Auditoría y Trazabilidad

**Historia de Usuario:** Como Director de DRTC, quiero que todas las acciones críticas del sistema queden registradas, para garantizar transparencia y cumplimiento normativo.

#### Criterios de Aceptación

1. WHEN un usuario realiza una acción crítica THEN el sistema SHALL registrar: usuario, fecha/hora, acción realizada, datos modificados
2. WHEN se habilita o suspende un conductor THEN el sistema SHALL registrar la justificación y el usuario responsable
3. WHEN se modifica un registro THEN el sistema SHALL mantener un historial de versiones con capacidad de consultar estados anteriores
4. WHEN se consulta auditoría THEN el sistema SHALL permitir filtrar por: usuario, tipo de acción, rango de fechas, módulo
5. WHEN se detecta un acceso no autorizado THEN el sistema SHALL registrar el intento y alertar a administradores
6. WHEN se genera un reporte de auditoría THEN el sistema SHALL incluir todas las operaciones realizadas en el período seleccionado
7. IF se requiere auditoría externa THEN el sistema SHALL permitir exportar logs completos en formato estándar

### Requisito 11: Notificaciones y Alertas

**Historia de Usuario:** Como usuario del sistema, quiero recibir notificaciones sobre eventos importantes, para mantenerme informado sobre cambios y acciones requeridas.

#### Criterios de Aceptación

1. WHEN una solicitud es observada THEN el sistema SHALL enviar notificación por correo al Gerente de Empresa
2. WHEN un conductor es habilitado THEN el sistema SHALL notificar al Gerente de Empresa
3. WHEN una licencia está próxima a vencer (30 días) THEN el sistema SHALL alertar al Gerente y al conductor
4. WHEN un certificado médico vence THEN el sistema SHALL suspender automáticamente al conductor y notificar
5. WHEN se registra una infracción grave THEN el sistema SHALL notificar inmediatamente a Directores
6. WHEN hay solicitudes pendientes por más de 5 días THEN el sistema SHALL alertar a Operarios
7. WHEN se actualiza el TUPA THEN el sistema SHALL notificar a todas las empresas registradas
8. WHEN un usuario recibe una notificación THEN el sistema SHALL mostrar un indicador en la interfaz y enviar correo electrónico

### Requisito 12: API REST para Integración con Sistema de Vehículos

**Historia de Usuario:** Como desarrollador del sistema de registro de vehículos DRTC, quiero consumir una API REST completa del sistema de nómina de conductores, para validar que los conductores asignados a vehículos estén debidamente habilitados.

#### Criterios de Aceptación

1. WHEN se consulta la API THEN el sistema SHALL proporcionar endpoints RESTful con autenticación mediante tokens JWT
2. WHEN el sistema de vehículos consulta un conductor THEN el sistema SHALL exponer endpoint GET /api/v1/conductores/{dni} con datos completos del conductor
3. WHEN se valida habilitación THEN el sistema SHALL exponer endpoint GET /api/v1/conductores/{dni}/habilitacion con estado actual y vigencia
4. WHEN se consultan conductores por empresa THEN el sistema SHALL exponer endpoint GET /api/v1/empresas/{ruc}/conductores con listado completo
5. WHEN se verifican infracciones THEN el sistema SHALL exponer endpoint GET /api/v1/conductores/{dni}/infracciones con historial completo
6. WHEN se valida compatibilidad THEN el sistema SHALL exponer endpoint POST /api/v1/validar-asignacion para verificar que conductor y vehículo sean compatibles según tipo de autorización
7. WHEN el sistema de vehículos registra una asignación THEN el sistema SHALL exponer endpoint POST /api/v1/asignaciones para registrar qué conductor opera qué vehículo
8. WHEN se consultan asignaciones THEN el sistema SHALL exponer endpoint GET /api/v1/conductores/{dni}/vehiculos-asignados
9. WHEN se recibe una petición API THEN el sistema SHALL responder en formato JSON con códigos HTTP estándar (200, 201, 400, 401, 404, 500)
10. WHEN se documenta la API THEN el sistema SHALL proporcionar documentación OpenAPI/Swagger accesible en /api/docs
11. WHEN se versiona la API THEN el sistema SHALL mantener compatibilidad hacia atrás y usar versionado semántico en URLs
12. WHEN se realizan múltiples consultas THEN el sistema SHALL implementar rate limiting para prevenir abuso (100 requests/minuto por token)

### Requisito 13: Interfaz de Usuario Responsiva y Accesible

**Historia de Usuario:** Como usuario del sistema, quiero una interfaz intuitiva y accesible desde diferentes dispositivos, para trabajar eficientemente desde oficina o campo.

#### Criterios de Aceptación

1. WHEN se accede al sistema desde cualquier dispositivo THEN el sistema SHALL adaptar la interfaz al tamaño de pantalla (responsive design)
2. WHEN se navega por el sistema THEN el sistema SHALL proporcionar menús claros organizados por módulos funcionales
3. WHEN se completan formularios THEN el sistema SHALL validar datos en tiempo real con mensajes de error claros
4. WHEN se muestran listados THEN el sistema SHALL permitir búsqueda, filtrado y ordenamiento
5. WHEN se visualizan datos THEN el sistema SHALL usar tablas paginadas para conjuntos grandes de datos
6. WHEN un usuario con discapacidad visual usa el sistema THEN el sistema SHALL cumplir con estándares WCAG 2.1 nivel AA
7. WHEN se realizan acciones críticas THEN el sistema SHALL solicitar confirmación antes de ejecutar
8. WHEN se procesan operaciones largas THEN el sistema SHALL mostrar indicadores de progreso

### Requisito 14: Despliegue con Docker y Contenedorización

**Historia de Usuario:** Como administrador de infraestructura, quiero que el sistema esté completamente dockerizado, para facilitar el despliegue, escalabilidad y mantenimiento en diferentes ambientes.

#### Criterios de Aceptación

1. WHEN se despliega el sistema THEN el sistema SHALL proporcionar archivos Dockerfile para frontend, backend y base de datos
2. WHEN se configura el entorno THEN el sistema SHALL incluir docker-compose.yml para orquestar todos los servicios
3. WHEN se inicia el sistema THEN el sistema SHALL levantar automáticamente: frontend (Astro), backend (FastAPI/Django), base de datos (PostgreSQL/MongoDB), y Redis para caché
4. WHEN se configuran contenedores THEN el sistema SHALL usar variables de entorno para configuración sensible (credenciales, URLs, secrets)
5. WHEN se despliega en producción THEN el sistema SHALL incluir configuración para reverse proxy (Nginx) como contenedor adicional
6. WHEN se escala el sistema THEN el sistema SHALL permitir múltiples instancias del backend con balanceo de carga
7. WHEN se persisten datos THEN el sistema SHALL usar volúmenes Docker para base de datos y archivos adjuntos
8. WHEN se actualizan servicios THEN el sistema SHALL permitir despliegue sin downtime mediante estrategia rolling update
9. WHEN se monitorea el sistema THEN el sistema SHALL incluir health checks en cada contenedor
10. WHEN se desarrolla localmente THEN el sistema SHALL proporcionar docker-compose.dev.yml con hot-reload habilitado
11. WHEN se construyen imágenes THEN el sistema SHALL usar multi-stage builds para optimizar tamaño de imágenes
12. WHEN se documenta despliegue THEN el sistema SHALL incluir README con instrucciones completas de instalación y configuración Docker

