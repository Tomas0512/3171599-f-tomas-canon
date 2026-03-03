from datetime import datetime
from typing import Optional


class Crop:
    """Modelo interno para representar un cultivo."""
    
    def __init__(
        self,
        id: int,
        code: str,
        name: str,
        scientific_name: str,
        crop_type: str,
        variety: Optional[str],
        area_hectares: float,
        planting_date: str,
        expected_harvest: str,
        status: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.code = code
        self.name = name
        self.scientific_name = scientific_name
        self.crop_type = crop_type
        self.variety = variety
        self.area_hectares = area_hectares
        self.planting_date = planting_date
        self.expected_harvest = expected_harvest
        self.status = status
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario para serialización."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "crop_type": self.crop_type,
            "variety": self.variety,
            "area_hectares": self.area_hectares,
            "planting_date": self.planting_date,
            "expected_harvest": self.expected_harvest,
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }