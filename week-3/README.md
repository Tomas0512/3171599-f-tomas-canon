# 🔍 Proyecto Semana 03: API de Catálogo AgroTech con Búsqueda Avanzada

## 🏛️ Dominio Asignado
**Dominio**: `Agricultura y AgroTech - Sistema de Gestión de Cultivos`

La semana 3 integra toda la funcionalidad CRUD de cultivos con un **sistema de catálogo avanzado** que incluye búsqueda por texto, filtros múltiples, rangos numéricos y relaciones entre entidades del dominio agrícola.

---

## 🎯 Objetivo

Construir una **API de catálogo completa** con búsqueda avanzada y filtros múltiples para optimizar la gestión y consulta de información agrícola, implementando patrones de search, clasificación por zonas y métricas de productividad.

---

## 🌾 Entidades del Sistema

### Zona Agrícola (AgriculturalZone)
```python
AgriculturalZone:
    id: int
    code: str               # A, B, C, Norte, Sur, etc.
    name: str               # "Zona Norte", "Sector Productivo A"
    climate_type: str       # tropical, temperate, arid, semi_arid
    max_capacity_hectares: int
    has_irrigation: bool
    average_rainfall_mm: int
    soil_type: str          # clay, sandy, loam, rocky
    elevation_meters: int
```

### Cultivo Expandido (Crop)
```python
Crop:
    id: int
    code: str               # CRP-YYYYMMDD-XXX
    name: str
    scientific_name: str
    crop_type: CropTypeEnum
    variety: str | None
    zone_id: int            # FK to AgriculturalZone
    area_hectares: Decimal
    planting_date: date
    expected_harvest: date
    status: CropStatusEnum
    yield_per_hectare: Decimal      # Toneladas por hectárea
    irrigation_frequency_days: int  # Cada cuántos días se riega
    fertilizer_type: str | None
    pest_resistance_level: int      # 1-10 scale
    organic_certified: bool
    market_price_per_kg: Decimal | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None
```

---

## 📋 Requisitos Funcionales - Catálogo y Búsqueda

### RF-01: Búsqueda de Texto Completo
**Endpoint:** `GET /catalog/search?q={query}`
- Búsqueda en nombre, nombre científico, variedad
- Búsqueda parcial case-insensitive
- Highlighting de términos encontrados
- Ranking por relevancia

### RF-02: Filtros Múltiples Combinados
**Endpoint:** `GET /catalog/crops`
- **Por zona**: `?zone_id=1` o `?zone_code=A`
- **Por tipo**: `?crop_type=cereal,vegetable`
- **Por estado**: `?status=growing,flowering`
- **Por área**: `?min_area=10&max_area=50`
- **Por rendimiento**: `?min_yield=5.0&max_yield=15.0`
- **Por precio**: `?min_price=2.5&max_price=8.0`
- **Certificación orgánica**: `?organic_only=true`
- **Con irrigación**: `?irrigated_zones_only=true`

### RF-03: Ordenamiento Avanzado
**Parámetros:** `?sort_by=field&order=asc|desc`
- Por nombre (`name`)
- Por área (`area_hectares`)
- Por rendimiento (`yield_per_hectare`)
- Por precio de mercado (`market_price_per_kg`)
- Por fecha de siembra (`planting_date`)
- Por fecha estimada de cosecha (`expected_harvest`)

### RF-04: Agregaciones y Estadísticas
**Endpoint:** `GET /catalog/analytics`
- Total de hectáreas por zona
- Rendimiento promedio por tipo de cultivo
- Distribución de cultivos por estado
- Comparativa de precios de mercado
- Índice de productividad por zona

### RF-05: Recomendaciones Inteligentes
**Endpoint:** `GET /catalog/recommendations`
- Cultivos similares por zona climática
- Rotación de cultivos sugerida
- Optimización de uso del suelo
- Análisis de rentabilidad

---

## 🔧 Filtros Específicos del Dominio Agrícola

### Filtro por Temporada de Siembra
```python
@app.get("/catalog/crops/by-season")
async def get_crops_by_season(
    season: SeasonEnum,          # spring, summer, fall, winter
    hemisphere: str = "north"     # north, south
):
```

### Filtro por Compatibilidad de Suelo
```python
@app.get("/catalog/crops/compatible-soil")
async def get_crops_by_soil_compatibility(
    soil_type: SoilTypeEnum,     # clay, sandy, loam, rocky
    ph_range: str = "6.0-7.5"    # "min-max" format
):
```

### Filtro por Rentabilidad
```python
@app.get("/catalog/crops/profitability")
async def get_crops_by_profitability(
    min_roi_percentage: float = 15.0,
    investment_budget: float = 50000.0,
    market_demand: MarketDemandEnum = None  # high, medium, low
):
```

---

## 🏗️ Arquitectura de Búsqueda

### SearchParams Schema
```python
class CropSearchParams(BaseModel):
    # Búsqueda por texto
    q: str | None = Field(None, description="Consulta de texto libre")
    
    # Filtros categóricos
    zone_id: list[int] | None = None
    crop_type: list[CropTypeEnum] | None = None
    status: list[CropStatusEnum] | None = None
    
    # Filtros numéricos (rangos)
    min_area: float | None = Field(None, ge=0)
    max_area: float | None = Field(None, ge=0)
    min_yield: float | None = Field(None, ge=0)
    max_yield: float | None = Field(None, ge=0)
    min_price: float | None = Field(None, ge=0)
    max_price: float | None = Field(None, ge=0)
    
    # Filtros booleanos
    organic_only: bool = False
    irrigated_zones_only: bool = False
    exclude_harvested: bool = False
    
    # Paginación y ordenamiento
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)
    sort_by: str = Field("name", regex="^(name|area_hectares|yield_per_hectare|market_price_per_kg|planting_date|expected_harvest)$")
    order: str = Field("asc", regex="^(asc|desc)$")
    
    # Configuración de respuesta
    include_zone_info: bool = False
    include_analytics: bool = False
```

### SearchResult Schema
```python
class CropSearchResult(BaseModel):
    crops: list[CropCatalogResponse]
    total_count: int
    filtered_count: int
    facets: dict                    # Agregaciones por categorías
    search_metadata: dict           # Info sobre la búsqueda
    analytics: dict | None = None   # Estadísticas opcionales
```

---

## 📊 Datos Expandidos de Prueba

### Zonas Agrícolas
```python
sample_zones = [
    {
        "code": "ZONA-A",
        "name": "Zona Norte - Cultivos de Clima Templado",
        "climate_type": "temperate",
        "max_capacity_hectares": 500,
        "has_irrigation": True,
        "average_rainfall_mm": 1200,
        "soil_type": "loam",
        "elevation_meters": 1800
    },
    {
        "code": "ZONA-B", 
        "name": "Zona Sur - Cultivos Tropicales",
        "climate_type": "tropical",
        "max_capacity_hectares": 750,
        "has_irrigation": True,
        "average_rainfall_mm": 2500,
        "soil_type": "clay",
        "elevation_meters": 300
    },
    {
        "code": "ZONA-C",
        "name": "Zona Oeste - Cultivos de Secano",
        "climate_type": "arid",
        "max_capacity_hectares": 300,
        "has_irrigation": False,
        "average_rainfall_mm": 450,
        "soil_type": "sandy",
        "elevation_meters": 950
    }
]
```

### Cultivos con Datos Completos
```python
sample_crops = [
    {
        "name": "Maíz Amarillo Duro",
        "scientific_name": "Zea mays var. indentata",
        "crop_type": "cereal",
        "variety": "Pioneer P30F53",
        "zone_id": 1,
        "area_hectares": 45.75,
        "yield_per_hectare": 8.2,
        "irrigation_frequency_days": 7,
        "fertilizer_type": "NPK 15-15-15",
        "pest_resistance_level": 7,
        "organic_certified": False,
        "market_price_per_kg": 0.85,
        "status": "growing"
    },
    {
        "name": "Quinoa Real Boliviana",
        "scientific_name": "Chenopodium quinoa",
        "crop_type": "cereal",
        "variety": "Real Blanca",
        "zone_id": 3,
        "area_hectares": 12.50,
        "yield_per_hectare": 2.1,
        "irrigation_frequency_days": 14,
        "fertilizer_type": "Orgánico compostado",
        "pest_resistance_level": 9,
        "organic_certified": True,
        "market_price_per_kg": 4.50,
        "status": "mature"
    }
]
```

---

## 🚀 Casos de Uso - Búsquedas Complejas

### Búsqueda de Cultivos Rentables para Nueva Zona
```bash
GET /catalog/crops?zone_id=1,2&organic_only=true&min_yield=5.0&min_price=3.0&sort_by=market_price_per_kg&order=desc
```

### Cultivos Listos para Cosecha por Zona
```bash
GET /catalog/crops?status=mature,harvested&zone_code=ZONA-A&sort_by=expected_harvest&order=asc&include_zone_info=true
```

### Análisis de Productividad por Tipo
```bash
GET /catalog/analytics?group_by=crop_type,zone_id&metrics=avg_yield,total_area,avg_price&include_trends=true
```

### Recomendaciones de Rotación
```bash
GET /catalog/recommendations?current_crop_id=5&season=next&optimize_for=profitability&soil_health_priority=high
```

---

## 📈 Métricas de Performance

- ✅ **Búsqueda**: < 200ms para consultas básicas
- ✅ **Filtros múltiples**: < 500ms con 1000+ registros
- ✅ **Agregaciones**: < 1s para análisis complejos
- ✅ **Cache**: Redis opcional para consultas frecuentes
- ✅ **Paginación**: Máximo 500 resultados por página
- ✅ **Full-text search**: Índices optimizados

---

## 🧪 Endpoints de Testing

### Generar Datos Masivos
```bash
POST /catalog/test/generate-data
{
    "zones_count": 10,
    "crops_per_zone": 50,
    "include_analytics": true
}
```

### Benchmark de Búsqueda
```bash
GET /catalog/test/benchmark?query_type=complex&iterations=100
```

---

## 📋 Criterios de Evaluación

- ✅ **Búsqueda por texto** funcional con ranking
- ✅ **Filtros combinados** - al menos 6 tipos diferentes
- ✅ **Rangos numéricos** para área, rendimiento, precios
- ✅ **Ordenamiento** por múltiples campos
- ✅ **Agregaciones** con facets informativos
- ✅ **Paginación** eficiente
- ✅ **Performance** optimizada
- ✅ **Documentación** completa con ejemplos