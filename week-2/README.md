# 🌾 Proyecto Semana 02: API CRUD Completa para Gestión de Cultivos

## 🏛️ Dominio Asignado
**Dominio**: `Agricultura y AgroTech - Sistema de Gestión de Cultivos`

La semana 2 expande nuestra API básica de AgroTech implementando un **CRUD completo** para la gestión profesional de cultivos agrícolas, con validación robusta usando Pydantic v2.

---

## 🎯 Objetivo

Construir una **API REST CRUD completa** para gestionar cultivos agrícolas usando FastAPI con Pydantic v2 para validación de datos, implementando todas las operaciones CRUD (Create, Read, Update, Delete) con validadores específicos del dominio agrícola.

---

## 🌱 Modelo de Entidad: Cultivo (Crop)

### Campos Obligatorios (10 campos mínimo)

```python
Crop:
    id: int                    # Auto-generated (primary key)
    code: str                  # Unique, formato: CRP-YYYYMMDD-XXX
    name: str                  # 2-100 chars (ej: "Maíz Híbrido Premium")
    scientific_name: str       # Nombre científico (ej: "Zea mays")
    crop_type: CropTypeEnum    # cereal, vegetable, fruit, legume
    variety: str | None        # Variedad específica del cultivo
    area_hectares: Decimal     # Área en hectáreas (> 0, 2 decimales)
    planting_date: date        # Fecha de siembra
    expected_harvest: date     # Fecha estimada de cosecha
    status: CropStatusEnum     # planted, growing, flowering, mature, harvested
    is_active: bool            # Default: True
    created_at: datetime       # Timestamp de creación
    updated_at: datetime | None # Timestamp de última actualización
```

### Enumeraciones Específicas

```python
class CropTypeEnum(str, Enum):
    CEREAL = "cereal"         # Maíz, Trigo, Arroz
    VEGETABLE = "vegetable"   # Tomate, Lechuga, Brócoli
    FRUIT = "fruit"           # Fresas, Manzanas  
    LEGUME = "legume"         # Frijol, Soya, Garbanzo

class CropStatusEnum(str, Enum):
    PLANTED = "planted"       # Recién sembrado
    GROWING = "growing"       # En crecimiento
    FLOWERING = "flowering"   # En floración  
    MATURE = "mature"         # Maduro para cosecha
    HARVESTED = "harvested"   # Ya cosechado
```

---

## 📋 Requisitos Funcionales - CRUD Completo

### RF-01: Crear Cultivo
**Endpoint:** `POST /crops/`
- Validar todos los campos obligatorios
- Generar código único automáticamente
- Validar que fecha de cosecha > fecha de siembra
- Retornar el cultivo creado con status 201

### RF-02: Listar Cultivos
**Endpoint:** `GET /crops/`
- Parámetros opcionales: `skip`, `limit` para paginación
- Filtro opcional por `status` y `crop_type`
- Ordenamiento por fecha de siembra (más reciente primero)

### RF-03: Obtener Cultivo por ID
**Endpoint:** `GET /crops/{crop_id}`
- Validar que el ID existe
- Retornar error 404 si no se encuentra
- Incluir información completa del cultivo

### RF-04: Actualizar Cultivo
**Endpoint:** `PUT /crops/{crop_id}`
- Validar campos modificables
- Actualizar `updated_at` automáticamente
- No permitir cambios en `id`, `code`, `created_at`
- Validar lógica de negocio (fechas, estados)

### RF-05: Eliminar Cultivo
**Endpoint:** `DELETE /crops/{crop_id}`
- Soft delete: marcar `is_active = False`
- Retornar confirmación de eliminación
- Hard delete opcional con parámetro `?hard=true`

---

## 🔧 Validadores Específicos del Dominio

### Validador de Código de Cultivo
```python
@field_validator('code')
@classmethod
def validate_crop_code(cls, v: str) -> str:
    pattern = r'^CRP-\d{8}-\d{3}$'  # CRP-YYYYMMDD-XXX
    if not re.match(pattern, v):
        raise ValueError('Código debe seguir formato CRP-YYYYMMDD-XXX')
    return v.upper()
```

### Validador de Área
```python
@field_validator('area_hectares')
@classmethod
def validate_area(cls, v: Decimal) -> Decimal:
    if v <= 0:
        raise ValueError('El área debe ser mayor a 0')
    if v > 10000:  # Límite práctico
        raise ValueError('El área no puede exceder 10,000 hectáreas')
    return v
```

### Validador de Fechas
```python
@model_validator(mode='after')
def validate_harvest_date(self) -> 'CropCreate':
    if self.expected_harvest <= self.planting_date:
        raise ValueError('La fecha de cosecha debe ser posterior a la siembra')
    
    # Validar que no sea más de 2 años en el futuro
    max_date = self.planting_date + timedelta(days=730)
    if self.expected_harvest > max_date:
        raise ValueError('La cosecha no puede ser más de 2 años después')
    
    return self
```

---

## 🏗️ Arquitectura de Código

### Estructura de Archivos
```
src/
├── main.py                    # FastAPI app y configuración
├── models/
│   └── crop.py               # Modelo de datos interno
├── schemas/
│   └── crop.py               # Schemas Pydantic (request/response)
├── routers/
│   └── crops.py              # Endpoints CRUD
└── services/
    └── crop_service.py       # Lógica de negocio
```

### Schemas Pydantic

```python
# Base Schema
class CropBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    scientific_name: str = Field(..., min_length=3, max_length=150)
    crop_type: CropTypeEnum
    variety: str | None = Field(None, max_length=100) 
    area_hectares: Decimal = Field(..., gt=0, decimal_places=2)
    planting_date: date
    expected_harvest: date
    status: CropStatusEnum = CropStatusEnum.PLANTED

# Request Schemas
class CropCreate(CropBase):
    pass  # Heredará validaciones del base

class CropUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    variety: str | None = Field(None, max_length=100)
    area_hectares: Decimal | None = Field(None, gt=0, decimal_places=2)
    expected_harvest: date | None = None
    status: CropStatusEnum | None = None

# Response Schemas  
class CropResponse(CropBase):
    id: int
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
```

---

## 📊 Datos de Prueba

### Cultivos de Ejemplo
```python
sample_crops = [
    {
        "name": "Maíz Híbrido Pioneer",
        "scientific_name": "Zea mays",
        "crop_type": "cereal",
        "variety": "P30F53",
        "area_hectares": 25.50,
        "planting_date": "2024-03-15",
        "expected_harvest": "2024-08-20",
        "status": "growing"
    },
    {
        "name": "Tomate Cherry Premium",
        "scientific_name": "Solanum lycopersicum var. cerasiforme",
        "crop_type": "vegetable",
        "variety": "Sweet 100",
        "area_hectares": 2.75,
        "planting_date": "2024-02-01",
        "expected_harvest": "2024-05-15",
        "status": "flowering"
    }
]
```

---

## 🚀 Instalación y Ejecución

### Requisitos
```bash
pip install fastapi[standard] python-multipart
```

### Ejecutar
```bash
cd starter
uvicorn src.main:app --reload
```

### Acceder a Documentación
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🧪 Casos de Prueba

### Crear Cultivo Válido
```bash
POST /crops/
{
    "name": "Café Arábica Premium",
    "scientific_name": "Coffea arabica",
    "crop_type": "fruit",
    "variety": "Castillo",
    "area_hectares": 15.25,
    "planting_date": "2024-04-01",
    "expected_harvest": "2025-01-15",
    "status": "planted"
}
```

### Validaciones que Deben Fallar
```bash
# Área negativa
{"area_hectares": -5.0}  # Error: debe ser > 0

# Fecha inválida  
{"planting_date": "2024-03-15", "expected_harvest": "2024-02-01"}  # Error: cosecha anterior a siembra

# Código malformado
{"code": "INVALID-CODE"}  # Error: formato incorrecto
```

---

## 📈 Criterios de Evaluación

- ✅ **Modelo completo** con mínimo 10 campos validados
- ✅ **CRUD funcional** - todos los endpoints implementados
- ✅ **Pydantic v2** con validators personalizados
- ✅ **Manejo de errores** apropiado (404, 422, etc.)
- ✅ **Documentación** automática funcional
- ✅ **Arquitectura limpia** - separación de responsabilidades
- ✅ **Casos de prueba** exitosos y de error