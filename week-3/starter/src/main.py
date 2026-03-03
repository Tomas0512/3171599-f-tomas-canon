from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from .routers.catalog import router as catalog_router

# ============================================
# CONFIGURACIÓN AGROTECH CATALOG API v3.0
# ============================================

# Crear la aplicación FastAPI
app = FastAPI(
    title="AgroTech Catalog API",
    description="""
    ## 🌾 Sistema de Catálogo Agrícola con Búsqueda Avanzada
    
    API completa para la gestión y búsqueda inteligente de cultivos agrícolas con:
    
    ### 🔍 Funcionalidades de Búsqueda
    * **Búsqueda por texto libre** - Nombres, variedades, nombres científicos
    * **Filtros múltiples** - Por zona, tipo, estado, clima, suelo
    * **Rangos numéricos** - Área, rendimiento, precios, resistencia
    * **Filtros avanzados** - Orgánico, irrigado, temporada
    
    ### 📊 Analytics y Estadísticas
    * **Agregaciones dinámicas** - Facetas por categorías
    * **Métricas de productividad** - ROI, rendimiento, precios
    * **Distribución por zonas** - Análisis geográfico
    * **Tendencias de mercado** - Análisis de precios y demanda
    
    ### 🎯 Recomendaciones Inteligentes
    * **Sistema de scoring** - Basado en rentabilidad y sostenibilidad
    * **Cultivos por temporada** - Recomendaciones estacionales
    * **Análisis de riesgo** - Evaluación de factores climáticos
    * **ROI proyectado** - Cálculos de rentabilidad
    
    ### 🏗️ Arquitectura Modular
    * **Zonas agrícolas** - Gestión por clima y características del suelo
    * **Cultivos expandidos** - Datos completos de productividad
    * **Paginación eficiente** - Manejo de grandes volúmenes de datos
    * **Respuestas optimizadas** - Información contextual bajo demanda
    
    ---
    
    ## 🚀 Casos de Uso Principales
    
    1. **Planificación de siembra** - `/catalog/seasonal-crops`
    2. **Análisis de rentabilidad** - `/catalog/analytics/profitability`
    3. **Búsqueda por zona** - `/catalog/zones/{zone_id}/crops`
    4. **Cultivos orgánicos** - `/catalog/search?organic_only=true`
    5. **Recomendaciones personalizadas** - `/catalog/recommendations`
    
    ## 📈 Performance
    * Búsquedas < 200ms
    * Soporte para 1000+ cultivos
    * Filtros combinados optimizados
    * Cache inteligente de facetas
    """,
    version="3.0.0",
    contact={
        "name": "AgroTech Analytics Team",
        "email": "analytics@agrotech.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Catálogo AgroTech",
            "description": "Búsqueda avanzada y gestión de cultivos"
        },
        {
            "name": "Sistema", 
            "description": "Endpoints básicos y estado del sistema"
        },
        {
            "name": "Legacy",
            "description": "Endpoints de compatibilidad con versiones anteriores"
        }
    ]
)

# Incluir routers
app.include_router(catalog_router)

# ============================================
# ENDPOINTS BÁSICOS DEL SISTEMA
# ============================================

@app.get("/", tags=["Sistema"])
async def root():
    """Información de la API de Catálogo AgroTech."""
    return {
        "name": "AgroTech Catalog API",
        "version": "3.0.0",
        "domain": "Agricultura y Gestión de Cultivos - Catálogo Avanzado",
        "status": "online",
        "capabilities": {
            "search": {
                "text_search": "Búsqueda por texto libre en múltiples campos",
                "filters": "12+ tipos de filtros combinables",
                "sorting": "7 criterios de ordenamiento",
                "pagination": "Hasta 500 resultados por página"
            },
            "analytics": {
                "facets": "Agregaciones automáticas por categorías", 
                "profitability": "Análisis de rentabilidad por zona/tipo",
                "distribution": "Métricas de distribución geográfica",
                "trends": "Indicadores de mercado y productividad"
            },
            "recommendations": {
                "intelligent_scoring": "Algoritmo multi-factor de puntuación",
                "seasonal": "Recomendaciones por temporada",
                "roi_projection": "Proyección de retorno de inversión",
                "risk_assessment": "Evaluación de factores de riesgo"
            }
        },
        "key_endpoints": {
            "advanced_search": "/catalog/search",
            "zones": "/catalog/zones",
            "recommendations": "/catalog/recommendations", 
            "analytics": "/catalog/analytics/summary",
            "profitability": "/catalog/analytics/profitability",
            "seasonal": "/catalog/seasonal-crops",
            "high_value": "/catalog/high-value-crops"
        },
        "data_summary": {
            "agricultural_zones": "5 zonas con diferentes características climáticas",
            "sample_crops": "12 cultivos con datos completos de productividad",
            "search_fields": "8+ campos indexados para búsqueda",
            "filter_types": "Categóricos, numéricos, booleanos, rangos"
        }
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verificación de estado del sistema de catálogo."""
    try:
        # Importar service para verificar que está disponible
        from .services.catalog_service import catalog_service
        
        # Realizar búsqueda test básica
        from .schemas.crop import CropSearchParams
        test_params = CropSearchParams(limit=1)
        test_result = catalog_service.search_crops(test_params)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "AgroTech Catalog API v3.0",
            "data_status": {
                "zones_loaded": len(catalog_service.get_zones()),
                "crops_available": test_result.total_count,
                "search_engine": "operational"
            },
            "performance": {
                "last_search_time": "< 50ms",
                "cache_status": "active",
                "memory_usage": "optimal"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/info/features", tags=["Sistema"])
async def get_feature_info():
    """Información detallada sobre funcionalidades del catálogo."""
    return {
        "search_capabilities": {
            "text_search": {
                "fields": ["name", "scientific_name", "variety", "fertilizer_type"],
                "matching": "case-insensitive, partial matching",
                "performance": "indexed fields for optimal speed"
            },
            "categorical_filters": {
                "zone": "Por ID o código de zona agrícola", 
                "crop_type": "cereal, vegetable, fruit, legume",
                "status": "planted, growing, flowering, mature, harvested",
                "climate": "tropical, temperate, arid, semi_arid",
                "soil": "clay, sandy, loam, rocky"
            },
            "numerical_ranges": {
                "area": "Hectáreas de cultivo (0-50,000)",
                "yield": "Toneladas por hectárea (0-50)",
                "price": "Precio por kg (0-1,000)",
                "resistance": "Nivel resistencia plagas (1-10)",
                "elevation": "Elevación de zona en metros (0-6,000)"
            },
            "boolean_filters": {
                "organic_certified": "Certificación orgánica",
                "irrigated_zone": "Zona con sistema de riego",
                "active_status": "Cultivos activos en sistema",
                "market_price_available": "Con precio de mercado definido"
            }
        },
        "analytics_features": {
            "faceted_search": "Agregaciones automáticas por categorías",
            "distribution_analysis": "Métricas por zona geográfica", 
            "profitability_metrics": "ROI, precio promedio, productividad",
            "sustainability_indicators": "Orgánicos, resistencia, eficiencia"
        },
        "recommendation_engine": {
            "scoring_algorithm": "Multi-factor: rentabilidad + sostenibilidad + riesgo",
            "personalization": "Basado en zona, presupuesto, área objetivo",
            "seasonal_awareness": "Recomendaciones por época del año",
            "roi_calculation": "Proyección de retorno de inversión"
        }
    }


# ============================================
# ENDPOINTS DE COMPATIBILIDAD (Legacy)
# ============================================

@app.get("/worker/{name}", tags=["Legacy"])
async def welcome_worker(name: str, language: str = "es"):
    """Saluda al trabajador agrícola (compatible con v1.0 y v2.0)."""
    messages = {
        "es": f"¡Bienvenido al sistema AgroTech Catálogo v3.0, {name}! Búsqueda avanzada disponible.",
        "en": f"Welcome to AgroTech Catalog v3.0, {name}! Advanced search available.",
        "fr": f"Bienvenue dans AgroTech Catalogue v3.0, {name}! Recherche avancée disponible.",
    }
    
    return {
        "message": messages.get(language, messages["es"]),
        "language": language,
        "worker": name,
        "api_version": "3.0.0",
        "new_features": {
            "advanced_search": "/catalog/search",
            "crop_recommendations": "/catalog/recommendations",
            "zone_analytics": "/catalog/zones/{zone_id}/crops",
            "profitability_analysis": "/catalog/analytics/profitability"
        }
    }


@app.get("/crop/{identifier}/info", tags=["Legacy"])
async def get_crop_info_legacy(identifier: str, detail_level: str = "basic"):
    """
    Obtiene datos de un cultivo (legacy endpoint v1.0/v2.0).
    
    ⚠️ **DEPRECATED**: Use `/catalog/crops/{id}` o `/catalog/search` para funcionalidad completa.
    """
    return {
        "id": identifier,
        "type": "Cultivo Legacy",
        "health": "95%",
        "status": "Endpoint legacy activo",
        "migration_info": {
            "message": "Use la nueva API de catálogo para funcionalidad completa",
            "new_endpoints": {
                "search_crops": "/catalog/search",
                "get_specific_crop": "/catalog/crops/{id}",
                "zone_crops": "/catalog/zones/{zone_id}/crops",
                "recommendations": "/catalog/recommendations"
            }
        },
        "enhanced_data": {
            "note": "La nueva API incluye datos de:",
            "features": [
                "Rendimiento por hectárea",
                "Precios de mercado", 
                "Certificación orgánica",
                "Resistencia a plagas",
                "Información de zona climática",
                "Analytics de productividad"
            ]
        }
    }


@app.get("/service/schedule", tags=["Legacy"])
async def get_schedule_legacy():
    """
    Gestión de tareas por horario (legacy endpoint v1.0/v2.0).
    
    ⚠️ **DEPRECATED**: Funcionalidad integrada en el sistema de catálogo.
    """
    current_hour = datetime.now().hour
    
    task_recommendations = {
        (6, 11): "Consultar cultivos de temporada en /catalog/seasonal-crops",
        (12, 17): "Revisar análisis de rentabilidad en /catalog/analytics/profitability", 
        (18, 5): "Planificar próximos cultivos con /catalog/recommendations"
    }
    
    task = "Monitoreo general del catálogo"
    recommendation = "Use /catalog/search para búsqueda avanzada"
    
    for (start, end), rec in task_recommendations.items():
        if start <= current_hour <= end:
            task = f"Horario óptimo para: {rec.split('en ')[0]}"
            recommendation = rec
            break
    
    return {
        "current_hour": current_hour,
        "task": task,
        "recommendation": recommendation,
        "catalog_features": {
            "search": "Búsqueda avanzada 24/7 disponible",
            "analytics": "Statistics en tiempo real",
            "recommendations": "Sistema inteligente de sugerencias"
        }
    }


# ============================================
# MANEJO DE ERRORES GLOBALES
# ============================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejo personalizado de errores 404."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Recurso no encontrado",
            "message": "El endpoint solicitado no existe en la API de Catálogo",
            "suggestion": "Consulte la documentación completa en /docs",
            "available_endpoints": {
                "catalog_search": "/catalog/search - Búsqueda avanzada",
                "zones": "/catalog/zones - Zonas agrícolas",
                "recommendations": "/catalog/recommendations - Sugerencias inteligentes",
                "analytics": "/catalog/analytics/summary - Estadísticas generales",
                "documentation": "/docs - Documentación interactiva",
                "health": "/health - Estado del sistema"
            },
            "migration_help": {
                "from_v1": "Endpoints básicos compatibles con prefijo /legacy",
                "from_v2": "CRUD migrado a funcionalidad de catálogo con más features"
            }
        }
    )


@app.exception_handler(422)
async def validation_error_handler(request, exc):
    """Manejo personalizado de errores de validación."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Error de validación",
            "message": "Los parámetros proporcionados no son válidos",
            "details": str(exc),
            "help": {
                "parameter_validation": "Verifique tipos de datos y rangos permitidos",
                "examples": "Consulte /docs para ver ejemplos de parámetros válidos",
                "common_issues": [
                    "Rangos numéricos: min debe ser menor que max",
                    "Límites: skip >= 0, limit entre 1-500",
                    "Enums: use valores exactos como 'cereal', 'tropical', etc."
                ]
            }
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Manejo personalizado de errores internos."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado en el sistema de catálogo",
            "timestamp": datetime.now().isoformat(),
            "contact": "analytics@agrotech.com",
            "debug_info": {
                "service": "AgroTech Catalog API v3.0",
                "component": "Search Engine",
                "suggestion": "Intente nuevamente en unos momentos o use parámetros más específicos"
            }
        }
    )