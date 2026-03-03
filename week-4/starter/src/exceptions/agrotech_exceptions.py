"""
Excepciones personalizadas para el dominio AgroTech.
"""
from fastapi import HTTPException, status
from typing import Dict, Any, Optional


class AgroTechException(HTTPException):
    """Excepción base para el dominio agrícola."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[list[str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a diccionario para response."""
        return {
            "error_code": self.error_code,
            "message": self.detail,
            "status_code": self.status_code,
            "context": self.context,
            "suggestions": self.suggestions
        }


# ============================================
# EXCEPCIONES DE TRANSFERENCIAS
# ============================================

class TransferException(AgroTechException):
    """Excepciones específicas de transferencias de cultivos."""
    pass


class InvalidTransferStateException(TransferException):
    def __init__(self, current_state: str, attempted_action: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede {attempted_action} en estado {current_state}",
            error_code="INVALID_TRANSFER_STATE",
            context={
                "current_state": current_state,
                "attempted_action": attempted_action
            },
            suggestions=[
                f"Verificar el estado actual de la transferencia",
                f"Consultar acciones válidas para estado {current_state}"
            ]
        )


class InsufficientCapacityException(TransferException):
    def __init__(self, requested: float, available: float, zone_name: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Capacidad insuficiente en {zone_name}",
            error_code="INSUFFICIENT_CAPACITY",
            context={
                "requested_hectares": requested,
                "available_capacity": available,
                "zone_name": zone_name
            },
            suggestions=[
                "Reducir la cantidad a transferir",
                "Seleccionar otra zona de destino",
                "Programar para una fecha posterior"
            ]
        )


class CropNotAvailableException(TransferException):
    def __init__(self, crop_id: int, reason: str):
        super().__init__(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Cultivo ID {crop_id} no disponible: {reason}",
            error_code="CROP_NOT_AVAILABLE",
            context={
                "crop_id": crop_id,
                "reason": reason
            },
            suggestions=[
                "Esperar a que termine la operación actual",
                "Contactar al supervisor de zona"
            ]
        )


# ============================================
# EXCEPCIONES DE TAREAS
# ============================================

class TaskException(AgroTechException):
    """Excepciones específicas de tareas agrícolas."""
    pass


class WorkerNotAvailableException(TaskException):
    def __init__(self, worker_name: str, schedule_conflict: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Trabajador {worker_name} no disponible",
            error_code="WORKER_NOT_AVAILABLE",
            context={
                "worker_name": worker_name,
                "conflict": schedule_conflict
            },
            suggestions=[
                "Asignar otro trabajador disponible",
                "Reprogramar la tarea",
                "Dividir la tarea entre varios trabajadores"
            ]
        )


class WeatherConditionException(TaskException):
    def __init__(self, task_type: str, weather_issue: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Condiciones climáticas no aptas para {task_type}",
            error_code="WEATHER_CONDITION_INVALID",
            context={
                "task_type": task_type,
                "weather_issue": weather_issue
            },
            suggestions=[
                "Esperar mejores condiciones climáticas",
                "Reprogramar para fecha más favorable",
                "Usar equipo especializado si está disponible"
            ]
        )


class EquipmentUnavailableException(TaskException):
    def __init__(self, equipment: str, availability_date: str = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Equipo {equipment} no disponible",
            error_code="EQUIPMENT_UNAVAILABLE",
            context={
                "equipment": equipment,
                "available_date": availability_date
            },
            suggestions=[
                "Usar equipo alternativo",
                "Reprogramar tarea",
                f"Hacer reserva para {availability_date}" if availability_date else "Consultar disponibilidad"
            ]
        )


# ============================================
# EXCEPCIONES DE INCIDENTES
# ============================================

class IncidentException(AgroTechException):
    """Excepciones específicas de incidentes agrícolas."""
    pass


class DuplicateIncidentException(IncidentException):
    def __init__(self, existing_incident_id: int, location: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe incidente similar en {location}",
            error_code="DUPLICATE_INCIDENT",
            context={
                "existing_incident_id": existing_incident_id,
                "location": location
            },
            suggestions=[
                f"Consultar incidente existente #{existing_incident_id}",
                "Agregar información al incidente existente",
                "Reportar como incidente relacionado"
            ]
        )


class IncidentResolutionException(IncidentException):
    def __init__(self, incident_id: int, missing_requirements: list[str]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No se puede resolver incidente {incident_id}",
            error_code="INCIDENT_RESOLUTION_INCOMPLETE",
            context={
                "incident_id": incident_id,
                "missing_requirements": missing_requirements
            },
            suggestions=[
                "Completar todos los requisitos",
                "Documentar acciones tomadas",
                "Obtener aprobación del supervisor"
            ]
        )


# ============================================
# EXCEPCIONES DE SISTEMA
# ============================================

class ExternalServiceException(AgroTechException):
    def __init__(self, service_name: str, error_detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Servicio {service_name} no disponible",
            error_code="EXTERNAL_SERVICE_ERROR",
            context={
                "service_name": service_name,
                "error_detail": error_detail
            },
            suggestions=[
                "Intentar nuevamente en unos minutos",
                "Contactar soporte técnico",
                "Usar modo offline si está disponible"
            ]
        )


class ValidationException(AgroTechException):
    def __init__(self, field: str, value: Any, validation_rule: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación en campo {field}",
            error_code="VALIDATION_ERROR",
            context={
                "field": field,
                "value": str(value),
                "validation_rule": validation_rule
            },
            suggestions=[
                f"Verificar formato del campo {field}",
                f"Consultar reglas de validación para {field}",
                "Revisar la documentación de la API"
            ]
        )