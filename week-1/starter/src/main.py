from fastapi import FastAPI, HTTPException

# ============================================
# DATOS DE CONFIGURACIÓN AGROTECH
# ============================================

# Mensajes según el rol del actor en el campo
WELCOME_MESSAGES = {
    "es": "¡Bienvenido al sistema de cultivo, {name}! Estado del suelo: Óptimo.",
    "en": "Welcome to the crop management system, {name}! Soil status: Optimal.",
    "fr": "Bienvenue dans le système de culture, {name}! État du sol : Optimal.",
}

app = FastAPI(
    title="AgroTech Management API",
    description="Sistema inteligente para la gestión de cultivos y sensores.",
    version="1.0.0"
)

# RF-01: Información de la API
@app.get("/")
async def root():
    """Retorna información básica de la API de AgroTech."""
    return {
        "name": "AgroTech API",
        "version": "1.0.0",
        "domain": "Agricultura y Gestión de Cultivos",
        "status": "online"
    }

# RF-02: Bienvenida Personalizada (Actor: Agricultor/Agrónomo)
@app.get("/worker/{name}")
async def welcome_worker(name: str, language: str = "es"):
    """Saluda al trabajador agrícola en su idioma."""
    message_template = WELCOME_MESSAGES.get(language, WELCOME_MESSAGES["es"])
    return {
        "message": message_template.format(name=name),
        "language": language,
        "worker": name
    }

# RF-03: Información del Cultivo (Entidad: Crop)
@app.get("/crop/{identifier}/info")
async def get_crop_info(identifier: str, detail_level: str = "basic"):
    """Obtiene datos de un cultivo (ej: Maíz, Trigo)."""
    # Simulamos datos
    data = {
        "id": identifier,
        "type": "Maíz Híbrido",
        "health": "95%"
    }
    
    if detail_level == "full":
        data.update({
            "last_watering": "2024-05-20",
            "soil_ph": 6.5,
            "expected_harvest": "2024-09-15"
        })
    
    return data

# RF-04: Servicio según horario (Riego/Mantenimiento)
@app.get("/service/schedule")
async def get_schedule(hour: int):
    """Indica qué actividad agrícola corresponde según la hora."""
    if not (0 <= hour <= 23):
        raise HTTPException(status_code=400, detail="Hora inválida (0-23)")

    if 6 <= hour <= 11:
        return {"message": "Turno Mañana: Aplicación de fertilizantes y monitoreo.", "action": "fertilizing"}
    elif 12 <= hour <= 17:
        return {"message": "Turno Tarde: Mantenimiento de maquinaria.", "action": "maintenance"}
    else:
        return {"message": "Turno Noche: Riego automático activado.", "action": "irrigation"}

# RF-05: Health Check
@app.get("/health")
async def health_check():
    """Estado de salud de los sensores y la API."""
    return {"status": "healthy", "sensors": "connected", "domain": "agriculture"}