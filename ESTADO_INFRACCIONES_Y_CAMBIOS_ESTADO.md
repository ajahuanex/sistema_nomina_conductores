# Estado de Infracciones y Cambios de Estado

**Fecha:** 16 de noviembre de 2025  
**Estado:** ⏳ PARCIALMENTE IMPLEMENTADO

## 📊 Resumen del Estado Actual

### ✅ Lo que está implementado (Backend)

#### 1. Modelos de Datos
**Archivo:** `backend/app/models/infraccion.py`

##### TipoInfraccion
- Código de infracción
- Descripción
- Gravedad (LEVE, GRAVE, MUY_GRAVE)
- Puntos
- Estado activo

##### Infraccion
- Conductor asociado
- Tipo de infracción
- Fecha de infracción
- Descripción
- Entidad fiscalizadora
- Número de acta
- Estado (REGISTRADA, EN_PROCESO, RESUELTA, ANULADA)
- Resolución
- Usuario que registró

##### AsignacionVehiculo
- Conductor asociado
- Placa del vehículo
- Fecha de asignación
- Fecha de desasignación
- Estado activo
- Observaciones

#### 2. Repositorios
**Archivo:** `backend/app/repositories/infraccion_repository.py`
- ✅ Operaciones CRUD básicas
- ✅ Consultas por conductor
- ✅ Consultas por estado

### ❌ Lo que falta implementar

#### 1. Cambios de Estado de Conductor
**Funcionalidad:** Botones de acción en el detalle del conductor

##### Estados Posibles:
- PENDIENTE → HABILITADO
- HABILITADO → SUSPENDIDO
- HABILITADO → REVOCADO
- SUSPENDIDO → HABILITADO
- OBSERVADO → HABILITADO

##### Acciones Necesarias:
- [ ] Endpoint para cambiar estado
- [ ] Validaciones de transiciones permitidas
- [ ] Registro en auditoría
- [ ] Notificaciones
- [ ] Botones en el frontend

#### 2. Módulo de Infracciones
**Funcionalidad:** Registro y gestión de infracciones

##### Backend Pendiente:
- [ ] Servicio InfraccionService
- [ ] Endpoints CRUD de infracciones
- [ ] Cálculo de gravedad acumulada
- [ ] Sugerencia de sanciones
- [ ] Sincronización con MTC/SUNARP

##### Frontend Pendiente:
- [ ] Lista de infracciones
- [ ] Formulario de registro
- [ ] Historial por conductor
- [ ] Visualización de gravedad

#### 3. Evaluación de Idoneidad
**Funcionalidad:** Determinar si un conductor es apto

##### Criterios de Idoneidad:
1. **Licencia Vigente**
   - ✅ Ya validado en el modelo
   - Fecha de vencimiento no pasada

2. **Certificado Médico Vigente**
   - ✅ Ya validado en el modelo
   - Fecha de vencimiento no pasada

3. **Sin Infracciones Graves Recientes**
   - ❌ Falta implementar
   - Máximo X infracciones graves en Y meses
   - Sin infracciones muy graves en Z meses

4. **Puntos de Licencia**
   - ❌ Falta implementar
   - Acumulación de puntos por infracciones
   - Límite máximo de puntos

5. **Sin Sanciones Activas**
   - ❌ Falta implementar
   - Suspensiones vigentes
   - Revocaciones

6. **Habilitación Vigente**
   - ✅ Ya implementado
   - Estado HABILITADO

## 🎯 Propuesta de Implementación

### Fase 1: Cambios de Estado (Prioridad Alta)

#### Backend
```python
# Endpoint para cambiar estado
POST /api/v1/conductores/{id}/cambiar-estado
{
  "nuevo_estado": "suspendido",
  "motivo": "Infracciones graves acumuladas",
  "observaciones": "Suspensión por 6 meses"
}
```

#### Validaciones:
- Estado actual permite la transición
- Usuario tiene permisos (DIRECTOR, SUBDIRECTOR)
- Motivo es obligatorio
- Se registra en auditoría

#### Frontend:
- Botones en página de detalle
- Modal de confirmación
- Campo de motivo/observaciones
- Actualización automática del estado

### Fase 2: Módulo de Infracciones (Prioridad Media)

#### Backend
```python
# Endpoints necesarios
GET /api/v1/infracciones
POST /api/v1/infracciones
GET /api/v1/infracciones/{id}
PUT /api/v1/infracciones/{id}
GET /api/v1/infracciones/conductor/{conductor_id}
GET /api/v1/conductores/{id}/idoneidad
```

#### Frontend:
- Página de lista de infracciones
- Formulario de registro
- Tab en detalle de conductor
- Indicador de idoneidad

### Fase 3: Evaluación de Idoneidad (Prioridad Media)

#### Servicio de Idoneidad
```python
class IdoneidadService:
    async def evaluar_idoneidad(conductor_id: UUID) -> IdoneidadResponse:
        """
        Evalúa si un conductor es apto para conducir
        
        Returns:
            - apto: bool
            - razones: List[str]
            - puntos_acumulados: int
            - infracciones_graves: int
            - recomendacion: str
        """
```

#### Criterios:
1. Licencia vigente (no vencida)
2. Certificado médico vigente
3. Máximo 2 infracciones graves en 12 meses
4. Sin infracciones muy graves en 24 meses
5. Máximo 100 puntos acumulados
6. Sin suspensiones activas
7. Estado HABILITADO

## 📋 Matriz de Transiciones de Estado

### Estados Permitidos

| Estado Actual | Puede Cambiar A | Requiere | Rol Mínimo |
|---------------|-----------------|----------|------------|
| PENDIENTE | HABILITADO | Aprobación de habilitación | SUBDIRECTOR |
| PENDIENTE | OBSERVADO | Documentos incompletos | OPERARIO |
| OBSERVADO | PENDIENTE | Corrección de documentos | OPERARIO |
| HABILITADO | SUSPENDIDO | Infracciones graves | DIRECTOR |
| HABILITADO | REVOCADO | Infracciones muy graves | DIRECTOR |
| SUSPENDIDO | HABILITADO | Cumplimiento de sanción | SUBDIRECTOR |
| REVOCADO | - | No reversible | - |

### Validaciones por Transición

#### PENDIENTE → HABILITADO
- ✅ Habilitación aprobada
- ✅ Pago confirmado
- ✅ Documentos completos
- ✅ Licencia vigente
- ✅ Certificado médico vigente

#### HABILITADO → SUSPENDIDO
- ✅ Motivo documentado
- ✅ Infracciones registradas
- ✅ Plazo de suspensión definido
- ✅ Notificación al conductor

#### HABILITADO → REVOCADO
- ✅ Infracciones muy graves
- ✅ Resolución administrativa
- ✅ Notificación formal
- ✅ Irreversible

#### SUSPENDIDO → HABILITADO
- ✅ Plazo cumplido
- ✅ Sanciones pagadas
- ✅ Documentos actualizados
- ✅ Evaluación de idoneidad

## 🔄 Flujo de Evaluación de Idoneidad

```
1. Usuario solicita evaluar idoneidad
   ↓
2. Sistema verifica:
   - Licencia vigente ✓/✗
   - Certificado médico vigente ✓/✗
   - Infracciones en período ✓/✗
   - Puntos acumulados ✓/✗
   - Estado actual ✓/✗
   ↓
3. Sistema calcula:
   - Puntos totales
   - Infracciones graves (12 meses)
   - Infracciones muy graves (24 meses)
   ↓
4. Sistema determina:
   - APTO / NO APTO
   - Razones de no idoneidad
   - Recomendaciones
   ↓
5. Sistema muestra resultado
```

## 📊 Indicadores de Idoneidad

### Semáforo Visual

#### 🟢 APTO
- Todos los criterios cumplidos
- Sin infracciones graves recientes
- Documentos vigentes
- Estado HABILITADO

#### 🟡 APTO CON OBSERVACIONES
- Criterios básicos cumplidos
- Infracciones leves recientes
- Documentos próximos a vencer
- Requiere seguimiento

#### 🔴 NO APTO
- Uno o más criterios no cumplidos
- Infracciones graves/muy graves
- Documentos vencidos
- Estado SUSPENDIDO/REVOCADO

## 🎨 Diseño de UI Propuesto

### Página de Detalle de Conductor

```
┌─────────────────────────────────────────┐
│ Estado: [HABILITADO]  Idoneidad: [🟢 APTO] │
├─────────────────────────────────────────┤
│ Acciones:                               │
│ [Suspender] [Revocar] [Ver Infracciones]│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Evaluación de Idoneidad                 │
├─────────────────────────────────────────┤
│ ✓ Licencia vigente hasta 2027-01-15    │
│ ✓ Certificado médico vigente           │
│ ✓ Sin infracciones graves (12 meses)   │
│ ✓ Puntos acumulados: 0/100             │
│ ✓ Estado: HABILITADO                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Historial de Infracciones (0)          │
├─────────────────────────────────────────┤
│ No hay infracciones registradas         │
└─────────────────────────────────────────┘
```

## 📝 Próximos Pasos Recomendados

### Paso 1: Implementar Cambios de Estado
1. Crear endpoint de cambio de estado
2. Agregar validaciones de transiciones
3. Implementar botones en frontend
4. Agregar modales de confirmación
5. Registrar en auditoría

### Paso 2: Implementar Módulo de Infracciones
1. Crear servicio InfraccionService
2. Implementar endpoints CRUD
3. Crear página de lista
4. Crear formulario de registro
5. Agregar tab en detalle de conductor

### Paso 3: Implementar Evaluación de Idoneidad
1. Crear servicio IdoneidadService
2. Implementar cálculo de puntos
3. Implementar validaciones
4. Crear endpoint de evaluación
5. Mostrar indicador en frontend

## ✅ Checklist de Implementación

### Cambios de Estado
- [ ] Endpoint POST /conductores/{id}/cambiar-estado
- [ ] Validaciones de transiciones
- [ ] Registro en auditoría
- [ ] Botones en frontend
- [ ] Modales de confirmación
- [ ] Actualización de UI

### Infracciones
- [ ] Servicio InfraccionService
- [ ] Endpoints CRUD
- [ ] Página de lista
- [ ] Formulario de registro
- [ ] Historial por conductor
- [ ] Cálculo de gravedad

### Idoneidad
- [ ] Servicio IdoneidadService
- [ ] Endpoint de evaluación
- [ ] Cálculo de puntos
- [ ] Validaciones de criterios
- [ ] Indicador visual
- [ ] Recomendaciones

## 🎉 Conclusión

El sistema tiene una base sólida con:
- ✅ Modelos de datos completos
- ✅ CRUD de conductores funcional
- ✅ Validaciones básicas

Falta implementar:
- ❌ Cambios de estado con validaciones
- ❌ Módulo completo de infracciones
- ❌ Evaluación de idoneidad

**Recomendación:** Implementar en el orden propuesto para tener funcionalidad incremental.

---

**Tiempo estimado:**
- Cambios de estado: 2-3 horas
- Módulo de infracciones: 4-5 horas
- Evaluación de idoneidad: 2-3 horas
- **Total: 8-11 horas**
