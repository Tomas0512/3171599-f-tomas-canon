from datetime import datetime
from typing import Optional


class AgriculturalZone:
    """Modelo para representar una zona agrícola."""
    
    def __init__(
        self,
        id: int,
        code: str,
        name: str,
        climate_type: str,
        max_capacity_hectares: int,
        has_irrigation: bool,
        average_rainfall_mm: int,
        soil_type: str,
        elevation_meters: int
    ):
        self.id = id
        self.code = code
        self.name = name
        self.climate_type = climate_type
        self.max_capacity_hectares = max_capacity_hectares
        self.has_irrigation = has_irrigation
        self.average_rainfall_mm = average_rainfall_mm
        self.soil_type = soil_type
        self.elevation_meters = elevation_meters

    def to_dict(self) -> dict:
        """Convierte el modelo a diccionario."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "climate_type": self.climate_type,
            "max_capacity_hectares": self.max_capacity_hectares,
            "has_irrigation": self.has_irrigation,
            "average_rainfall_mm": self.average_rainfall_mm,
            "soil_type": self.soil_type,
            "elevation_meters": self.elevation_meters
        }


class Crop:
    """Modelo expandido para representar un cultivo con datos de catálogo."""
    
    def __init__(
        self,
        id: int,
        code: str,
        name: str,
        scientific_name: str,
        crop_type: str,
        variety: Optional[str],
        zone_id: int,
        area_hectares: float,
        planting_date: str,
        expected_harvest: str,
        status: str,
        yield_per_hectare: float,
        irrigation_frequency_days: int,
        fertilizer_type: Optional[str],
        pest_resistance_level: int,
        organic_certified: bool,
        market_price_per_kg: Optional[float],
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
        self.zone_id = zone_id
        self.area_hectares = area_hectares
        self.planting_date = planting_date
        self.expected_harvest = expected_harvest
        self.status = status
        self.yield_per_hectare = yield_per_hectare
        self.irrigation_frequency_days = irrigation_frequency_days
        self.fertilizer_type = fertilizer_type
        self.pest_resistance_level = pest_resistance_level
        self.organic_certified = organic_certified
        self.market_price_per_kg = market_price_per_kg
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at

    def to_dict(self, include_zone_info: bool = False, zone_data: Optional[dict] = None) -> dict:
        """Convierte el modelo a diccionario con información opcional de zona."""
        result = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "crop_type": self.crop_type,
            "variety": self.variety,
            "zone_id": self.zone_id,
            "area_hectares": self.area_hectares,
            "planting_date": self.planting_date,
            "expected_harvest": self.expected_harvest,
            "status": self.status,
            "yield_per_hectare": self.yield_per_hectare,
            "irrigation_frequency_days": self.irrigation_frequency_days,
            "fertilizer_type": self.fertilizer_type,
            "pest_resistance_level": self.pest_resistance_level,
            "organic_certified": self.organic_certified,
            "market_price_per_kg": self.market_price_per_kg,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_zone_info and zone_data:
            result["zone_info"] = zone_data
        
        return result

    def matches_search_query(self, query: str) -> bool:
        """Verifica si el cultivo coincide con la consulta de búsqueda."""
        if not query:
            return True
        
        query_lower = query.lower()
        searchable_fields = [
            self.name.lower() if self.name else "",
            self.scientific_name.lower() if self.scientific_name else "",
            self.variety.lower() if self.variety else "",
            self.crop_type.lower() if self.crop_type else "",
            self.fertilizer_type.lower() if self.fertilizer_type else ""
        ]
        
        return any(query_lower in field for field in searchable_fields if field)