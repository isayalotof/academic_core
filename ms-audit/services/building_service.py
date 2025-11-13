"""
Building Service
Бизнес-логика для работы со зданиями
"""

from typing import Dict, Any, List, Optional
from db.connection import db
from db.queries import buildings as building_queries
from utils.logger import logger


class BuildingService:
    """Сервис управления зданиями"""
    
    def create_building(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать здание
        
        Args:
            building_data: Данные здания
            
        Returns:
            ID и timestamp созданного здания
        """
        try:
            params = (
                building_data['name'],
                building_data.get('short_name'),
                building_data.get('code'),
                building_data.get('address'),
                building_data.get('campus'),
                building_data.get('latitude'),
                building_data.get('longitude'),
                building_data.get('total_floors', 1),
                building_data.get('has_elevator', False)
            )
            
            # Use cursor directly with commit=True for INSERT
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(building_queries.INSERT_BUILDING, params)
                result = cursor.fetchall()
            
            if result and len(result) > 0:
                building_id = result[0]['id']
                created_at = result[0]['created_at']
                
                logger.info(
                    f"Created building: {building_id} - "
                    f"{building_data['name']}"
                )
                
                return {
                    'id': building_id,
                    'created_at': str(created_at)
                }
            else:
                raise Exception("Failed to create building")
                
        except Exception as e:
            logger.error(f"Error creating building: {e}", exc_info=True)
            raise
    
    def get_building(self, building_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить здание по ID
        
        Args:
            building_id: ID здания
            
        Returns:
            Данные здания или None
        """
        try:
            result = db.execute_query(
                building_queries.SELECT_BUILDING_BY_ID,
                (building_id,),
                fetch=True
            )
            
            if result and len(result) > 0:
                building = dict(result[0])
                logger.debug(f"Retrieved building {building_id}: {building.get('name', 'N/A')}")
                return building
            
            logger.warning(f"Building {building_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting building {building_id}: {e}", exc_info=True)
            raise
    
    def get_building_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Получить здание по коду
        
        Args:
            code: Код здания
            
        Returns:
            Данные здания или None
        """
        try:
            result = db.execute_query(
                building_queries.SELECT_BUILDING_BY_CODE,
                (code,),
                fetch=True
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting building by code {code}: {e}")
            raise
    
    def list_buildings(self) -> List[Dict[str, Any]]:
        """
        Получить список всех зданий
        
        Returns:
            Список зданий
        """
        try:
            result = db.execute_query(
                building_queries.SELECT_ALL_BUILDINGS,
                fetch=True
            )
            
            if result:
                return [dict(r) for r in result]
            
            return []
            
        except Exception as e:
            logger.error(f"Error listing buildings: {e}")
            raise
    
    def update_building(
        self,
        building_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить здание
        
        Args:
            building_id: ID здания
            updates: Поля для обновления (только переданные поля)
            
        Returns:
            Полные данные обновленного здания
        """
        try:
            # Check if building exists
            existing = self.get_building(building_id)
            if not existing:
                raise Exception(f"Building {building_id} not found")
            
            # Build SET clause dynamically
            set_clauses = []
            params = []
            
            # Allowed fields for update
            allowed_fields = [
                'name', 'short_name', 'code', 'address', 'campus',
                'latitude', 'longitude', 'total_floors', 'has_elevator'
            ]
            
            for key, value in updates.items():
                if key in allowed_fields and value is not None:
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            if not set_clauses:
                # No fields to update, return current data
                return existing
            
            params.append(building_id)
            
            query = building_queries.UPDATE_BUILDING.format(
                updates=', '.join(set_clauses)
            )
            
            # Use cursor directly with commit=True for UPDATE
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(query, tuple(params))
                result = cursor.fetchall()
            
            if result and len(result) > 0:
                logger.info(
                    f"Updated building {building_id}: "
                    f"{', '.join(set_clauses)}"
                )
                # Return full updated building data
                return self.get_building(building_id)
            else:
                raise Exception("Failed to update building")
                
        except Exception as e:
            logger.error(
                f"Error updating building {building_id}: {e}",
                exc_info=True
            )
            raise
    
    def delete_building(self, building_id: int) -> bool:
        """
        Удалить здание
        
        Args:
            building_id: ID здания
            
        Returns:
            True если удалено успешно
        """
        try:
            # Check if building has classrooms
            count_result = db.execute_query(
                building_queries.COUNT_CLASSROOMS_IN_BUILDING,
                (building_id,),
                fetch=True
            )
            
            if count_result and count_result[0]['count'] > 0:
                raise Exception(
                    f"Cannot delete building: {count_result[0]['count']} "
                    "active classrooms exist"
                )
            
            # Use cursor directly with commit=True for DELETE
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(building_queries.DELETE_BUILDING, (building_id,))
            
            logger.info(f"Deleted building {building_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting building {building_id}: {e}")
            raise


# Singleton instance
building_service = BuildingService()

