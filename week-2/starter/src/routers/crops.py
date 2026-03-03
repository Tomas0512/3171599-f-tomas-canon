from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..schemas.crop import (
    CropCreate, 
    CropUpdate, 
    CropResponse, 
    CropListResponse,
    CropTypeEnum,
    CropStatusEnum
)
from ..services.crop_service import crop_service

# Crear el router
router = APIRouter(prefix="/crops", tags=["Cultivos"])


@router.post(
    "/",
    response_model=CropResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo cultivo",
    description="Registra un nuevo cultivo en el sistema con validación completa."
)
async def create_crop(crop_data: CropCreate):
    """Crear un nuevo cultivo agrícola."""
    try:
        crop = crop_service.create_crop(crop_data)
        return CropResponse(**crop.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get(
    "/",
    response_model=CropListResponse,
    summary="Listar cultivos",
    description="Obtiene lista paginada de cultivos con filtros opcionales."
)
async def get_crops(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    status: Optional[CropStatusEnum] = Query(None, description="Filtrar por estado del cultivo"),
    crop_type: Optional[CropTypeEnum] = Query(None, description="Filtrar por tipo de cultivo"),
    active_only: bool = Query(True, description="Mostrar solo cultivos activos")
):
    """Obtener lista de cultivos con filtros y paginación."""
    try:
        crops, total = crop_service.get_crops(
            skip=skip,
            limit=limit, 
            status=status,
            crop_type=crop_type,
            active_only=active_only
        )
        
        crop_responses = [CropResponse(**crop.to_dict()) for crop in crops]
        
        return CropListResponse(
            crops=crop_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cultivos: {str(e)}"
        )


@router.get(
    "/{crop_id}",
    response_model=CropResponse,
    summary="Obtener cultivo por ID",
    description="Obtiene la información completa de un cultivo específico."
)
async def get_crop(crop_id: int):
    """Obtener un cultivo específico por su ID."""
    crop = crop_service.get_crop_by_id(crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cultivo con ID {crop_id} no encontrado"
        )
    
    return CropResponse(**crop.to_dict())


@router.put(
    "/{crop_id}",
    response_model=CropResponse,
    summary="Actualizar cultivo",
    description="Actualiza información de un cultivo existente."
)
async def update_crop(crop_id: int, crop_data: CropUpdate):
    """Actualizar información de un cultivo."""
    try:
        # Verificar que el cultivo existe
        existing_crop = crop_service.get_crop_by_id(crop_id)
        if not existing_crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cultivo con ID {crop_id} no encontrado"
            )
        
        # Actualizar el cultivo
        updated_crop = crop_service.update_crop(crop_id, crop_data)
        if not updated_crop:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el cultivo"
            )
        
        return CropResponse(**updated_crop.to_dict())
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.delete(
    "/{crop_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar cultivo",
    description="Elimina un cultivo del sistema (soft delete por defecto)."
)
async def delete_crop(
    crop_id: int,
    hard_delete: bool = Query(False, description="Eliminación física (true) o lógica (false)")
):
    """Eliminar un cultivo del sistema."""
    # Verificar que el cultivo existe
    existing_crop = crop_service.get_crop_by_id(crop_id)
    if not existing_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cultivo con ID {crop_id} no encontrado"
        )
    
    # Intentar eliminar
    success = crop_service.delete_crop(crop_id, hard_delete=hard_delete)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo eliminar el cultivo"
        )
    
    delete_type = "física" if hard_delete else "lógica"
    return JSONResponse(
        content={
            "message": f"Cultivo eliminado exitosamente (eliminación {delete_type})",
            "crop_id": crop_id,
            "hard_delete": hard_delete
        }
    )


@router.get(
    "/stats/summary",
    summary="Estadísticas de cultivos",
    description="Obtiene estadísticas generales de los cultivos en el sistema."
)
async def get_crop_stats():
    """Obtener estadísticas de cultivos."""
    try:
        stats = crop_service.get_crop_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# Endpoint adicional para verificar códigos únicos
@router.get(
    "/validate/code/{code}",
    summary="Validar código único",
    description="Verifica si un código de cultivo está disponible."
)
async def validate_crop_code(code: str):
    """Validar si un código de cultivo ya existe."""
    crops, _ = crop_service.get_crops(active_only=False)
    existing_codes = [crop.code for crop in crops]
    
    is_available = code not in existing_codes
    
    return JSONResponse(content={
        "code": code,
        "is_available": is_available,
        "message": "Código disponible" if is_available else "Código ya existe"
    })