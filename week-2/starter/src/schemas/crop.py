from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional
import re

from pydantic import BaseModel, Field, field_validator, model_validator


class CropTypeEnum(str, Enum):
    """Enumeración de tipos de cultivos agrícolas."""
    CEREAL = "cereal"       # Maíz, Trigo, Arroz
    VEGETABLE = "vegetable" # Tomate, Lechuga, Brócoli  
    FRUIT = "fruit"         # Fresas, Manzanas
    LEGUME = "legume"       # Frijol, Soya, Garbanzo


class CropStatusEnum(str, Enum):
    """Enumeración de estados del cultivo."""
    PLANTED = "planted"         # Recién sembrado
    GROWING = "growing"         # En crecimiento
    FLOWERING = "flowering"     # En floración
    MATURE = "mature"           # Maduro para cosecha
    HARVESTED = "harvested"     # Ya cosechado


class CropBase(BaseModel):
    """Schema base para cultivos."""
    
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Nombre del cultivo (ej: Maíz Híbrido Premium)"
    )
    scientific_name: str = Field(
        ..., 
        min_length=3, 
        max_length=150,
        description="Nombre científico del cultivo (ej: Zea mays)"
    )
    crop_type: CropTypeEnum = Field(
        ...,
        description="Tipo de cultivo: cereal, vegetable, fruit, legume"
    )
    variety: Optional[str] = Field(
        None, 
        max_length=100,
        description="Variedad específica del cultivo"
    )
    area_hectares: Decimal = Field(
        ..., 
        gt=0, 
        decimal_places=2,
        description="Área del cultivo en hectáreas"
    )
    planting_date: date = Field(
        ...,
        description="Fecha de siembra del cultivo"
    )
    expected_harvest: date = Field(
        ...,
        description="Fecha estimada de cosecha"
    )
    status: CropStatusEnum = Field(
        default=CropStatusEnum.PLANTED,
        description="Estado actual del cultivo"
    )

    @field_validator('area_hectares')
    @classmethod
    def validate_area(cls, v: Decimal) -> Decimal:
        """Validar que el área esté en rangos realistas."""
        if v <= 0:
            raise ValueError('El área debe ser mayor a 0')
        if v > 10000:  # Límite práctico para una finca
            raise ValueError('El área no puede exceder 10,000 hectáreas')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validar formato del nombre."""
        # No permitir solo números o caracteres especiales
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', v):
            raise ValueError('El nombre debe contener al menos una letra')
        return v.strip()

    @field_validator('scientific_name')
    @classmethod
    def validate_scientific_name(cls, v: str) -> str:
        """Validar formato básico del nombre científico."""
        # Debe tener al menos dos palabras (género y especie)
        words = v.strip().split()
        if len(words) < 2:
            raise ValueError('Nombre científico debe tener al menos género y especie')
        # Primera letra de cada palabra debe ser mayúscula para el género
        if not words[0][0].isupper():
            raise ValueError('El género debe comenzar con mayúscula')
        return v.strip()

    @model_validator(mode='after')
    def validate_harvest_date(self) -> 'CropBase':
        """Validar lógica entre fechas de siembra y cosecha."""
        if self.expected_harvest <= self.planting_date:
            raise ValueError('La fecha de cosecha debe ser posterior a la siembra')
        
        # Validar que no sea más de 2 años en el futuro (cultivos perennes máximo)
        max_date = self.planting_date + timedelta(days=730)
        if self.expected_harvest > max_date:
            raise ValueError('La cosecha no puede ser más de 2 años después de la siembra')
        
        return self


class CropCreate(CropBase):
    """Schema para crear un nuevo cultivo."""
    pass


class CropUpdate(BaseModel):
    """Schema para actualizar un cultivo existente."""
    
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100
    )
    scientific_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150
    )
    crop_type: Optional[CropTypeEnum] = None
    variety: Optional[str] = Field(
        None, 
        max_length=100
    )
    area_hectares: Optional[Decimal] = Field(
        None, 
        gt=0, 
        decimal_places=2
    )
    expected_harvest: Optional[date] = None
    status: Optional[CropStatusEnum] = None

    @field_validator('area_hectares')
    @classmethod
    def validate_area(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validar área si se proporciona."""
        if v is not None:
            if v <= 0:
                raise ValueError('El área debe ser mayor a 0')
            if v > 10000:
                raise ValueError('El área no puede exceder 10,000 hectáreas')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validar nombre si se proporciona."""
        if v is not None:
            if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', v):
                raise ValueError('El nombre debe contener al menos una letra')
            return v.strip()
        return v

    @field_validator('scientific_name')
    @classmethod
    def validate_scientific_name(cls, v: Optional[str]) -> Optional[str]:
        """Validar nombre científico si se proporciona."""
        if v is not None:
            words = v.strip().split()
            if len(words) < 2:
                raise ValueError('Nombre científico debe tener al menos género y especie')
            if not words[0][0].isupper():
                raise ValueError('El género debe comenzar con mayúscula')
            return v.strip()
        return v


class CropResponse(CropBase):
    """Schema de respuesta para cultivos."""
    
    id: int = Field(..., description="ID único del cultivo")
    code: str = Field(..., description="Código único del cultivo (CRP-YYYYMMDD-XXX)")
    is_active: bool = Field(..., description="Si el cultivo está activo")
    created_at: datetime = Field(..., description="Fecha y hora de creación")
    updated_at: Optional[datetime] = Field(None, description="Fecha y hora de última actualización")

    class Config:
        from_attributes = True


class CropListResponse(BaseModel):
    """Schema de respuesta para listas de cultivos."""
    
    crops: list[CropResponse]
    total: int
    skip: int
    limit: int