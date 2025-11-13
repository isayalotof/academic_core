"""
Distance Calculation Service
Сервис для расчета расстояний между аудиториями
"""

from typing import Optional, Dict, Any
import math
from db.connection import db
from db.queries import distances as queries
from utils.logger import logger
from utils.metrics import track_db_query


class DistanceService:
    """Сервис расчета расстояний между аудиториями"""
    
    @staticmethod
    def _haversine_distance(
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Расчет расстояния между двумя точками по формуле Haversine
        
        Args:
            lat1, lon1: Координаты первой точки
            lat2, lon2: Координаты второй точки
            
        Returns:
            Расстояние в метрах
        """
        R = 6371000  # Радиус Земли в метрах
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def _estimate_walking_time(
        distance_meters: int,
        requires_building_change: bool,
        requires_floor_change: bool,
        floor_diff: int = 0
    ) -> int:
        """
        Оценка времени пешей прогулки
        
        Args:
            distance_meters: Расстояние в метрах
            requires_building_change: Требуется смена здания
            requires_floor_change: Требуется смена этажа
            floor_diff: Разница в этажах
            
        Returns:
            Время в секундах
        """
        # Базовая скорость: 1.4 м/с (типичная скорость ходьбы)
        base_speed = 1.4
        time_seconds = distance_meters / base_speed
        
        # Добавить время на смену здания (выход/вход)
        if requires_building_change:
            time_seconds += 60  # 1 минута
        
        # Добавить время на смену этажа (15 секунд на этаж)
        if requires_floor_change:
            time_seconds += abs(floor_diff) * 15
        
        return int(time_seconds)
    
    @track_db_query('select', 'classroom_distances')
    def get_distance(
        self,
        from_classroom_id: int,
        to_classroom_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получить расстояние между аудиториями (из кэша или рассчитать)
        
        Args:
            from_classroom_id: ID исходной аудитории
            to_classroom_id: ID целевой аудитории
            
        Returns:
            Информация о расстоянии
        """
        if from_classroom_id == to_classroom_id:
            return {
                'distance_meters': 0,
                'walking_time_seconds': 0,
                'requires_building_change': False,
                'requires_floor_change': False
            }
        
        try:
            # Try to get from cache
            result = db.execute_query(
                queries.SELECT_DISTANCE,
                (from_classroom_id, to_classroom_id),
                fetch=True
            )
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'distance_meters': row['distance_meters'],
                    'walking_time_seconds': row['walking_time_seconds'],
                    'requires_building_change': row['requires_building_change'],
                    'requires_floor_change': row['requires_floor_change']
                }
            
            # Calculate distance
            return self._calculate_distance(from_classroom_id, to_classroom_id)
            
        except Exception as e:
            logger.error(
                f"Error getting distance from {from_classroom_id} "
                f"to {to_classroom_id}: {e}"
            )
            return None
    
    @track_db_query('select', 'classrooms')
    def _calculate_distance(
        self,
        from_classroom_id: int,
        to_classroom_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Рассчитать расстояние между аудиториями
        
        Args:
            from_classroom_id: ID исходной аудитории
            to_classroom_id: ID целевой аудитории
            
        Returns:
            Информация о расстоянии
        """
        try:
            # Get classroom details
            result = db.execute_query(
                queries.CALCULATE_DISTANCE_QUERY,
                (from_classroom_id, to_classroom_id),
                fetch=True
            )
            
            if not result or len(result) == 0:
                return None
            
            data = result[0]
            
            # Check if same building
            same_building = data['from_building'] == data['to_building']
            requires_building_change = not same_building
            
            # Check floor change
            floor_diff = abs(data['from_floor'] - data['to_floor'])
            requires_floor_change = floor_diff > 0
            
            # Calculate distance
            if same_building:
                # Same building: use simple floor-based calculation
                # Assume 50m per floor + 20m horizontal
                distance_meters = floor_diff * 50 + 20
            else:
                # Different buildings: use GPS coordinates if available
                if all([
                    data.get('from_lat'),
                    data.get('from_lng'),
                    data.get('to_lat'),
                    data.get('to_lng')
                ]):
                    distance_meters = int(self._haversine_distance(
                        float(data['from_lat']),
                        float(data['from_lng']),
                        float(data['to_lat']),
                        float(data['to_lng'])
                    ))
                else:
                    # Default estimate: 200 meters between buildings
                    distance_meters = 200
            
            # Calculate walking time
            walking_time = self._estimate_walking_time(
                distance_meters,
                requires_building_change,
                requires_floor_change,
                floor_diff
            )
            
            result_data = {
                'distance_meters': distance_meters,
                'walking_time_seconds': walking_time,
                'requires_building_change': requires_building_change,
                'requires_floor_change': requires_floor_change
            }
            
            # Cache the result
            self._cache_distance(
                from_classroom_id,
                to_classroom_id,
                result_data
            )
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return None
    
    @track_db_query('insert', 'classroom_distances')
    def _cache_distance(
        self,
        from_classroom_id: int,
        to_classroom_id: int,
        distance_data: Dict[str, Any]
    ) -> None:
        """Сохранить расстояние в кэш"""
        try:
            params = (
                from_classroom_id,
                to_classroom_id,
                distance_data['distance_meters'],
                distance_data['walking_time_seconds'],
                distance_data['requires_building_change'],
                distance_data['requires_floor_change']
            )
            
            db.execute_query(queries.INSERT_DISTANCE, params, fetch=False)
            
        except Exception as e:
            # Non-critical error, just log it
            logger.warning(f"Failed to cache distance: {e}")

