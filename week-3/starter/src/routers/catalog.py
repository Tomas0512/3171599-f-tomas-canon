from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse

from ..schemas.crop import (
    CropSearchParams,
    CropSearchResult,
    CropCatalogResponse,
    AgriculturalZoneResponse,
    CropRecommendation,
    RecommendationParams,
    CropTypeEnum,
    CropStatusEnum,
    ClimateTypeEnum,
    SoilTypeEnum,
    SortFieldEnum,
    SortOrderEnum
)
from ..services.catalog_service import catalog_service

# ============================================
# ROUTER PRINCIPAL DE CATÁLOGO
# ============================================

router = APIRouter(prefix="/catalog", tags=["Catálogo AgroTech"])


@router.get(
    "/search",
    response_model=CropSearchResult,
    summary="Búsqueda avanzada de cultivos",
    description="""
    Realiza búsqueda avanzada con múltiples filtros:
    - Texto libre en nombre, científico, variedad
    - Filtros por zona, tipo, estado, clima
    - Rangos numéricos: área, rendimiento, precio
    - Filtros booleanos: orgánico, irrigado
    - Ordenamiento y paginación
    - Analytics opcionales
    """
)
async def search_crops(
    # Búsqueda por texto
    q: Optional[str] = Query(None, description="Búsqueda de texto libre"),
    
    # Filtros categóricos
    zone_id: Optional[List[int]] = Query(None, description="IDs de zonas"),
    zone_code: Optional[List[str]] = Query(None, description="Códigos de zonas"),
    crop_type: Optional[List[CropTypeEnum]] = Query(None, description="Tipos de cultivo"),
    status: Optional[List[CropStatusEnum]] = Query(None, description="Estados del cultivo"),
    climate_type: Optional[List[ClimateTypeEnum]] = Query(None, description="Tipos de clima"),
    soil_type: Optional[List[SoilTypeEnum]] = Query(None, description="Tipos de suelo"),
    
    # Filtros numéricos
    min_area: Optional[float] = Query(None, ge=0, description="Área mínima (hectáreas)"),
    max_area: Optional[float] = Query(None, ge=0, description="Área máxima (hectáreas)"),
    min_yield: Optional[float] = Query(None, ge=0, description="Rendimiento mínimo (ton/ha)"),
    max_yield: Optional[float] = Query(None, ge=0, description="Rendimiento máximo (ton/ha)"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo ($/kg)"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo ($/kg)"),
    min_resistance: Optional[int] = Query(None, ge=1, le=10, description="Resistencia mínima a plagas"),
    max_resistance: Optional[int] = Query(None, ge=1, le=10, description="Resistencia máxima a plagas"),
    min_elevation: Optional[int] = Query(None, ge=0, description="Elevación mínima zona (metros)"),
    max_elevation: Optional[int] = Query(None, ge=0, description="Elevación máxima zona (metros)"),
    
    # Filtros booleanos
    organic_only: bool = Query(False, description="Solo cultivos orgánicos"),
    irrigated_zones_only: bool = Query(False, description="Solo zonas con riego"),
    exclude_harvested: bool = Query(False, description="Excluir ya cosechados"),
    active_only: bool = Query(True, description="Solo cultivos activos"),
    with_market_price: bool = Query(False, description="Solo con precio de mercado"),
    
    # Paginación y ordenamiento
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(50, ge=1, le=500, description="Límite de registros"),
    sort_by: SortFieldEnum = Query(SortFieldEnum.NAME, description="Campo para ordenar"),
    order: SortOrderEnum = Query(SortOrderEnum.ASC, description="Orden asc/desc"),
    
    # Configuraciones de respuesta
    include_zone_info: bool = Query(False, description="Incluir info completa de zona"),
    include_analytics: bool = Query(False, description="Incluir analytics y estadísticas")
):
    """Búsqueda avanzada de cultivos con filtros múltiples."""
    try:
        # Crear parámetros de búsqueda
        search_params = CropSearchParams(
            q=q,
            zone_id=zone_id,
            zone_code=zone_code,
            crop_type=crop_type,
            status=status,
            climate_type=climate_type,
            soil_type=soil_type,
            min_area=min_area,
            max_area=max_area,
            min_yield=min_yield,
            max_yield=max_yield,
            min_price=min_price,
            max_price=max_price,
            min_resistance=min_resistance,
            max_resistance=max_resistance,
            min_elevation=min_elevation,
            max_elevation=max_elevation,
            organic_only=organic_only,
            irrigated_zones_only=irrigated_zones_only,
            exclude_harvested=exclude_harvested,
            active_only=active_only,
            with_market_price=with_market_price,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            order=order,
            include_zone_info=include_zone_info,
            include_analytics=include_analytics
        )
        
        # Realizar búsqueda
        result = catalog_service.search_crops(search_params)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )


@router.get(
    "/crops",
    response_model=CropSearchResult,
    summary="Listar cultivos con filtros básicos",
    description="Versión simplificada de búsqueda para casos de uso comunes."
)
async def list_crops_filtered(
    crop_type: Optional[CropTypeEnum] = Query(None, description="Filtrar por tipo"),
    status: Optional[CropStatusEnum] = Query(None, description="Filtrar por estado"),
    organic_only: bool = Query(False, description="Solo orgánicos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Listar cultivos con filtros básicos."""
    search_params = CropSearchParams(
        crop_type=[crop_type] if crop_type else None,
        status=[status] if status else None,
        organic_only=organic_only,
        skip=skip,
        limit=limit,
        include_zone_info=True
    )
    
    return catalog_service.search_crops(search_params)


@router.get(
    "/crops/{crop_id}",
    response_model=CropCatalogResponse,
    summary="Obtener cultivo específico",
    description="Obtiene información completa de un cultivo incluyendo datos de zona."
)
async def get_crop_detail(crop_id: int):
    """Obtener detalles completos de un cultivo."""
    crop = catalog_service.get_crop_by_id(crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cultivo con ID {crop_id} no encontrado"
        )
    
    # Incluir información de zona
    zone = catalog_service.get_zone_by_id(crop.zone_id)
    zone_info = AgriculturalZoneResponse(**zone.to_dict()) if zone else None
    
    crop_dict = crop.to_dict(
        include_zone_info=True,
        zone_data=zone_info.dict() if zone_info else None
    )
    
    return CropCatalogResponse(**crop_dict)


# ============================================
# ENDPOINTS DE ZONAS AGRÍCOLAS
# ============================================

@router.get(
    "/zones",
    response_model=List[AgriculturalZoneResponse],
    summary="Listar zonas agrícolas",
    description="Obtiene todas las zonas agrícolas disponibles."
)
async def get_agricultural_zones():
    """Listar todas las zonas agrícolas."""
    zones = catalog_service.get_zones()
    return [AgriculturalZoneResponse(**zone.to_dict()) for zone in zones]


@router.get(
    "/zones/{zone_id}/crops",
    response_model=CropSearchResult,
    summary="Cultivos por zona",
    description="Obtiene todos los cultivos de una zona específica."
)
async def get_crops_by_zone(
    zone_id: int,
    status: Optional[CropStatusEnum] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Obtener cultivos de una zona específica."""
    # Verificar que la zona existe
    zone = catalog_service.get_zone_by_id(zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona con ID {zone_id} no encontrada"
        )
    
    search_params = CropSearchParams(
        zone_id=[zone_id],
        status=[status] if status else None,
        skip=skip,
        limit=limit,
        include_zone_info=True,
        include_analytics=True
    )
    
    return catalog_service.search_crops(search_params)


# ============================================
# ENDPOINTS DE ANALYTICS
# ============================================

@router.get(
    "/analytics/summary",
    summary="Resumen de analytics",
    description="Estadísticas generales del catálogo de cultivos."
)
async def get_catalog_analytics():
    """Obtener estadísticas generales del catálogo."""
    try:
        # Búsqueda sin filtros para obtener todos los datos
        search_params = CropSearchParams(
            limit=1000,  # Suficiente para obtener todos
            include_analytics=True
        )
        
        result = catalog_service.search_crops(search_params)
        
        return JSONResponse(content={
            "total_crops": result.total_count,
            "active_crops": result.filtered_count,
            "facets": result.facets.dict(),
            "analytics": result.analytics.dict() if result.analytics else {},
            "zones_count": len(catalog_service.get_zones()),
            "generated_at": result.search_metadata["search_time"]
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar analytics: {str(e)}"
        )


@router.get(
    "/analytics/profitability",
    summary="Análisis de rentabilidad",
    description="Análisis de rentabilidad por tipo de cultivo y zona."
)
async def get_profitability_analysis(
    crop_type: Optional[CropTypeEnum] = Query(None, description="Analizar tipo específico"),
    zone_id: Optional[int] = Query(None, description="Analizar zona específica")
):
    """Análisis de rentabilidad de cultivos."""
    search_params = CropSearchParams(
        crop_type=[crop_type] if crop_type else None,
        zone_id=[zone_id] if zone_id else None,
        with_market_price=True,  # Solo cultivos con precio
        limit=500,
        include_analytics=True
    )
    
    result = catalog_service.search_crops(search_params)
    
    if not result.analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay datos suficientes para análisis de rentabilidad"
        )
    
    return JSONResponse(content={
        "total_crops_analyzed": result.filtered_count,
        "average_yield": result.analytics.average_yield,
        "average_price": result.analytics.average_price,
        "total_production_value": result.analytics.profitability_index,
        "organic_percentage": result.analytics.organic_percentage,
        "top_categories": dict(list(result.facets.crop_types.items())[:5]),
        "zone_distribution": result.analytics.zones_distribution,
        "recommendations": "Use /catalog/recommendations para sugerencias personalizadas"
    })


# ============================================
# ENDPOINTS DE RECOMENDACIONES
# ============================================

@router.get(
    "/recommendations",
    response_model=List[CropRecommendation],
    summary="Recomendaciones de cultivos",
    description="Genera recomendaciones inteligentes basadas en criterios especificados."
)
async def get_crop_recommendations(
    zone_id: Optional[int] = Query(None, description="Zona objetivo"),
    budget: Optional[float] = Query(None, gt=0, description="Presupuesto disponible"),
    target_area: Optional[float] = Query(None, gt=0, description="Área objetivo en hectáreas"),
    organic_priority: bool = Query(False, description="Priorizar cultivos orgánicos"),
    profitability_weight: float = Query(0.4, ge=0, le=1, description="Peso de rentabilidad"),
    sustainability_weight: float = Query(0.3, ge=0, le=1, description="Peso de sostenibilidad"),
    risk_tolerance: float = Query(0.3, ge=0, le=1, description="Tolerancia al riesgo"),
    limit: int = Query(5, ge=1, le=20, description="Número máximo de recomendaciones")
):
    """Generar recomendaciones inteligentes de cultivos."""
    try:
        # Validar que los pesos sumen máximo 1.0
        total_weight = profitability_weight + sustainability_weight
        if total_weight > 1.0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La suma de pesos no puede exceder 1.0"
            )
        
        params = RecommendationParams(
            zone_id=zone_id,
            budget=budget,
            target_area=target_area,
            organic_priority=organic_priority,
            profitability_weight=profitability_weight,
            sustainability_weight=sustainability_weight,
            risk_tolerance=risk_tolerance,
            limit=limit
        )
        
        recommendations = catalog_service.generate_recommendations(params)
        
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudieron generar recomendaciones con los criterios especificados"
            )
        
        return recommendations
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar recomendaciones: {str(e)}"
        )


# ============================================
# ENDPOINTS ESPECIALES
# ============================================

@router.get(
    "/seasonal-crops",
    response_model=CropSearchResult,
    summary="Cultivos por temporada",
    description="Encuentra cultivos apropiados para la temporada actual."
)
async def get_seasonal_crops(
    season: str = Query(..., regex="^(spring|summer|fall|winter)$", description="Temporada"),
    climate_zone: Optional[ClimateTypeEnum] = Query(None, description="Tipo de clima"),
    limit: int = Query(20, ge=1, le=100)
):
    """Obtener cultivos recomendados por temporada."""
    # Mapeo simple de temporadas a estados de cultivo
    season_status_map = {
        "spring": [CropStatusEnum.PLANTED, CropStatusEnum.GROWING],
        "summer": [CropStatusEnum.GROWING, CropStatusEnum.FLOWERING],
        "fall": [CropStatusEnum.MATURE, CropStatusEnum.HARVESTED],
        "winter": [CropStatusEnum.PLANTED, CropStatusEnum.MATURE]
    }
    
    search_params = CropSearchParams(
        status=season_status_map.get(season, []),
        climate_type=[climate_zone] if climate_zone else None,
        limit=limit,
        include_zone_info=True,
        sort_by=SortFieldEnum.YIELD_PER_HECTARE,
        order=SortOrderEnum.DESC
    )
    
    return catalog_service.search_crops(search_params)


@router.get(
    "/high-value-crops",
    response_model=CropSearchResult,
    summary="Cultivos de alto valor",
    description="Cultivos con mayor valor de mercado y rentabilidad."
)
async def get_high_value_crops(
    min_price: float = Query(2.0, ge=0, description="Precio mínimo por kg"),
    min_yield: float = Query(5.0, ge=0, description="Rendimiento mínimo"),
    organic_only: bool = Query(False, description="Solo orgánicos"),
    limit: int = Query(15, ge=1, le=50)
):
    """Obtener cultivos de alto valor comercial."""
    search_params = CropSearchParams(
        min_price=min_price,
        min_yield=min_yield,
        organic_only=organic_only,
        with_market_price=True,
        limit=limit,
        sort_by=SortFieldEnum.MARKET_PRICE_PER_KG,
        order=SortOrderEnum.DESC,
        include_analytics=True
    )
    
    return catalog_service.search_crops(search_params)