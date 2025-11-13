"""
Statistics Service
Сервис для статистики и аналитики аудиторий
"""

from typing import Optional, Dict, Any
from db.connection import db
from db.queries import classrooms as queries
from utils.logger import logger
from utils.metrics import track_db_query


class StatisticsService:
    """Сервис статистики и аналитики"""
    
    @track_db_query('select', 'classrooms')
    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Получить общую статистику по всем аудиториям
        
        Returns:
            Словарь со статистикой
        """
        try:
            # Overall statistics
            overall = db.execute_query(
                queries.GET_OVERALL_STATISTICS,
                fetch=True
            )
            
            # Statistics by type
            by_type = db.execute_query(
                queries.GET_STATISTICS_BY_TYPE,
                fetch=True
            )
            
            result = {
                'total_classrooms': 0,
                'total_capacity': 0,
                'average_utilization': 0.0,
                'by_type': {}
            }
            
            if overall and len(overall) > 0:
                result['total_classrooms'] = overall[0]['total_classrooms'] or 0
                result['total_capacity'] = overall[0]['total_capacity'] or 0
                result['average_utilization'] = float(
                    overall[0]['avg_utilization'] or 0
                )
            
            if by_type:
                result['by_type'] = {
                    row['classroom_type']: row['count']
                    for row in by_type
                }
            
            logger.info("Retrieved overall statistics")
            return result
            
        except Exception as e:
            logger.error(f"Error getting overall statistics: {e}")
            return {
                'total_classrooms': 0,
                'total_capacity': 0,
                'average_utilization': 0.0,
                'by_type': {}
            }
    
    @track_db_query('select', 'classrooms')
    def get_building_statistics(
        self, 
        building_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Получить статистику по зданию
        
        Args:
            building_id: ID здания (None для всех зданий)
            
        Returns:
            Словарь со статистикой
        """
        try:
            # Если указан building_id, проверим существование здания
            if building_id:
                from db.queries import buildings as building_queries
                building_check = db.execute_query(
                    building_queries.SELECT_BUILDING_BY_ID,
                    (building_id,),
                    fetch=True
                )
                if not building_check or len(building_check) == 0:
                    logger.warning(f"Building {building_id} not found")
                    return {'buildings': []}
            
            result = db.execute_query(
                queries.GET_BUILDING_STATISTICS,
                (building_id, building_id),
                fetch=True
            )
            
            logger.info(f"Building statistics query result for building_id={building_id}: {result}")
            
            if result and len(result) > 0:
                buildings_stats = []
                
                for row in result:
                    # Логируем сырые данные из БД
                    logger.info(
                        f"Raw row data: id={row.get('id')}, name={row.get('name')}, "
                        f"total_classrooms={row.get('total_classrooms')}, "
                        f"total_capacity={row.get('total_capacity')}, "
                        f"avg_capacity={row.get('avg_capacity')}, "
                        f"total_occupied_slots={row.get('total_occupied_slots')}"
                    )
                    
                    total_slots = row['total_occupied_slots'] or 0
                    total_classrooms = row['total_classrooms'] or 0
                    
                    # Calculate utilization (36 slots per classroom per week)
                    max_slots = total_classrooms * 36 if total_classrooms else 1
                    utilization = round((total_slots / max_slots) * 100, 2) if max_slots > 0 else 0.0
                    
                    building_stat = {
                        'building_id': row['id'],
                        'building_name': row['name'],
                        'total_classrooms': total_classrooms,
                        'total_capacity': int(row['total_capacity'] or 0),
                        'avg_capacity': round(
                            float(row['avg_capacity'] or 0), 2
                        ),
                        'total_occupied_slots': total_slots,
                        'utilization_percentage': utilization
                    }
                    
                    logger.info(f"Processed building stat: {building_stat}")
                    buildings_stats.append(building_stat)
                
                logger.info(f"Retrieved statistics for {len(buildings_stats)} building(s)")
                return {
                    'buildings': buildings_stats
                }
            
            logger.warning(f"No statistics found for building_id={building_id}")
            return {'buildings': []}
            
        except Exception as e:
            logger.error(f"Error getting building statistics: {e}", exc_info=True)
            return {'buildings': []}
    
    @track_db_query('select', 'classroom_schedules')
    def get_classroom_utilization(
        self, 
        classroom_id: int
    ) -> Dict[str, Any]:
        """
        Получить статистику использования конкретной аудитории
        
        Args:
            classroom_id: ID аудитории
            
        Returns:
            Словарь с информацией об использовании
        """
        try:
            result = db.execute_query(
                queries.GET_CLASSROOM_UTILIZATION,
                (classroom_id,),
                fetch=True
            )
            
            if result and len(result) > 0:
                row = result[0]
                return {
                    'classroom_id': row['id'],
                    'classroom_name': row['name'],
                    'occupied_slots': row['occupied_slots'] or 0,
                    'utilization_percentage': float(
                        row['utilization_percentage'] or 0
                    ),
                    'available_slots': 36 - (row['occupied_slots'] or 0)
                }
            
            return {
                'classroom_id': classroom_id,
                'occupied_slots': 0,
                'utilization_percentage': 0.0,
                'available_slots': 36
            }
            
        except Exception as e:
            logger.error(
                f"Error getting utilization for classroom {classroom_id}: {e}"
            )
            return {
                'classroom_id': classroom_id,
                'occupied_slots': 0,
                'utilization_percentage': 0.0,
                'available_slots': 36
            }

