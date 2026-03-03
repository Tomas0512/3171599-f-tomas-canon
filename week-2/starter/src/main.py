from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

from .routers.crops import router as crops_router

# ============================================
# CONFIGURACIÓN AGROTECH API v2.0
# ============================================

# Mensajes según el rol del actor en el campo (mantenidos de week-1)
WELCOME_MESSAGES = {
    "es": "¡Bienvenido al sistema AgroTech v2.0, {name}! CRUD completo disponible.",
    "en": "Welcome to AgroTech v2.0 system, {name}! Full CRUD available.",
    "fr": "Bienvenue dans le système AgroTech v2.0, {name}! CRUD complet disponible.",
}

# Crear la aplicación FastAPI
app = FastAPI(
    title="AgroTech CRUD API",
    description="""
    Sistema completo de gestión de cultivos agrícolas con operaciones CRUD.
    
    ## Funcionalidades
    
    * **Gestión de Cultivos** - CRUD completo para cultivos agrícolas
    * **Validación Robusta** - Pydantic v2 con validadores específicos del dominio
    * **Filtros Avanzados** - Búsqueda por tipo, estado, área y más
    * **Códigos Únicos** - Generación automática de códigos CRP-YYYYMMDD-XXX
    * **Estadísticas** - Métricas en tiempo real del sistema
    
    ## Compatibilidad
    
    Mantiene endpoints básicos de la v1.0 para retrocompatibilidad.
    """,
    version="2.0.0",
    contact={
        "name": "AgroTech Development Team",
        "email": "dev@agrotech.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Incluir routers
app.include_router(crops_router)

# ============================================
# ENDPOINTS BÁSICOS (Compatibilidad week-1)
# ============================================

@app.get("/", tags=["Sistema"])
async def root():
    """Información básica de la API (compatible con week-1)."""
    return {
        "name": "AgroTech CRUD API",
        "version": "2.0.0",
        "domain": "Agricultura y Gestión de Cultivos",
        "status": "online",
        "features": [
            "CRUD completo de cultivos",
            "Validación con Pydantic v2",
            "Filtros avanzados",
            "Códigos únicos automáticos",
            "Estadísticas en tiempo real"
        ],
        "endpoints": {
            "crops": "/crops/",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verificación de estado del sistema."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AgroTech API v2.0"
    }


@app.get("/worker/{name}", tags=["Sistema"])
async def welcome_worker(name: str, language: str = "es"):
    """Saluda al trabajador agrícola en su idioma (compatible con week-1)."""
    message_template = WELCOME_MESSAGES.get(language, WELCOME_MESSAGES["es"])
    return {
        "message": message_template.format(name=name),
        "language": language,
        "worker": name,
        "api_version": "2.0.0",
        "new_features": "CRUD completo disponible en /crops/"
    }


# ============================================
# ENDPOINTS LEGACY (Compatibilidad week-1)
# ============================================

@app.get("/crop/{identifier}/info", tags=["Legacy"])
async def get_crop_info_legacy(identifier: str, detail_level: str = "basic"):
    """
    Obtiene datos de un cultivo (legacy endpoint de week-1).
    
    ⚠️ **DEPRECATED**: Use `/crops/{id}` para la nueva funcionalidad CRUD.
    """
    # Simulamos datos para compatibilidad
    base_data = {
        "id": identifier,
        "type": "Cultivo Legacy",
        "health": "95%",
        "status": "Endpoint legacy - usar /crops/ para funcionalidad completa"
    }
    
    if detail_level == "full":
        base_data.update({
            "soil_ph": 6.5,
            "last_irrigation": "2024-03-15",
            "sensors": ["humidity", "temperature"],
            "migration_note": "Use POST /crops/ para crear cultivos con validación completa"
        })
    
    return base_data


@app.get("/service/schedule", tags=["Legacy"])
async def get_schedule_legacy():
    """
    Gestión de tareas por horario (legacy endpoint de week-1).
    
    ⚠️ **DEPRECATED**: Funcionalidad integrada en el sistema de cultivos.
    """
    current_hour = datetime.now().hour
    
    if 6 <= current_hour <= 11:
        task = "Fertilización programada"
        recommendation = "Utilice /crops/ para gestionar cultivos específicos"
    elif 12 <= current_hour <= 17:
        task = "Mantenimiento de cultivos"
        recommendation = "Consulte estadísticas en /crops/stats/summary"
    else:
        task = "Monitoreo nocturno"
        recommendation = "API CRUD 24/7 disponible en /crops/"
    
    return {
        "current_hour": current_hour,
        "task": task,
        "recommendation": recommendation,
        "new_api": "Use /crops/ para gestión completa de cultivos"
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
            "message": "El endpoint solicitado no existe",
            "suggestion": "Consulte la documentación en /docs",
            "available_endpoints": {
                "crops": "/crops/",
                "documentation": "/docs", 
                "health": "/health"
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
            "message": "Ha ocurrido un error inesperado",
            "timestamp": datetime.now().isoformat(),
            "contact": "dev@agrotech.com"
        }
    )