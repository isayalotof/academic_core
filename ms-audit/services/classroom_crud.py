"""
Classroom CRUD Service
Сервис для CRUD операций с аудиториями
"""

from typing import Optional, Dict, Any, List
from db.connection import db
from db.queries import classrooms as queries
from utils.logger import logger
from utils.metrics import track_db_query


class ClassroomCRUD:
    """CRUD операции для аудиторий"""
    
    @track_db_query('insert', 'classrooms')
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать новую аудиторию
        
        Args:
            data: Данные аудитории
            
        Returns:
            Созданная аудитория с ID
            
        Raises:
            Exception: При ошибке создания
        """
        try:
            params = (
                data['name'],
                data['code'],
                data['building_id'],
                data['floor'],
                data.get('wing'),
                data['capacity'],
                data.get('actual_area'),
                data['classroom_type'],
                data.get('has_projector', False),
                data.get('has_whiteboard', False),
                data.get('has_blackboard', False),
                data.get('has_markers', False),
                data.get('has_chalk', False),
                data.get('has_computers', False),
                data.get('computers_count', 0),
                data.get('has_audio_system', False),
                data.get('has_video_recording', False),
                data.get('has_air_conditioning', False),
                data.get('is_accessible', True),
                data.get('has_windows', True),
                data.get('description'),
                data.get('created_by')
            )
            
            # Use cursor directly with commit=True for INSERT
            with db.get_cursor(commit=True) as cursor:
                cursor.execute(queries.INSERT_CLASSROOM, params)
                result = cursor.fetchall()
            
            if result and len(result) > 0:
                classroom_id = result[0]['id']
                created_at = result[0]['created_at']
                
                # Fetch full classroom data
                classroom = self.get_by_id(classroom_id)
                
                if not classroom:
                    raise Exception(f"Failed to retrieve created classroom {classroom_id}")
                
                logger.info(f"Created classroom: {classroom_id} ({data['code']})")
                return classroom
            else:
                raise Exception("Failed to create classroom")
                
        except Exception as e:
            logger.error(f"Error creating classroom: {e}", exc_info=True)
            raise
    
    @track_db_query('select', 'classrooms')
    def get_by_id(self, classroom_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить аудиторию по ID
        
        Args:
            classroom_id: ID аудитории
            
        Returns:
            Данные аудитории или None
        """
        try:
            result = db.execute_query(
                queries.SELECT_CLASSROOM_BY_ID, 
                (classroom_id,), 
                fetch=True
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting classroom {classroom_id}: {e}")
            return None
    
    @track_db_query('select', 'classrooms')
    def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Получить аудиторию по коду
        
        Args:
            code: Код аудитории
            
        Returns:
            Данные аудитории или None
        """
        try:
            result = db.execute_query(
                queries.SELECT_CLASSROOM_BY_CODE, 
                (code,), 
                fetch=True
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
            
        except Exception as e:
            logger.error(f"Error getting classroom by code {code}: {e}")
            return None
    
    @track_db_query('update', 'classrooms')
    def update(
        self, 
        classroom_id: int, 
        updates: Dict[str, Any], 
        updated_by: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить аудиторию
        
        Args:
            classroom_id: ID аудитории
            updates: Словарь с обновлениями
            updated_by: ID пользователя, который обновляет
            
        Returns:
            Обновленная аудитория или None
        """
        try:
            if not updates:
                return self.get_by_id(classroom_id)
            
            # Build SET clause
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                set_clauses.append(f"{key} = %s")
                params.append(value)
            
            # Add updated_by
            if updated_by is not None:
                set_clauses.append("updated_by = %s")
                params.append(updated_by)
            
            # Add classroom_id for WHERE clause
            params.append(classroom_id)
            
            # Build final query
            query = queries.UPDATE_CLASSROOM.format(
                updates=', '.join(set_clauses)
            )
            
            result = db.execute_query(query, tuple(params), fetch=False)
            
            logger.info(f"Updated classroom {classroom_id}")
            
            # Return updated classroom
            return self.get_by_id(classroom_id)
            
        except Exception as e:
            logger.error(f"Error updating classroom {classroom_id}: {e}", exc_info=True)
            raise
    
    @track_db_query('delete', 'classrooms')
    def delete(
        self, 
        classroom_id: int, 
        hard_delete: bool = False,
        deleted_by: Optional[int] = None
    ) -> bool:
        """
        Удалить аудиторию
        
        Args:
            classroom_id: ID аудитории
            hard_delete: True для физического удаления
            deleted_by: ID пользователя, который удаляет
            
        Returns:
            True если успешно
        """
        try:
            if hard_delete:
                query = queries.DELETE_CLASSROOM_HARD
                params = (classroom_id,)
            else:
                query = queries.DELETE_CLASSROOM_SOFT
                params = (deleted_by, classroom_id)
            
            db.execute_query(query, params, fetch=False)
            
            logger.info(
                f"Deleted classroom {classroom_id} "
                f"({'hard' if hard_delete else 'soft'})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error deleting classroom {classroom_id}: {e}")
            return False
    
    @track_db_query('select', 'classrooms')
    def list_classrooms(
        self,
        page: int = 1,
        page_size: int = 20,
        search_query: Optional[str] = None,
        building_ids: Optional[List[int]] = None,
        classroom_types: Optional[List[str]] = None,
        min_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        sort_by: str = 'name',
        sort_order: str = 'ASC'
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Получить список аудиторий с фильтрацией и пагинацией
        
        Returns:
            Tuple (список аудиторий, общее количество)
        """
        try:
            # Prepare search pattern
            search_pattern = f"%{search_query}%" if search_query else None
            
            # Build query parameters
            params = [
                search_query,
                search_pattern,
                search_pattern,
                search_pattern,
                building_ids,
                building_ids,
                classroom_types,
                classroom_types,
                min_capacity,
                min_capacity,
                max_capacity,
                max_capacity,
                sort_by,
                sort_by,
                sort_by
            ]
            
            # Add pagination
            offset = (page - 1) * page_size
            params.extend([page_size, offset])
            
            # Build query with sort order
            query = queries.SEARCH_CLASSROOMS.format(order=sort_order.upper())
            
            # Execute query
            classrooms = db.execute_query(query, tuple(params), fetch=True)
            
            # Get total count
            count_params = [
                search_query,
                search_pattern,
                search_pattern,
                search_pattern,
                building_ids,
                building_ids,
                classroom_types,
                classroom_types,
                min_capacity,
                min_capacity,
                max_capacity,
                max_capacity
            ]
            
            count_result = db.execute_query(
                queries.COUNT_CLASSROOMS, 
                tuple(count_params), 
                fetch=True
            )
            
            total_count = count_result[0]['total'] if count_result else 0
            
            return [dict(c) for c in classrooms], total_count
            
        except Exception as e:
            logger.error(f"Error listing classrooms: {e}", exc_info=True)
            return [], 0

