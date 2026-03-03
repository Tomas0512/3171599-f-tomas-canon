from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class CropTypeEnum(str, Enum):
    """Enumeración de tipos de cultivos agrícolas."""
    CEREAL = "cereal"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    LEGUME = "legume"


class CropStatusEnum(str, Enum):
    """Enumeración de estados del cultivo."""
    PLANTED = "planted"
    GROWING = "growing"
    FLOWERING = "flowering"
    MATURE = "mature"
    HARVESTED = "harvested"


class ClimateTypeEnum(str, Enum):
    """Enumeración de tipos de clima."""
    TROPICAL = "tropical"
    TEMPERATE = "temperate"
    ARID = "arid"
    SEMI_ARID = "semi_arid"


class SoilTypeEnum(str, Enum):
    """Enumeración de tipos de suelo."""
    CLAY = "clay"
    SANDY = "sandy"
    LOAM = "loam"
    ROCKY = "rocky"


class SortOrderEnum(str, Enum):
    """Enumeración para orden de clasificación."""
    ASC = "asc"
    DESC = "desc"


class SortFieldEnum(str, Enum):
    """Enumeración de campos válidos para ordenamiento."""
    NAME = "name"
    AREA_HECTARES = "area_hectares"
    YIELD_PER_HECTARE = "yield_per_hectare"
    MARKET_PRICE_PER_KG = "market_price_per_kg"
    PLANTING_DATE = "planting_date"
    EXPECTED_HARVEST = "expected_harvest"
    PEST_RESISTANCE_LEVEL = "pest_resistance_level"


# ============================================
# SCHEMAS DE ZONA AGRÍCOLA
# ============================================

class AgriculturalZoneBase(BaseModel):
    """Schema base para zonas agrícolas."""
    
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=3, max_length=150)
    climate_type: ClimateTypeEnum
    max_capacity_hectares: int = Field(..., gt=0)
    has_irrigation: bool
    average_rainfall_mm: int = Field(..., ge=0, le=5000)
    soil_type: SoilTypeEnum
    elevation_meters: int = Field(..., ge=0, le=6000)


class AgriculturalZoneResponse(AgriculturalZoneBase):
    """Schema de respuesta para zonas agrícolas."""
    
    id: int

    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE CULTIVO EXPANDIDO
# ============================================

class CropCatalogBase(BaseModel):
    """Schema base expandido para cultivos del catálogo."""
    
    name: str = Field(..., min_length=2, max_length=100)
    scientific_name: str = Field(..., min_length=3, max_length=150)
    crop_type: CropTypeEnum
    variety: Optional[str] = Field(None, max_length=100)
    zone_id: int = Field(..., gt=0)
    area_hectares: Decimal = Field(..., gt=0, decimal_places=2)
    planting_date: date
    expected_harvest: date
    status: CropStatusEnum = CropStatusEnum.PLANTED
    yield_per_hectare: Decimal = Field(..., ge=0, decimal_places=2)
    irrigation_frequency_days: int = Field(..., gt=0, le=365)
    fertilizer_type: Optional[str] = Field(None, max_length=100)
    pest_resistance_level: int = Field(..., ge=1, le=10)
    organic_certified: bool = False
    market_price_per_kg: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class CropCatalogResponse(CropCatalogBase):
    """Schema de respuesta para cultivos del catálogo."""
    
    id: int
    code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    zone_info: Optional[AgriculturalZoneResponse] = None

    class Config:
        from_attributes = True


# ============================================
# SCHEMAS DE BÚSQUEDA
# ============================================

class CropSearchParams(BaseModel):
    """Parámetros de búsqueda avanzada para cultivos."""
    
    # Búsqueda por texto libre
    q: Optional[str] = Field(
        None, 
        max_length=200,
        description="Consulta de texto libre en nombre, científico, variedad"
    )
    
    # Filtros categóricos
    zone_id: Optional[List[int]] = Field(None, description="IDs de zonas agrícolas")
    zone_code: Optional[List[str]] = Field(None, description="Códigos de zonas")
    crop_type: Optional[List[CropTypeEnum]] = Field(None, description="Tipos de cultivo")
    status: Optional[List[CropStatusEnum]] = Field(None, description="Estados del cultivo")
    climate_type: Optional[List[ClimateTypeEnum]] = Field(None, description="Tipos de clima de la zona")
    soil_type: Optional[List[SoilTypeEnum]] = Field(None, description="Tipos de suelo")
    
    # Filtros numéricos - rangos
    min_area: Optional[float] = Field(None, ge=0, description="Área mínima en hectáreas")
    max_area: Optional[float] = Field(None, ge=0, description="Área máxima en hectáreas")
    min_yield: Optional[float] = Field(None, ge=0, description="Rendimiento mínimo por hectárea")
    max_yield: Optional[float] = Field(None, ge=0, description="Rendimiento máximo por hectárea")
    min_price: Optional[float] = Field(None, ge=0, description="Precio mínimo por kg")
    max_price: Optional[float] = Field(None, ge=0, description="Precio máximo por kg")
    min_resistance: Optional[int] = Field(None, ge=1, le=10, description="Nivel mínimo resistencia plagas")
    max_resistance: Optional[int] = Field(None, ge=1, le=10, description="Nivel máximo resistencia plagas")
    min_elevation: Optional[int] = Field(None, ge=0, description="Elevación mínima de zona en metros")
    max_elevation: Optional[int] = Field(None, ge=0, description="Elevación máxima de zona en metros")
    
    # Filtros booleanos
    organic_only: bool = Field(False, description="Solo cultivos orgánicos certificados")
    irrigated_zones_only: bool = Field(False, description="Solo zonas con sistema de riego")
    exclude_harvested: bool = Field(False, description="Excluir cultivos ya cosechados")
    active_only: bool = Field(True, description="Solo cultivos activos")
    with_market_price: bool = Field(False, description="Solo cultivos con precio de mercado")
    
    # Paginación y ordenamiento
    skip: int = Field(0, ge=0, description="Registros a saltar")
    limit: int = Field(50, ge=1, le=500, description="Límite de registros")
    sort_by: SortFieldEnum = Field(SortFieldEnum.NAME, description="Campo para ordenar")
    order: SortOrderEnum = Field(SortOrderEnum.ASC, description="Orden ascendente o descendente")
    
    # Configuraciones de respuesta
    include_zone_info: bool = Field(False, description="Incluir información completa de zona")
    include_analytics: bool = Field(False, description="Incluir análisis y estadísticas")
    
    @field_validator('min_area', 'max_area')
    @classmethod
    def validate_area_range(cls, v, values):
        if v is not None and v > 50000:  # Límite práctico
            raise ValueError('El área no puede exceder 50,000 hectáreas')
        return v
    
    @field_validator('min_price', 'max_price')
    @classmethod
    def validate_price_range(cls, v):
        if v is not None and v > 1000:  # Límite práctico
            raise ValueError('El precio no puede exceder $1,000 por kg')
        return v
    
    @model_validator(mode='after')
    def validate_ranges(self) -> 'CropSearchParams':
        """Validar que los rangos mínimos sean menores a los máximos."""
        if self.min_area is not None and self.max_area is not None:
            if self.min_area > self.max_area:
                raise ValueError('El área mínima debe ser menor a la máxima')
        
        if self.min_yield is not None and self.max_yield is not None:
            if self.min_yield > self.max_yield:
                raise ValueError('El rendimiento mínimo debe ser menor al máximo')
        
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                raise ValueError('El precio mínimo debe ser menor al máximo')
        
        if self.min_resistance is not None and self.max_resistance is not None:
            if self.min_resistance > self.max_resistance:
                raise ValueError('La resistencia mínima debe ser menor a la máxima')
        
        return self


class SearchFacets(BaseModel):
    """Facetas (agregaciones) para filtros de búsqueda."""
    
    crop_types: dict[str, int] = {}
    statuses: dict[str, int] = {}
    zones: dict[str, int] = {}
    climate_types: dict[str, int] = {}
    soil_types: dict[str, int] = {}
    organic_count: int = 0
    irrigated_count: int = 0


class SearchAnalytics(BaseModel):
    """Analytics avanzados de los resultados de búsqueda."""
    
    total_area: float = 0
    average_yield: float = 0
    average_price: float = 0
    highest_resistance: int = 0
    organic_percentage: float = 0
    zones_distribution: dict[str, float] = {}
    profitability_index: float = 0


class CropSearchResult(BaseModel):
    """Resultado completo de búsqueda de cultivos."""
    
    crops: List[CropCatalogResponse]
    total_count: int = Field(..., description="Total de registros en BD")
    filtered_count: int = Field(..., description="Registros que pasan los filtros")
    facets: SearchFacets = Field(..., description="Agregaciones por categorías")
    search_metadata: dict = Field(..., description="Metadata de la búsqueda")
    analytics: Optional[SearchAnalytics] = Field(None, description="Análisis estadístico")


# ============================================
# SCHEMAS DE RECOMENDACIONES
# ============================================

class CropRecommendation(BaseModel):
    """Recomendación de cultivo."""
    
    crop: CropCatalogResponse
    score: float = Field(..., ge=0, le=1, description="Puntuación de recomendación")
    reasons: List[str] = Field(..., description="Razones de la recomendación")
    roi_projection: Optional[float] = Field(None, description="ROI proyectado en porcentaje")


class RecommendationParams(BaseModel):
    """Parámetros para generar recomendaciones."""
    
    zone_id: Optional[int] = None
    budget: Optional[float] = Field(None, gt=0)
    target_area: Optional[float] = Field(None, gt=0)
    season_preference: Optional[str] = None
    organic_priority: bool = False
    profitability_weight: float = Field(0.4, ge=0, le=1)
    sustainability_weight: float = Field(0.3, ge=0, le=1)
    risk_tolerance: float = Field(0.3, ge=0, le=1)
    limit: int = Field(5, ge=1, le=20)