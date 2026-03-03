from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
import statistics

from ..models.crop import AgriculturalZone, Crop
from ..schemas.crop import (
    CropSearchParams, 
    CropSearchResult,
    CropCatalogResponse,
    SearchFacets,
    SearchAnalytics,
    CropRecommendation,
    RecommendationParams,
    AgriculturalZoneResponse,
    CropTypeEnum,
    CropStatusEnum,
    ClimateTypeEnum,
    SoilTypeEnum
)


class CatalogService:
    """Servicio para búsqueda avanzada y catálogo de cultivos."""
    
    def __init__(self):
        self.zones: List[AgriculturalZone] = []
        self.crops: List[Crop] = []
        self.next_zone_id = 1
        self.next_crop_id = 1
        self._initialize_sample_data()

    def search_crops(self, params: CropSearchParams) -> CropSearchResult:
        """Realizar búsqueda avanzada de cultivos."""
        # Aplicar todos los filtros
        filtered_crops = self._apply_filters(params)
        
        # Calcular totales
        total_count = len(self.crops)
        filtered_count = len(filtered_crops)
        
        # Ordenar resultados
        sorted_crops = self._sort_crops(filtered_crops, params.sort_by, params.order)
        
        # Aplicar paginación
        paginated_crops = sorted_crops[params.skip:params.skip + params.limit]
        
        # Convertir a response objects
        crop_responses = []
        for crop in paginated_crops:
            zone_info = None
            if params.include_zone_info:
                zone = self.get_zone_by_id(crop.zone_id)
                if zone:
                    zone_info = AgriculturalZoneResponse(**zone.to_dict())
            
            crop_dict = crop.to_dict(
                include_zone_info=params.include_zone_info,
                zone_data=zone_info.dict() if zone_info else None
            )
            crop_responses.append(CropCatalogResponse(**crop_dict))
        
        # Generar facetas
        facets = self._generate_facets(filtered_crops)
        
        # Metadata de búsqueda
        search_metadata = {
            "query": params.q,
            "filters_applied": self._count_active_filters(params),
            "search_time": datetime.now().isoformat(),
            "total_pages": (filtered_count + params.limit - 1) // params.limit,
            "current_page": params.skip // params.limit + 1
        }
        
        # Analytics opcionales
        analytics = None
        if params.include_analytics and filtered_crops:
            analytics = self._generate_analytics(filtered_crops)
        
        return CropSearchResult(
            crops=crop_responses,
            total_count=total_count,
            filtered_count=filtered_count,
            facets=facets,
            search_metadata=search_metadata,
            analytics=analytics
        )

    def _apply_filters(self, params: CropSearchParams) -> List[Crop]:
        """Aplicar todos los filtros a la lista de cultivos."""
        filtered = self.crops.copy()
        
        # Filtro por activos
        if params.active_only:
            filtered = [c for c in filtered if c.is_active]
        
        # Búsqueda por texto
        if params.q:
            filtered = [c for c in filtered if c.matches_search_query(params.q)]
        
        # Filtros categóricos
        if params.zone_id:
            filtered = [c for c in filtered if c.zone_id in params.zone_id]
        
        if params.zone_code:
            zone_ids = [z.id for z in self.zones if z.code in params.zone_code]
            filtered = [c for c in filtered if c.zone_id in zone_ids]
        
        if params.crop_type:
            crop_types = [ct.value for ct in params.crop_type]
            filtered = [c for c in filtered if c.crop_type in crop_types]
        
        if params.status:
            statuses = [s.value for s in params.status]
            filtered = [c for c in filtered if c.status in statuses]
        
        # Filtrar por tipo de clima de la zona
        if params.climate_type:
            climate_types = [ct.value for ct in params.climate_type]
            zone_ids = [z.id for z in self.zones if z.climate_type in climate_types]
            filtered = [c for c in filtered if c.zone_id in zone_ids]
        
        # Filtrar por tipo de suelo
        if params.soil_type:
            soil_types = [st.value for st in params.soil_type]
            zone_ids = [z.id for z in self.zones if z.soil_type in soil_types]
            filtered = [c for c in filtered if c.zone_id in zone_ids]
        
        # Filtros numéricos - rangos
        if params.min_area is not None:
            filtered = [c for c in filtered if c.area_hectares >= params.min_area]
        if params.max_area is not None:
            filtered = [c for c in filtered if c.area_hectares <= params.max_area]
        
        if params.min_yield is not None:
            filtered = [c for c in filtered if c.yield_per_hectare >= params.min_yield]
        if params.max_yield is not None:
            filtered = [c for c in filtered if c.yield_per_hectare <= params.max_yield]
        
        if params.min_price is not None:
            filtered = [c for c in filtered if c.market_price_per_kg and c.market_price_per_kg >= params.min_price]
        if params.max_price is not None:
            filtered = [c for c in filtered if c.market_price_per_kg and c.market_price_per_kg <= params.max_price]
        
        if params.min_resistance is not None:
            filtered = [c for c in filtered if c.pest_resistance_level >= params.min_resistance]
        if params.max_resistance is not None:
            filtered = [c for c in filtered if c.pest_resistance_level <= params.max_resistance]
        
        # Filtrar por elevación de zona
        if params.min_elevation is not None:
            zone_ids = [z.id for z in self.zones if z.elevation_meters >= params.min_elevation]
            filtered = [c for c in filtered if c.zone_id in zone_ids]
        if params.max_elevation is not None:
            zone_ids = [z.id for z in self.zones if z.elevation_meters <= params.max_elevation]
            filtered = [c for c in filtered if c.zone_id in zone_ids]
        
        # Filtros booleanos
        if params.organic_only:
            filtered = [c for c in filtered if c.organic_certified]
        
        if params.irrigated_zones_only:
            irrigated_zone_ids = [z.id for z in self.zones if z.has_irrigation]
            filtered = [c for c in filtered if c.zone_id in irrigated_zone_ids]
        
        if params.exclude_harvested:
            filtered = [c for c in filtered if c.status != CropStatusEnum.HARVESTED.value]
        
        if params.with_market_price:
            filtered = [c for c in filtered if c.market_price_per_kg is not None]
        
        return filtered

    def _sort_crops(self, crops: List[Crop], sort_by: str, order: str) -> List[Crop]:
        """Ordenar cultivos según criterio especificado."""
        reverse = order == "desc"
        
        if sort_by == "name":
            return sorted(crops, key=lambda c: c.name.lower(), reverse=reverse)
        elif sort_by == "area_hectares":
            return sorted(crops, key=lambda c: c.area_hectares, reverse=reverse)
        elif sort_by == "yield_per_hectare":
            return sorted(crops, key=lambda c: c.yield_per_hectare, reverse=reverse)
        elif sort_by == "market_price_per_kg":
            # Cultivos sin precio van al final
            with_price = [c for c in crops if c.market_price_per_kg is not None]
            without_price = [c for c in crops if c.market_price_per_kg is None]
            sorted_with_price = sorted(with_price, key=lambda c: c.market_price_per_kg, reverse=reverse)
            return sorted_with_price + without_price if not reverse else without_price + sorted_with_price
        elif sort_by == "planting_date":
            return sorted(crops, key=lambda c: c.planting_date, reverse=reverse)
        elif sort_by == "expected_harvest":
            return sorted(crops, key=lambda c: c.expected_harvest, reverse=reverse)
        elif sort_by == "pest_resistance_level":
            return sorted(crops, key=lambda c: c.pest_resistance_level, reverse=reverse)
        
        return crops  # Sin ordenamiento si no se reconoce el campo

    def _generate_facets(self, crops: List[Crop]) -> SearchFacets:
        """Generar facetas (agregaciones) para los resultados."""
        facets = SearchFacets()
        
        # Contar por tipos de cultivo
        for crop in crops:
            facets.crop_types[crop.crop_type] = facets.crop_types.get(crop.crop_type, 0) + 1
        
        # Contar por estados
        for crop in crops:
            facets.statuses[crop.status] = facets.statuses.get(crop.status, 0) + 1
        
        # Contar por zonas (incluir nombre de zona)
        for crop in crops:
            zone = self.get_zone_by_id(crop.zone_id)
            zone_key = f"{zone.code}: {zone.name}" if zone else f"Zona {crop.zone_id}"
            facets.zones[zone_key] = facets.zones.get(zone_key, 0) + 1
        
        # Contar por tipos de clima
        for crop in crops:
            zone = self.get_zone_by_id(crop.zone_id)
            if zone:
                facets.climate_types[zone.climate_type] = facets.climate_types.get(zone.climate_type, 0) + 1
        
        # Contar por tipos de suelo
        for crop in crops:
            zone = self.get_zone_by_id(crop.zone_id)
            if zone:
                facets.soil_types[zone.soil_type] = facets.soil_types.get(zone.soil_type, 0) + 1
        
        # Contar orgánicos e irrigados
        facets.organic_count = len([c for c in crops if c.organic_certified])
        irrigated_zones = {z.id for z in self.zones if z.has_irrigation}
        facets.irrigated_count = len([c for c in crops if c.zone_id in irrigated_zones])
        
        return facets

    def _generate_analytics(self, crops: List[Crop]) -> SearchAnalytics:
        """Generar analytics avanzados de los cultivos."""
        if not crops:
            return SearchAnalytics()
        
        analytics = SearchAnalytics()
        
        # Área total
        analytics.total_area = sum(c.area_hectares for c in crops)
        
        # Rendimiento promedio
        yields = [c.yield_per_hectare for c in crops]
        analytics.average_yield = statistics.mean(yields) if yields else 0
        
        # Precio promedio (solo cultivos con precio)
        prices = [c.market_price_per_kg for c in crops if c.market_price_per_kg is not None]
        analytics.average_price = statistics.mean(prices) if prices else 0
        
        # Mejor resistencia a plagas
        analytics.highest_resistance = max(c.pest_resistance_level for c in crops)
        
        # Porcentaje orgánico
        organic_count = len([c for c in crops if c.organic_certified])
        analytics.organic_percentage = (organic_count / len(crops)) * 100
        
        # Distribución por zonas (porcentaje del área total)
        for crop in crops:
            zone = self.get_zone_by_id(crop.zone_id)
            if zone:
                zone_key = zone.name
                current_area = analytics.zones_distribution.get(zone_key, 0)
                analytics.zones_distribution[zone_key] = current_area + crop.area_hectares
        
        # Convertir distribución a porcentajes
        if analytics.total_area > 0:
            for zone_name in analytics.zones_distribution:
                analytics.zones_distribution[zone_name] = (
                    analytics.zones_distribution[zone_name] / analytics.total_area
                ) * 100
        
        # Índice de productividad (rendimiento promedio * área total * precio promedio)
        analytics.profitability_index = (
            analytics.average_yield * analytics.total_area * analytics.average_price
        ) if analytics.average_price > 0 else analytics.average_yield * analytics.total_area
        
        return analytics

    def _count_active_filters(self, params: CropSearchParams) -> int:
        """Contar cuántos filtros están activos."""
        active_filters = 0
        
        if params.q:
            active_filters += 1
        if params.zone_id:
            active_filters += 1
        if params.zone_code:
            active_filters += 1
        if params.crop_type:
            active_filters += 1
        if params.status:
            active_filters += 1
        if params.climate_type:
            active_filters += 1
        if params.soil_type:
            active_filters += 1
        if params.min_area is not None or params.max_area is not None:
            active_filters += 1
        if params.min_yield is not None or params.max_yield is not None:
            active_filters += 1
        if params.min_price is not None or params.max_price is not None:
            active_filters += 1
        if params.organic_only:
            active_filters += 1
        if params.irrigated_zones_only:
            active_filters += 1
        if params.exclude_harvested:
            active_filters += 1
        if params.with_market_price:
            active_filters += 1
        
        return active_filters

    def get_zone_by_id(self, zone_id: int) -> Optional[AgriculturalZone]:
        """Obtener zona por ID."""
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        return None

    def get_zones(self) -> List[AgriculturalZone]:
        """Obtener todas las zonas."""
        return self.zones.copy()

    def get_crop_by_id(self, crop_id: int) -> Optional[Crop]:
        """Obtener cultivo por ID."""
        for crop in self.crops:
            if crop.id == crop_id and crop.is_active:
                return crop
        return None

    def generate_recommendations(self, params: RecommendationParams) -> List[CropRecommendation]:
        """Generar recomendaciones de cultivos."""
        # Filtrar cultivos candidatos
        candidates = [c for c in self.crops if c.is_active]
        
        if params.zone_id:
            candidates = [c for c in candidates if c.zone_id == params.zone_id]
        
        # Calcular puntuaciones
        recommendations = []
        for crop in candidates[:params.limit * 2]:  # Tomar más para filtrar
            score = self._calculate_recommendation_score(crop, params)
            reasons = self._generate_recommendation_reasons(crop, params)
            roi = self._calculate_roi_projection(crop, params)
            
            crop_response = CropCatalogResponse(**crop.to_dict())
            
            recommendations.append(CropRecommendation(
                crop=crop_response,
                score=score,
                reasons=reasons,
                roi_projection=roi
            ))
        
        # Ordenar por puntuación y tomar los mejores
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:params.limit]

    def _calculate_recommendation_score(self, crop: Crop, params: RecommendationParams) -> float:
        """Calcular puntuación de recomendación."""
        score = 0.0
        
        # Puntuación base por rendimiento
        score += (crop.yield_per_hectare / 20.0) * params.profitability_weight
        
        # Puntuación por resistencia a plagas (sostenibilidad)
        score += (crop.pest_resistance_level / 10.0) * params.sustainability_weight
        
        # Puntuación por precio de mercado
        if crop.market_price_per_kg:
            # Normalizar precio (asumiendo rango 0-10)
            price_score = min(crop.market_price_per_kg / 10.0, 1.0)
            score += price_score * params.profitability_weight
        
        # Bonus por certificación orgánica
        if crop.organic_certified and params.organic_priority:
            score += 0.2
        
        # Factor de riesgo (inversamente proporcional)
        risk_factor = 1.0 - params.risk_tolerance
        score *= (1.0 - risk_factor * 0.3)  # Reducir hasta 30% por alto riesgo
        
        return min(score, 1.0)  # Máximo 1.0

    def _generate_recommendation_reasons(self, crop: Crop, params: RecommendationParams) -> List[str]:
        """Generar razones para la recomendación."""
        reasons = []
        
        if crop.yield_per_hectare > 10:
            reasons.append(f"Alto rendimiento: {crop.yield_per_hectare:.1f} ton/ha")
        
        if crop.pest_resistance_level > 7:
            reasons.append(f"Excelente resistencia a plagas (nivel {crop.pest_resistance_level})")
        
        if crop.market_price_per_kg and crop.market_price_per_kg > 5:
            reasons.append(f"Precio atractivo: ${crop.market_price_per_kg:.2f}/kg")
        
        if crop.organic_certified:
            reasons.append("Certificación orgánica - mayor valor de mercado")
        
        zone = self.get_zone_by_id(crop.zone_id)
        if zone and zone.has_irrigation:
            reasons.append("Zona con sistema de riego disponible")
        
        if not reasons:
            reasons.append("Cultivo balanceado para la zona")
        
        return reasons

    def _calculate_roi_projection(self, crop: Crop, params: RecommendationParams) -> Optional[float]:
        """Calcular ROI proyectado."""
        if not crop.market_price_per_kg or not params.budget or not params.target_area:
            return None
        
        # Ingresos estimados
        estimated_production = crop.yield_per_hectare * params.target_area
        estimated_revenue = estimated_production * crop.market_price_per_kg
        
        # Costos estimados (simplificado)
        cost_per_hectare = params.budget / params.target_area if params.target_area > 0 else 0
        total_costs = cost_per_hectare * params.target_area
        
        if total_costs > 0:
            roi = ((estimated_revenue - total_costs) / total_costs) * 100
            return max(roi, -100)  # Mínimo -100% de pérdida
        
        return None

    def _initialize_sample_data(self):
        """Inicializar datos de muestra expandidos."""
        # Crear zonas agrícolas
        sample_zones = [
            AgriculturalZone(1, "ZONA-A", "Zona Norte - Cultivos Templados", "temperate", 500, True, 1200, "loam", 1800),
            AgriculturalZone(2, "ZONA-B", "Zona Sur - Cultivos Tropicales", "tropical", 750, True, 2500, "clay", 300),
            AgriculturalZone(3, "ZONA-C", "Zona Oeste - Cultivos de Secano", "arid", 300, False, 450, "sandy", 950),
            AgriculturalZone(4, "ZONA-D", "Zona Este - Agricultura Intensiva", "temperate", 400, True, 900, "loam", 1200),
            AgriculturalZone(5, "ZONA-E", "Zona Central - Diversificación", "semi_arid", 600, True, 800, "clay", 1500)
        ]
        
        self.zones.extend(sample_zones)
        self.next_zone_id = len(sample_zones) + 1
        
        # Crear cultivos expandidos
        sample_crops = [
            # Zona A - Templados
            Crop(1, "CRP-20240315-001", "Maíz Amarillo Duro", "Zea mays var. indentata", 
                 "cereal", "Pioneer P30F53", 1, 45.75, "2024-03-15", "2024-08-20", 
                 "growing", 8.2, 7, "NPK 15-15-15", 7, False, 0.85, True),
            
            Crop(2, "CRP-20240301-002", "Trigo de Invierno", "Triticum aestivum", 
                 "cereal", "Canadian Red", 1, 32.50, "2024-03-01", "2024-07-15", 
                 "flowering", 6.5, 10, "Orgánico compostado", 8, True, 1.20, True),
            
            # Zona B - Tropicales
            Crop(3, "CRP-20240201-003", "Café Arábica Premium", "Coffea arabica", 
                 "fruit", "Castillo Paraguaicito", 2, 15.25, "2024-01-10", "2025-01-15", 
                 "mature", 2.1, 5, "Orgánico lombricompuesto", 9, True, 4.50, True),
            
            Crop(4, "CRP-20240220-004", "Plátano Hartón", "Musa acuminata × balbisiana", 
                 "fruit", "Dominico Hartón", 2, 8.75, "2024-02-20", "2024-08-10", 
                 "growing", 35.0, 3, "Fertilizante orgánico", 6, True, 0.45, True),
            
            # Zona C - Secano
            Crop(5, "CRP-20240110-005", "Quinoa Real", "Chenopodium quinoa", 
                 "cereal", "Real Blanca", 3, 12.50, "2024-01-10", "2024-06-15", 
                 "mature", 2.1, 14, "Sin fertilización", 9, True, 4.50, True),
            
            Crop(6, "CRP-20240305-006", "Frijol Tepary", "Phaseolus acutifolius", 
                 "legume", "Negro Jamapa", 3, 6.25, "2024-03-05", "2024-06-20", 
                 "flowering", 1.8, 21, "Inoculante bacteriano", 8, True, 2.30, True),
            
            # Zona D - Intensiva
            Crop(7, "CRP-20240215-007", "Tomate Chonto", "Solanum lycopersicum", 
                 "vegetable", "Milano F1", 4, 3.50, "2024-02-15", "2024-06-30", 
                 "flowering", 45.0, 2, "Fertirrigación NPK", 5, False, 1.80, True),
            
            Crop(8, "CRP-20240301-008", "Lechuga Americana", "Lactuca sativa", 
                 "vegetable", "Great Lakes", 4, 2.25, "2024-03-01", "2024-04-15", 
                 "growing", 25.0, 1, "Hidropónico", 6, True, 3.20, True),
            
            # Zona E - Diversificación
            Crop(9, "CRP-20240125-009", "Aguacate Hass", "Persea americana", 
                 "fruit", "Hass Méxicano", 5, 18.00, "2024-01-25", "2024-12-30", 
                 "growing", 12.5, 7, "Orgánico certificado", 7, True, 6.50, True),
            
            Crop(10, "CRP-20240210-010", "Cebolla Cabezona", "Allium cepa", 
                  "vegetable", "Yellow Granex", 5, 4.75, "2024-02-10", "2024-06-25", 
                  "growing", 28.0, 4, "NPK + microelementos", 6, False, 1.10, True),
            
            # Cultivos adicionales para diversidad
            Crop(11, "CRP-20240105-011", "Arroz Integral", "Oryza sativa", 
                 "cereal", "Fedearroz 67", 2, 25.50, "2024-01-05", "2024-05-20", 
                 "harvested", 7.8, 5, "Urea + DAP", 7, False, 0.95, True),
            
            Crop(12, "CRP-20240320-012", "Cilantro Orgánico", "Coriandrum sativum", 
                 "vegetable", "Nativo criollo", 4, 0.75, "2024-03-20", "2024-05-05", 
                 "planted", 15.0, 1, "Compost orgánico", 8, True, 5.80, True)
        ]
        
        self.crops.extend(sample_crops)
        self.next_crop_id = len(sample_crops) + 1


# Instancia global del servicio
catalog_service = CatalogService()