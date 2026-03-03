from datetime import datetime, date
from typing import List, Optional
from decimal import Decimal

from ..models.crop import Crop
from ..schemas.crop import CropCreate, CropUpdate, CropTypeEnum, CropStatusEnum


class CropService:
    """Servicio para gestionar operaciones CRUD de cultivos."""
    
    def __init__(self):
        self.crops: List[Crop] = []
        self.next_id = 1
        self._initialize_sample_data()

    def _generate_crop_code(self, planting_date: date) -> str:
        """Genera un código único para el cultivo: CRP-YYYYMMDD-XXX"""
        date_str = planting_date.strftime("%Y%m%d")
        # Contar cultivos del mismo día para el sequence
        same_day_count = len([c for c in self.crops if c.planting_date.startswith(date_str)])
        sequence = str(same_day_count + 1).zfill(3)
        return f"CRP-{date_str}-{sequence}"

    def create_crop(self, crop_data: CropCreate) -> Crop:
        """Crear un nuevo cultivo."""
        # Generar código único
        code = self._generate_crop_code(crop_data.planting_date)
        
        # Crear el cultivo
        crop = Crop(
            id=self.next_id,
            code=code,
            name=crop_data.name,
            scientific_name=crop_data.scientific_name,
            crop_type=crop_data.crop_type.value,
            variety=crop_data.variety,
            area_hectares=float(crop_data.area_hectares),
            planting_date=crop_data.planting_date.isoformat(),
            expected_harvest=crop_data.expected_harvest.isoformat(),
            status=crop_data.status.value,
            created_at=datetime.now()
        )
        
        self.crops.append(crop)
        self.next_id += 1
        return crop

    def get_crops(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[CropStatusEnum] = None,
        crop_type: Optional[CropTypeEnum] = None,
        active_only: bool = True
    ) -> tuple[List[Crop], int]:
        """Obtener lista de cultivos con filtros y paginación."""
        filtered_crops = self.crops.copy()
        
        # Filtrar por activos
        if active_only:
            filtered_crops = [c for c in filtered_crops if c.is_active]
        
        # Filtrar por estado
        if status:
            filtered_crops = [c for c in filtered_crops if c.status == status.value]
        
        # Filtrar por tipo
        if crop_type:
            filtered_crops = [c for c in filtered_crops if c.crop_type == crop_type.value]
        
        # Ordenar por fecha de siembra (más reciente primero)
        filtered_crops.sort(key=lambda c: c.planting_date, reverse=True)
        
        total = len(filtered_crops)
        paginated_crops = filtered_crops[skip:skip + limit]
        
        return paginated_crops, total

    def get_crop_by_id(self, crop_id: int) -> Optional[Crop]:
        """Obtener un cultivo por ID."""
        for crop in self.crops:
            if crop.id == crop_id and crop.is_active:
                return crop
        return None

    def update_crop(self, crop_id: int, crop_data: CropUpdate) -> Optional[Crop]:
        """Actualizar un cultivo existente."""
        crop = self.get_crop_by_id(crop_id)
        if not crop:
            return None

        # Actualizar solo los campos proporcionados
        if crop_data.name is not None:
            crop.name = crop_data.name
        if crop_data.scientific_name is not None:
            crop.scientific_name = crop_data.scientific_name
        if crop_data.crop_type is not None:
            crop.crop_type = crop_data.crop_type.value
        if crop_data.variety is not None:
            crop.variety = crop_data.variety
        if crop_data.area_hectares is not None:
            crop.area_hectares = float(crop_data.area_hectares)
        if crop_data.expected_harvest is not None:
            crop.expected_harvest = crop_data.expected_harvest.isoformat()
        if crop_data.status is not None:
            crop.status = crop_data.status.value
        
        # Actualizar timestamp
        crop.updated_at = datetime.now()
        return crop

    def delete_crop(self, crop_id: int, hard_delete: bool = False) -> bool:
        """Eliminar un cultivo (soft o hard delete)."""
        crop = self.get_crop_by_id(crop_id)
        if not crop:
            return False

        if hard_delete:
            # Eliminación física
            self.crops = [c for c in self.crops if c.id != crop_id]
        else:
            # Eliminación lógica (soft delete)
            crop.is_active = False
            crop.updated_at = datetime.now()

        return True

    def get_crop_stats(self) -> dict:
        """Obtener estadísticas de cultivos."""
        active_crops = [c for c in self.crops if c.is_active]
        
        stats = {
            "total_crops": len(active_crops),
            "total_area": sum(c.area_hectares for c in active_crops),
            "crops_by_type": {},
            "crops_by_status": {}
        }
        
        # Estadísticas por tipo
        for crop in active_crops:
            crop_type = crop.crop_type
            stats["crops_by_type"][crop_type] = stats["crops_by_type"].get(crop_type, 0) + 1
        
        # Estadísticas por estado
        for crop in active_crops:
            status = crop.status
            stats["crops_by_status"][status] = stats["crops_by_status"].get(status, 0) + 1
        
        return stats

    def _initialize_sample_data(self):
        """Inicializar con datos de muestra."""
        sample_crops = [
            CropCreate(
                name="Maíz Híbrido Pioneer",
                scientific_name="Zea mays",
                crop_type=CropTypeEnum.CEREAL,
                variety="P30F53",
                area_hectares=Decimal("25.50"),
                planting_date=date(2024, 3, 15),
                expected_harvest=date(2024, 8, 20),
                status=CropStatusEnum.GROWING
            ),
            CropCreate(
                name="Tomate Cherry Premium",
                scientific_name="Solanum lycopersicum var. cerasiforme",
                crop_type=CropTypeEnum.VEGETABLE,
                variety="Sweet 100",
                area_hectares=Decimal("2.75"),
                planting_date=date(2024, 2, 1),
                expected_harvest=date(2024, 5, 15),
                status=CropStatusEnum.FLOWERING
            ),
            CropCreate(
                name="Café Arábica Premium",
                scientific_name="Coffea arabica",
                crop_type=CropTypeEnum.FRUIT,
                variety="Castillo",
                area_hectares=Decimal("15.25"),
                planting_date=date(2024, 1, 10),
                expected_harvest=date(2025, 1, 15),
                status=CropStatusEnum.MATURE
            ),
            CropCreate(
                name="Frijol Común",
                scientific_name="Phaseolus vulgaris",
                crop_type=CropTypeEnum.LEGUME,
                variety="Cargamanto",
                area_hectares=Decimal("8.00"),
                planting_date=date(2024, 2, 20),
                expected_harvest=date(2024, 6, 10),
                status=CropStatusEnum.HARVESTED
            ),
            CropCreate(
                name="Arroz Integral",
                scientific_name="Oryza sativa",
                crop_type=CropTypeEnum.CEREAL,
                variety="Fedearroz 67",
                area_hectares=Decimal("45.75"),
                planting_date=date(2024, 3, 1),
                expected_harvest=date(2024, 7, 15),
                status=CropStatusEnum.GROWING
            )
        ]
        
        for crop_data in sample_crops:
            self.create_crop(crop_data)


# Instancia global del servicio
crop_service = CropService()