from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from .exceptions.agrotech_exceptions import (
    AgroTechException,
    InvalidTransferStateException,
    InsufficientCapacityException,
    WorkerNotAvailableException,
    WeatherConditionException,
    DuplicateIncidentException
)

# ============================================
# ENUMS DE ESTADO
# ============================================

class TransferStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"  
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class TaskStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"
    FAILED = "failed"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================
# MODELS DE RESPONSE
# ============================================

class StatusChange(BaseModel):
    """Cambio de estado en timeline."""
    timestamp: datetime
    from_status: str
    to_status: str
    changed_by: str
    reason: Optional[str] = None

class TransferDetail(BaseModel):
    """Detalle completo de transferencia."""
    id: int
    transfer_code: str
    source_zone_name: str
    destination_zone_name: str
    crop_name: str
    quantity_hectares: float
    status: TransferStatus
    priority: Priority
    requested_by: str
    approved_by: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    progress_percentage: int = 0
    created_at: datetime

class TransferResponse(BaseModel):
    """Response especializado para transferencias."""
    transfer: TransferDetail
    status_info: Dict[str, Any]
    timeline: List[StatusChange]
    next_actions: List[str]
    warnings: List[str] = []

class TaskDetail(BaseModel):
    """Detalle de tarea agrícola."""
    id: int
    task_code: str
    task_type: str
    crop_name: str
    zone_name: str
    status: TaskStatus
    assigned_to: Optional[str] = None
    scheduled_start: datetime
    completion_percentage: int = 0
    priority: Priority

class TaskResponse(BaseModel):
    """Response para tareas."""
    task: TaskDetail
    assignment_info: Dict[str, Any]
    resource_status: Dict[str, str]
    next_steps: List[str]

# ============================================
# SCHEMAS DE REQUEST
# ============================================

class TransferCreateRequest(BaseModel):
    source_zone_id: int = Field(..., gt=0)
    destination_zone_id: int = Field(..., gt=0)
    crop_id: int = Field(..., gt=0)
    quantity_hectares: float = Field(..., gt=0, le=1000)
    reason: str = Field(..., min_length=10, max_length=500)
    priority: Priority = Priority.MEDIUM

class TransferApprovalRequest(BaseModel):
    approved_by: str = Field(..., min_length=2)
    approval_notes: str = Field(..., min_length=5)
    conditions: Optional[List[str]] = None

# ============================================
# CONFIGURACIÓN FASTAPI
# ============================================

app = FastAPI(
    title="AgroTech Operations API",
    description="""
    ## 🚜 Sistema Avanzado de Operaciones Agrícolas
    
    API empresarial para gestión de transferencias, tareas e incidentes agrícolas con:
    
    ### ✨ Características Principales
    * **Manejo de Estados** - Workflows complejos con validaciones
    * **Responses Contextuales** - Información rica y específica por operación
    * **Excepciones Personalizadas** - Errores descriptivos del dominio
    * **Status Codes Apropiados** - Códigos HTTP semánticamente correctos
    * **Documentación Rica** - Examples y descriptions detalladas
    
    ### 🔄 Workflows Implementados
    * **Transferencias** - De cultivos entre zonas agrícolas
    * **Tareas** - Programación y seguimiento de actividades
    * **Incidentes** - Reporte y resolución de problemas
    
    ### 🛡️ Manejo Robusto de Errores
    * Excepciones contextualizadas por dominio
    * Sugerencias de resolución automáticas
    * Logging estructurado para debugging
    * Responses informativos con next actions
    """,
    version="4.0.0",
    contact={
        "name": "AgroTech Operations Team",
        "email": "operations@agrotech.com"
    }
)

# ============================================
# DATOS SIMULADOS EN MEMORIA
# ============================================

# Simular datos base
transfers_db = {}
tasks_db = {}
next_id = 1

# Datos de zonas y cultivos para referencia
zones_data = {
    1: {"name": "Zona Norte - Templada", "capacity": 500, "used": 250},
    2: {"name": "Zona Sur - Tropical", "capacity": 400, "used": 150},
    3: {"name": "Zona Este - Intensiva", "capacity": 300, "used": 280}
}

crops_data = {
    1: {"name": "Maíz Amarillo Duro", "zone_id": 1, "hectares": 45},
    2: {"name": "Café Arábica Premium", "zone_id": 2, "hectares": 25},
    3: {"name": "Tomate Chonto", "zone_id": 3, "hectares": 15}
}

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(AgroTechException)
async def agrotech_exception_handler(request: Request, exc: AgroTechException):
    """Handler para excepciones del dominio AgroTech."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            **exc.to_dict(),
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path),
            "method": request.method
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    """Handler para errores internos del servidor."""
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Error interno del servidor de operaciones",
            "context": {
                "service": "AgroTech Operations API v4.0",
                "path": str(request.url.path),
                "timestamp": datetime.now().isoformat()
            },
            "suggestions": [
                "Intentar la operación nuevamente",
                "Contactar al equipo de soporte",
                "Verificar el estado del sistema en /health"
            ]
        }
    )

# ============================================
# ENDPOINTS PRINCIPALES
# ============================================

@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "name": "AgroTech Operations API",
        "version": "4.0.0",
        "domain": "Operaciones Agrícolas Avanzadas",
        "status": "online",
        "features": {
            "transfers": "Gestión de transferencias con estados y validaciones",
            "tasks": "Programación y seguimiento de tareas agrícolas", 
            "incidents": "Reporte y manejo de incidentes",
            "error_handling": "Excepciones contextuales del dominio",
            "responses": "Información rica y específica por operación"
        },
        "workflows": {
            "transfer_states": ["pending", "approved", "in_transit", "completed", "cancelled", "failed"],
            "task_states": ["scheduled", "in_progress", "completed", "cancelled", "delayed", "failed"]
        },
        "key_endpoints": {
            "create_transfer": "POST /transfers/",
            "approve_transfer": "PUT /transfers/{id}/approve",
            "transfer_status": "GET /transfers/{id}/status",
            "create_task": "POST /tasks/",
            "task_progress": "PUT /tasks/{id}/progress"
        }
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verificación de estado del sistema."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AgroTech Operations API v4.0",
        "components": {
            "transfer_system": "operational",
            "task_scheduler": "operational", 
            "incident_manager": "operational",
            "error_handler": "operational"
        },
        "statistics": {
            "active_transfers": len([t for t in transfers_db.values() if t["status"] in ["pending", "approved", "in_transit"]]),
            "total_transfers": len(transfers_db),
            "active_tasks": len([t for t in tasks_db.values() if t["status"] in ["scheduled", "in_progress"]]),
            "zones_available": len(zones_data)
        }
    }

# ============================================
# ENDPOINTS DE TRANSFERENCIAS
# ============================================

@app.post(
    "/transfers/",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva transferencia",
    description="Crea una nueva transferencia de cultivos entre zonas con validaciones completas"
)
async def create_transfer(transfer_request: TransferCreateRequest):
    """Crear transferencia de cultivos con validaciones."""
    global next_id
    
    # Validaciones de negocio
    if transfer_request.source_zone_id == transfer_request.destination_zone_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La zona origen y destino deben ser diferentes"
        )
    
    # Verificar capacidad de zona destino
    dest_zone = zones_data.get(transfer_request.destination_zone_id)
    if not dest_zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona destino {transfer_request.destination_zone_id} no encontrada"
        )
    
    available_capacity = dest_zone["capacity"] - dest_zone["used"]
    if transfer_request.quantity_hectares > available_capacity:
        raise InsufficientCapacityException(
            requested=transfer_request.quantity_hectares,
            available=available_capacity,
            zone_name=dest_zone["name"]
        )
    
    # Crear transferencia
    transfer_id = next_id
    next_id += 1
    
    crop_info = crops_data.get(transfer_request.crop_id, {"name": "Cultivo Desconocido"})
    source_zone = zones_data.get(transfer_request.source_zone_id, {"name": "Zona Desconocida"})
    
    transfer = {
        "id": transfer_id,
        "transfer_code": f"TRF-{datetime.now().strftime('%Y%m%d')}-{transfer_id:03d}",
        "source_zone_id": transfer_request.source_zone_id,
        "destination_zone_id": transfer_request.destination_zone_id,
        "crop_id": transfer_request.crop_id,
        "quantity_hectares": transfer_request.quantity_hectares,
        "status": TransferStatus.PENDING.value,
        "priority": transfer_request.priority.value,
        "requested_by": "user_system",  # En producción vendría del auth
        "reason": transfer_request.reason,
        "created_at": datetime.now(),
        "timeline": []
    }
    
    transfers_db[transfer_id] = transfer
    
    # Crear response
    transfer_detail = TransferDetail(
        id=transfer["id"],
        transfer_code=transfer["transfer_code"],
        source_zone_name=source_zone["name"],
        destination_zone_name=dest_zone["name"],
        crop_name=crop_info["name"],
        quantity_hectares=transfer["quantity_hectares"],
        status=TransferStatus(transfer["status"]),
        priority=Priority(transfer["priority"]),
        requested_by=transfer["requested_by"],
        created_at=transfer["created_at"]
    )
    
    return TransferResponse(
        transfer=transfer_detail,
        status_info={
            "current_step": "Aguardando aprobación del supervisor",
            "days_in_status": 0,
            "approver_required": "supervisor_zona",
            "estimated_approval_time": "2-4 horas"
        },
        timeline=[],  # Nueva transferencia sin historial
        next_actions=[
            "Aprobar transferencia",
            "Solicitar modificaciones", 
            "Cancelar solicitud",
            "Cambiar prioridad"
        ],
        warnings=[] if available_capacity > transfer_request.quantity_hectares * 2 else [
            f"Capacidad limitada en zona destino: {available_capacity:.1f} hectáreas disponibles"
        ]
    )

@app.put(
    "/transfers/{transfer_id}/approve",
    response_model=TransferResponse,
    summary="Aprobar transferencia",
    description="Aprueba una transferencia pendiente y la marca para ejecución"
)
async def approve_transfer(transfer_id: int, approval: TransferApprovalRequest):
    """Aprobar una transferencia pendiente."""
    transfer = transfers_db.get(transfer_id)
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transferencia {transfer_id} no encontrada"
        )
    
    # Validar estado
    if transfer["status"] != TransferStatus.PENDING.value:
        raise InvalidTransferStateException(
            current_state=transfer["status"],
            attempted_action="aprobar"
        )
    
    # Actualizar transferencia
    transfer["status"] = TransferStatus.APPROVED.value
    transfer["approved_by"] = approval.approved_by
    transfer["updated_at"] = datetime.now()
    
    # Agregar al timeline
    status_change = StatusChange(
        timestamp=datetime.now(),
        from_status=TransferStatus.PENDING.value,
        to_status=TransferStatus.APPROVED.value,
        changed_by=approval.approved_by,
        reason=approval.approval_notes
    )
    
    transfer["timeline"].append(status_change.dict())
    
    # Construir response
    crop_info = crops_data.get(transfer["crop_id"], {"name": "Cultivo Desconocido"})
    source_zone = zones_data.get(transfer["source_zone_id"], {"name": "Zona Desconocida"})
    dest_zone = zones_data.get(transfer["destination_zone_id"], {"name": "Zona Desconocida"})
    
    transfer_detail = TransferDetail(
        id=transfer["id"],
        transfer_code=transfer["transfer_code"],
        source_zone_name=source_zone["name"],
        destination_zone_name=dest_zone["name"],
        crop_name=crop_info["name"],
        quantity_hectares=transfer["quantity_hectares"],
        status=TransferStatus(transfer["status"]),
        priority=Priority(transfer["priority"]),
        requested_by=transfer["requested_by"],
        approved_by=transfer.get("approved_by"),
        created_at=transfer["created_at"]
    )
    
    return TransferResponse(
        transfer=transfer_detail,
        status_info={
            "current_step": "Aprobado - Listo para iniciar traslado",
            "approved_by": approval.approved_by,
            "approval_date": datetime.now().isoformat(),
            "next_deadline": "Iniciar en 24 horas"
        },
        timeline=[StatusChange(**item) for item in transfer["timeline"]],
        next_actions=[
            "Iniciar transferencia", 
            "Programar fecha de inicio",
            "Asignar equipo de traslado",
            "Cancelar transferencia"
        ]
    )

@app.get(
    "/transfers/{transfer_id}/status",
    response_model=TransferResponse,
    summary="Estado de transferencia",
    description="Obtiene el estado actual y historial completo de una transferencia"
)
async def get_transfer_status(transfer_id: int):
    """Obtener estado detallado de transferencia."""
    transfer = transfers_db.get(transfer_id)
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transferencia {transfer_id} no encontrada"
        )
    
    # Construir información contextual según estado
    status_info = {}
    next_actions = []
    
    if transfer["status"] == TransferStatus.PENDING.value:
        status_info = {
            "current_step": "Aguardando aprobación",
            "waiting_time": "2 horas",
            "approver_required": "supervisor_zona"
        }
        next_actions = ["Aprobar", "Rechazar", "Solicitar cambios"]
        
    elif transfer["status"] == TransferStatus.APPROVED.value:
        status_info = {
            "current_step": "Aprobado - Listo para ejecutar",
            "approved_by": transfer.get("approved_by", "N/A"),
            "deadline": "24 horas para iniciar"
        }
        next_actions = ["Iniciar transferencia", "Programar inicio", "Asignar equipo"]
        
    elif transfer["status"] == TransferStatus.COMPLETED.value:
        status_info = {
            "current_step": "Transferencia completada exitosamente",
            "completion_date": transfer.get("completed_at", "N/A"),
            "final_status": "Exitoso"
        }
        next_actions = ["Ver reporte final", "Archivar", "Calificar proceso"]
    
    # Construir response completo
    crop_info = crops_data.get(transfer["crop_id"], {"name": "Cultivo Desconocido"})
    source_zone = zones_data.get(transfer["source_zone_id"], {"name": "Zona Desconocida"})
    dest_zone = zones_data.get(transfer["destination_zone_id"], {"name": "Zona Desconocida"})
    
    transfer_detail = TransferDetail(
        id=transfer["id"],
        transfer_code=transfer["transfer_code"],
        source_zone_name=source_zone["name"],
        destination_zone_name=dest_zone["name"],
        crop_name=crop_info["name"],
        quantity_hectares=transfer["quantity_hectares"],
        status=TransferStatus(transfer["status"]),
        priority=Priority(transfer["priority"]),
        requested_by=transfer["requested_by"],
        approved_by=transfer.get("approved_by"),
        created_at=transfer["created_at"]
    )
    
    return TransferResponse(
        transfer=transfer_detail,
        status_info=status_info,
        timeline=[StatusChange(**item) for item in transfer.get("timeline", [])],
        next_actions=next_actions
    )