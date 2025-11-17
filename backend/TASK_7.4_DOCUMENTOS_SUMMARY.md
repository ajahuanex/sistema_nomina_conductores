# Task 7.4: Gestión de Documentos de Conductores - Summary

## Fecha de Implementación
2025-11-15

## Descripción
Implementación completa del módulo de gestión de documentos para conductores, permitiendo subir, listar, descargar y eliminar archivos adjuntos como licencias, certificados médicos, antecedentes, etc.

## Componentes Implementados

### 1. Modelo de Datos
- **Archivo**: `backend/app/models/documento_conductor.py`
- **Modelo**: `DocumentoConductor`
- **Enum**: `TipoDocumento` (licencia_conducir, certificado_medico, antecedentes_penales, antecedentes_policiales, antecedentes_judiciales, foto_conductor, otro)
- **Validaciones**:
  - Tipos MIME permitidos: PDF, JPG, JPEG, PNG
  - Tamaño máximo: 10MB
  - Relación con Conductor y Usuario (quien subió)

### 2. Repositorio
- **Archivo**: `backend/app/repositories/documento_repository.py`
- **Clase**: `DocumentoRepository`
- **Métodos**:
  - `get_by_conductor()`: Obtener documentos de un conductor con filtro opcional por tipo
  - `get_by_nombre_almacenado()`: Buscar documento por nombre en sistema
  - `count_by_conductor()`: Contar documentos de un conductor
  - `delete_by_conductor()`: Eliminar todos los documentos de un conductor

### 3. Servicio
- **Archivo**: `backend/app/services/documento_service.py`
- **Clase**: `DocumentoService`
- **Métodos**:
  - `subir_documento()`: Subir archivo con validaciones
  - `obtener_documentos_conductor()`: Listar documentos con filtros
  - `obtener_documento()`: Obtener documento por ID
  - `eliminar_documento()`: Eliminar documento (archivo físico + BD)
  - `contar_documentos_conductor()`: Contador de documentos
  - `obtener_ruta_archivo()`: Obtener ruta completa del archivo

### 4. Utilidades de Manejo de Archivos
- **Archivo**: `backend/app/utils/file_handler.py`
- **Funciones**:
  - `validate_file_type()`: Validar extensión y MIME type
  - `validate_file_size()`: Validar tamaño máximo (10MB)
  - `generate_unique_filename()`: Generar nombre único con UUID
  - `save_upload_file()`: Guardar archivo en sistema
  - `delete_file()`: Eliminar archivo físico
  - `get_file_path()`: Obtener ruta de archivo
  - `file_exists()`: Verificar existencia de archivo

**Configuración**:
- Directorio de uploads: `uploads/conductores/`
- Tamaño máximo: 10MB
- Extensiones permitidas: .pdf, .jpg, .jpeg, .png
- MIME types permitidos: application/pdf, image/jpeg, image/jpg, image/png

### 5. Schemas Pydantic
- **Archivo**: `backend/app/schemas/documento.py`
- **Schemas**:
  - `DocumentoBase`: Schema base con tipo y descripción
  - `DocumentoCreate`: Para creación (usado en form data)
  - `DocumentoConductorResponse`: Respuesta completa con metadatos
  - `DocumentoConductorListResponse`: Lista de documentos
  - `DocumentoUploadResponse`: Respuesta al subir documento

### 6. Endpoints API
- **Archivo**: `backend/app/api/v1/endpoints/conductores.py`

#### POST /api/v1/conductores/{conductor_id}/documentos
- **Descripción**: Subir documento para un conductor
- **Permisos**: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE
- **Restricción**: Gerentes solo pueden subir a conductores de su empresa
- **Form Data**:
  - `file`: Archivo (PDF, JPG, PNG, máx 10MB)
  - `tipo_documento`: Tipo de documento (enum)
  - `descripcion`: Descripción opcional
- **Respuesta**: 201 Created con DocumentoUploadResponse
- **Validaciones**:
  - Tipo de archivo permitido
  - Tamaño máximo
  - Conductor existe
  - Permisos de empresa (para gerentes)

#### GET /api/v1/conductores/{conductor_id}/documentos
- **Descripción**: Listar documentos de un conductor
- **Permisos**: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE
- **Restricción**: Gerentes solo ven documentos de conductores de su empresa
- **Query Params**:
  - `tipo_documento`: Filtrar por tipo (opcional)
- **Respuesta**: 200 OK con DocumentoConductorListResponse

#### GET /api/v1/conductores/{conductor_id}/documentos/{documento_id}
- **Descripción**: Descargar un documento
- **Permisos**: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, OPERARIO, GERENTE
- **Restricción**: Gerentes solo descargan de conductores de su empresa
- **Respuesta**: FileResponse con el archivo
- **Headers**: Content-Type según tipo MIME, Content-Disposition con nombre original

#### DELETE /api/v1/conductores/{conductor_id}/documentos/{documento_id}
- **Descripción**: Eliminar un documento
- **Permisos**: SUPERUSUARIO, DIRECTOR, SUBDIRECTOR, GERENTE
- **Restricción**: Gerentes solo eliminan de conductores de su empresa
- **Respuesta**: 204 No Content
- **Acción**: Elimina archivo físico y registro en BD

### 7. Tests
- **Archivo**: `backend/tests/api/test_documentos.py`
- **Cobertura**:
  - ✅ Subir documento PDF exitosamente
  - ✅ Subir imagen exitosamente
  - ✅ Validar tipo de archivo no permitido
  - ✅ Validar tamaño excedido
  - ✅ Conductor no existe
  - ✅ Sin autenticación
  - ✅ Listar documentos
  - ✅ Filtrar por tipo
  - ✅ Conductor sin documentos
  - ✅ Descargar documento
  - ✅ Documento no existe
  - ✅ Eliminar documento
  - ✅ Eliminar sin permisos

## Seguridad Implementada

### Control de Acceso
- Autenticación JWT requerida en todos los endpoints
- RBAC (Role-Based Access Control) implementado
- Gerentes limitados a conductores de su propia empresa
- Operarios no pueden eliminar documentos

### Validaciones
- Tipos de archivo restringidos (solo PDF e imágenes)
- Tamaño máximo de 10MB
- Validación de MIME type y extensión
- Verificación de existencia de conductor
- Verificación de permisos por rol y empresa

### Almacenamiento
- Nombres de archivo únicos (UUID)
- Archivos almacenados fuera del código fuente
- Directorio dedicado: `uploads/conductores/`
- Eliminación de archivos físicos al eliminar registro

## Integración con Sistema Existente

### Relaciones
- `DocumentoConductor` → `Conductor` (many-to-one)
- `DocumentoConductor` → `Usuario` (many-to-one, quien subió)

### Modelo Conductor
- Relación `documentos` agregada al modelo Conductor
- Permite acceder a documentos desde el conductor

## Requisitos Cumplidos
- ✅ **Requisito 3.6**: Registro de antecedentes penales, policiales y judiciales
- ✅ **Requisito 3.7**: Certificado médico vigente

## Notas Técnicas

### Manejo de Errores
- `RecursoNoEncontrado`: Conductor o documento no existe
- `HTTPException 400`: Tipo de archivo no permitido o tamaño excedido
- `HTTPException 403`: Sin permisos para la operación
- `HTTPException 404`: Archivo físico no existe
- `HTTPException 500`: Error al guardar archivo

### Transacciones
- Rollback automático si falla el registro en BD después de guardar archivo
- Eliminación de archivo físico si falla la transacción
- Commit explícito después de operaciones exitosas

### Performance
- Lectura de archivo en memoria para validación
- Generación de nombres únicos con UUID4
- Índices en BD para búsquedas rápidas:
  - `conductor_id`
  - `tipo_documento`
  - `conductor_id + tipo_documento` (compuesto)

## Próximos Pasos Sugeridos
1. Implementar compresión de imágenes para reducir espacio
2. Agregar thumbnails para imágenes
3. Implementar escaneo de virus en archivos subidos
4. Agregar versionado de documentos
5. Implementar firma digital de documentos
6. Agregar notificaciones cuando se suben/eliminan documentos
7. Implementar backup automático de archivos

## Comandos de Prueba

### Ejecutar tests
```bash
cd backend
python -m pytest tests/api/test_documentos.py -v
```

### Ejecutar tests específicos
```bash
python -m pytest tests/api/test_documentos.py::TestListarDocumentos -v
python -m pytest tests/api/test_documentos.py::TestSubirDocumento::test_subir_documento_pdf_exitoso -v
```

## Estado
✅ **COMPLETADO** - Todos los sub-tasks implementados y probados

## Autor
Kiro AI Assistant

## Fecha
2025-11-15
