# 🚀 Proyecto Semana 04: API AgroTech con Responses y Manejo de Errores Avanzado

## 🏛️ Dominio Asignado
**Dominio**: `Agricultura y AgroTech - Sistema de Gestión de Operaciones Agrícolas`

La semana 4 implementa un **sistema completo de gestión de operaciones agrícolas** con manejo profesional de responses, status codes HTTP, excepciones personalizadas y workflows con estados para transferencias de cultivos, tareas de campo y operaciones logísticas.

---

## 🎯 Objetivo

Construir una **API REST empresarial** aplicando responses específicos, status codes apropiados, manejo robusto de errores, documentación OpenAPI avanzada y workflows con estados para operaciones complejas del dominio agrícola.

---

## 🌾 Entidades con Estados Complejos

### Transferencia de Cultivos (CropTransfer)
```python
class TransferStatus(str, Enum):
    PENDING = "pending"           # Solicitada, aguardando aprobación
    APPROVED = "approved"         # Aprobada, lista para ejecutar
    IN_TRANSIT = "in_transit"     # En proceso de traslado
    COMPLETED = "completed"       # Transferencia exitosa
    CANCELLED = "cancelled"       # Cancelada por user/sistema
    FAILED = "failed"            # Falló durante el proceso

CropTransfer:
    id: int
    transfer_code: str           # TRF-YYYYMMDD-XXX
    source_zone_id: int          # Zona origen
    destination_zone_id: int     # Zona destino  
    crop_id: int                 # Cultivo a transferir
    quantity_hectares: Decimal   # Área a transferir
    status: TransferStatus
    requested_by: str           # Usuario solicitante
    approved_by: str | None     # Usuario aprobador
    reason: str                 # Motivo de la transferencia
    priority: Priority          # Low, Medium, High, Critical
    estimated_start: datetime   # Fecha estimada inicio
    estimated_completion: datetime # Fecha estimada fin
    actual_start: datetime | None
    actual_completion: datetime | None
    notes: str | None
    cost_estimate: Decimal | None
    created_at: datetime
    updated_at: datetime | None
```

### Tarea Agrícola (AgriculturalTask)
```python
class TaskType(str, Enum):
    PLANTING = "planting"         # Siembra
    IRRIGATION = "irrigation"     # Riego
    FERTILIZATION = "fertilization" # Fertilización
    PEST_CONTROL = "pest_control"  # Control de plagas
    HARVESTING = "harvesting"     # Cosecha
    SOIL_ANALYSIS = "soil_analysis" # Análisis de suelo
    MAINTENANCE = "maintenance"   # Mantenimiento general

class TaskStatus(str, Enum):
    SCHEDULED = "scheduled"       # Programada
    IN_PROGRESS = "in_progress"   # En ejecución
    COMPLETED = "completed"       # Completada
    CANCELLED = "cancelled"       # Cancelada
    DELAYED = "delayed"          # Retrasada
    FAILED = "failed"           # Falló

AgriculturalTask:
    id: int
    task_code: str              # TSK-YYYYMMDD-XXX
    task_type: TaskType
    crop_id: int               # Cultivo asociado
    zone_id: int              # Zona donde se ejecuta
    status: TaskStatus
    assigned_to: str          # Trabajador asignado
    supervisor: str           # Supervisor responsable
    scheduled_start: datetime # Fecha programada inicio
    scheduled_end: datetime   # Fecha programada fin
    actual_start: datetime | None
    actual_end: datetime | None
    description: str
    instructions: str | None   # Instrucciones específicas
    equipment_needed: list[str] # Equipos necesarios
    materials_needed: list[str] # Materiales necesarios
    completion_percentage: int  # 0-100
    quality_score: int | None   # 1-10 calificación
    weather_conditions: str | None
    is_recurring: bool         # Si es tarea recurrente
    parent_task_id: int | None # Para subtareas
    created_at: datetime
    updated_at: datetime | None
```

### Incidente Agrícola (AgriculturalIncident)
```python
class IncidentSeverity(str, Enum):
    LOW = "low"               # Menor impacto
    MEDIUM = "medium"         # Impacto moderado  
    HIGH = "high"            # Alto impacto
    CRITICAL = "critical"    # Crítico, requiere acción inmediata

class IncidentType(str, Enum):
    PEST_OUTBREAK = "pest_outbreak"      # Brote de plaga
    DISEASE = "disease"                  # Enfermedad del cultivo
    WEATHER_DAMAGE = "weather_damage"    # Daño climático
    EQUIPMENT_FAILURE = "equipment_failure" # Falla de equipo
    IRRIGATION_ISSUE = "irrigation_issue"   # Problema de riego
    SOIL_CONTAMINATION = "soil_contamination" # Contaminación
    THEFT = "theft"                      # Robo
    OTHER = "other"                      # Otro tipo

class IncidentStatus(str, Enum):
    REPORTED = "reported"     # Reportado
    INVESTIGATING = "investigating" # En investigación
    ADDRESSING = "addressing" # Atendiendo
    RESOLVED = "resolved"     # Resuelto
    CLOSED = "closed"        # Cerrado
```

---

## 📋 Requisitos Funcionales - Responses y Estados

### RF-01: Gestión de Transferencias con Estados
**Endpoints de Workflow:**
- `POST /transfers/` - Crear transferencia (201 Created)
- `PUT /transfers/{id}/approve` - Aprobar (200 OK + detalles)
- `PUT /transfers/{id}/start` - Iniciar traslado (202 Accepted)
- `PUT /transfers/{id}/complete` - Completar (200 OK + summary)
- `PUT /transfers/{id}/cancel` - Cancelar (200 OK + reason)
- `GET /transfers/{id}/status` - Estado actual (200 OK + timeline)

### RF-02: Sistema de Tareas con Tracking
**Endpoints de Operaciones:**
- `POST /tasks/` - Crear tarea (201 Created + location header)
- `PUT /tasks/{id}/assign` - Asignar trabajador (200 OK)
- `PUT /tasks/{id}/start` - Iniciar ejecución (202 Accepted)
- `PUT /tasks/{id}/progress` - Actualizar progreso (200 OK + %)
- `PUT /tasks/{id}/complete` - Marcar completada (200 OK + results)
- `GET /tasks/{id}/timeline` - Historia de cambios (200 OK)

### RF-03: Manejo de Incidentes
**Endpoints de Crisis:**
- `POST /incidents/` - Reportar incidente (201 Created + alert)
- `PUT /incidents/{id}/escalate` - Escalar severidad (200 OK)
- `PUT /incidents/{id}/investigate` - Iniciar investigación (202 Accepted)
- `PUT /incidents/{id}/resolve` - Resolver incidente (200 OK + solution)
- `GET /incidents/active` - Incidentes activos (200 OK + priority sort)

---

## 🔧 Responses Específicos por Dominio

### Response Models Especializados

```python
class TransferResponse(BaseModel):
    """Response especializado para transferencias."""
    transfer: CropTransferDetail
    status_info: dict           # Info del estado actual
    timeline: list[StatusChange] # Historia de cambios
    next_actions: list[str]     # Acciones disponibles
    estimated_completion: datetime | None
    progress_percentage: int    # 0-100
    
class TaskResponse(BaseModel):
    """Response para tareas agrícolas.""" 
    task: AgriculturalTaskDetail
    assignment_info: dict       # Info del trabajador
    resource_status: dict       # Estado de recursos
    weather_forecast: dict | None # Pronóstico relevante
    dependencies: list[TaskSummary] # Tareas dependientes
    
class IncidentResponse(BaseModel):
    """Response para incidentes."""
    incident: AgriculturalIncidentDetail  
    impact_assessment: dict     # Evaluación de impacto
    response_team: list[str]    # Equipo asignado
    resolution_steps: list[str] # Pasos de resolución
    similar_incidents: list[IncidentSummary] # Casos similares
```

### Status Codes Contextuales

```python
# Transferencias
201 - Transferencia creada exitosamente
202 - Transferencia iniciada, procesando en background
200 - Estado actualizado correctamente  
409 - Conflicto: transferencia ya en proceso
422 - Error de validación: zona destino sin capacidad
423 - Recurso bloqueado: cultivo en otra transferencia
503 - Servicio no disponible: sistema de transporte inactivo

# Tareas
201 - Tarea programada exitosamente
202 - Tarea iniciada, en ejecución
200 - Progreso actualizado
409 - Conflicto: trabajador ya asignado a otra tarea
422 - Error: equipo no disponible para fecha programada
412 - Precondición falla: tarea previa no completada

# Incidentes  
201 - Incidente reportado, equipo notificado
202 - Investigación iniciada
200 - Estado actualizado
503 - Sistema de alertas no disponible
422 - Datos insuficientes para clasificar severidad
```

---

## 🛡️ Excepciones Personalizadas

```python
class AgroTechException(HTTPException):
    """Excepción base del dominio agrícola."""
    
class TransferException(AgroTechException):
    """Excepciones específicas de transferencias."""

class InvalidTransferStateException(TransferException):
    status_code = 409
    detail = "Operación no válida para el estado actual"

class InsufficientCapacityException(TransferException):
    status_code = 422
    detail = "Zona destino sin capacidad suficiente"

class TaskException(AgroTechException):
    """Excepciones específicas de tareas."""

class WorkerNotAvailableException(TaskException):
    status_code = 409
    detail = "Trabajador no disponible en el horario solicitado"

class WeatherConditionException(TaskException):
    status_code = 422
    detail = "Condiciones climáticas no aptas para la tarea"

class IncidentException(AgroTechException):
    """Excepciones específicas de incidentes."""

class DuplicateIncidentException(IncidentException):
    status_code = 409
    detail = "Ya existe un incidente similar reportado"
```

---

## 📊 Documentación OpenAPI Avanzada

### Response Examples
```python
@app.post(
    "/transfers/",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Transferencia creada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "transfer": {
                            "id": 123,
                            "transfer_code": "TRF-20240315-001",
                            "status": "pending",
                            "crop_name": "Maíz Amarillo Duro",
                            "quantity_hectares": 15.5
                        },
                        "status_info": {
                            "current_step": "Aguardando aprobación",
                            "days_in_status": 0,
                            "approver_required": "supervisor_zona"
                        },
                        "next_actions": [
                            "Aprobar transferencia",
                            "Solicitar modificaciones",
                            "Cancelar solicitud"
                        ]
                    }
                }
            }
        },
        422: {
            "description": "Error de validación",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "INSUFFICIENT_CAPACITY",
                        "message": "La zona destino no tiene capacidad suficiente",
                        "details": {
                            "requested_hectares": 15.5,
                            "available_capacity": 8.2,
                            "zone_name": "Zona Norte"
                        },
                        "suggestions": [
                            "Reducir cantidad a transferir",
                            "Seleccionar otra zona destino",
                            "Programar para fecha posterior"
                        ]
                    }
                }
            }
        }
    }
)
```

---

## 🔄 Workflows de Estados

### Transferencia de Cultivos
```
PENDING → APPROVED → IN_TRANSIT → COMPLETED
   ↓         ↓           ↓
CANCELLED ← CANCELLED ← FAILED
```

### Tareas Agrícolas
```
SCHEDULED → IN_PROGRESS → COMPLETED
    ↓           ↓
 CANCELLED ← DELAYED
    ↓           ↓
 FAILED ← ←  FAILED
```

### Manejo de Incidentes
```
REPORTED → INVESTIGATING → ADDRESSING → RESOLVED → CLOSED
```

---

## 🧪 Casos de Prueba Específicos

### Transferencia Exitosa
```bash
# Crear transferencia
POST /transfers/
{
    "source_zone_id": 1,
    "destination_zone_id": 2,
    "crop_id": 5,
    "quantity_hectares": 10.5,
    "reason": "Optimización de recursos por temporada"
}
# Response: 201 Created + transfer details

# Aprobar transferencia  
PUT /transfers/123/approve
{
    "approved_by": "supervisor01",
    "approval_notes": "Aprobado - zona destino con capacidad"
}
# Response: 200 OK + updated status
```

### Manejo de Errores Contextualizados
```bash
# Error de capacidad
POST /transfers/
{
    "destination_zone_id": 3,
    "quantity_hectares": 100.0  # Excede capacidad
}
# Response: 422 Unprocessable Entity + detailed error

# Error de estado inválido
PUT /transfers/123/complete    # Transfer aún pending
# Response: 409 Conflict + valid actions
```

---

## 📈 Métricas de Performance

- ✅ **Response Time**: < 300ms para operaciones complejas
- ✅ **Error Handling**: 100% de errores con códigos apropiados  
- ✅ **Documentation**: Swagger con examples para cada endpoint
- ✅ **Monitoring**: Logs estructurados para debugging
- ✅ **Validation**: Pydantic v2 con validadores específicos del dominio

---

## 🔍 Monitoreo y Logging

```python
# Estructura de logs
{
    "timestamp": "2024-03-15T10:30:00Z",
    "level": "INFO",
    "service": "agrotech-operations",
    "operation": "transfer_approval", 
    "transfer_id": 123,
    "user_id": "supervisor01",
    "status_change": "pending -> approved",
    "processing_time_ms": 145,
    "context": {
        "zone_from": "Zona A",
        "zone_to": "Zona B", 
        "crop_type": "cereal",
        "hectares": 10.5
    }
}
```

---

## 📋 Criterios de Evaluación

- ✅ **Entity con Estados** - Mínimo 10 campos + workflow complejo
- ✅ **Responses Específicos** - Models diferenciados por operación
- ✅ **Status Codes** - Uso apropiado de códigos HTTP
- ✅ **Exception Handling** - Excepciones personalizadas del dominio
- ✅ **OpenAPI Documentation** - Examples y descriptions completas
- ✅ **Workflow Management** - Transiciones de estado validadas
- ✅ **Error Context** - Mensajes informativos y sugerencias
- ✅ **Performance Monitoring** - Logs y métricas estructuradas