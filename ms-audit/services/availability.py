"""
Classroom Availability Service
Сервис для поиска свободных аудиторий и бронирования
"""

from typing import Optional, Dict, Any, List
from db.connection import db
from db.queries import classrooms as classroom_queries
from db.queries import schedules as schedule_queries
from utils.logger import logger
from utils.metrics import track_db_query


class AvailabilityService:
    """Сервис управления доступностью аудиторий"""
    
    @track_db_query('select', 'classrooms')
    def find_available(
        self,
        day_of_week: int,
        time_slot: int,
        min_capacity: int = 1,
        need_projector: bool = False,
        need_whiteboard: bool = False,
        need_computers: bool = False,
        building_ids: Optional[List[int]] = None,
        classroom_types: Optional[List[str]] = None,
        sort_by: str = 'capacity'
    ) -> List[Dict[str, Any]]:
        """
        Найти свободные аудитории по критериям
        
        Args:
            day_of_week: День недели (1-6)
            time_slot: Номер пары (1-6)
            min_capacity: Минимальная вместимость
            need_projector: Требуется проектор
            need_whiteboard: Требуется доска
            need_computers: Требуются компьютеры
            building_ids: Список ID зданий (фильтр)
            classroom_types: Список типов аудиторий (фильтр)
            sort_by: Поле для сортировки
            
        Returns:
            Список доступных аудиторий с дополнительной информацией
        """
        try:
            # Prepare parameters
            params = [
                min_capacity,
                need_projector,
                need_whiteboard,
                need_computers,
                building_ids,
                building_ids,
                classroom_types,
                classroom_types,
                day_of_week,
                time_slot,
                sort_by,
                sort_by
            ]
            
            # Determine sort order
            sort_order = 'ASC' if sort_by == 'capacity' else 'DESC'
            query = classroom_queries.FIND_AVAILABLE_CLASSROOMS.format(
                order=sort_order
            )
            
            # Execute query
            classrooms = db.execute_query(query, tuple(params), fetch=True)
            
            # Enhance results with additional info
            result = []
            for classroom in classrooms:
                classroom_dict = dict(classroom)
                
                # Calculate utilization score
                total_slots = classroom_dict.get('total_scheduled_slots', 0)
                utilization_score = round((total_slots / 36) * 100, 2) if total_slots else 0
                
                # Check if fully equipped based on requirements
                fully_equipped = True
                if need_projector and not classroom_dict.get('has_projector'):
                    fully_equipped = False
                if need_whiteboard and not classroom_dict.get('has_whiteboard'):
                    fully_equipped = False
                if need_computers and not classroom_dict.get('has_computers'):
                    fully_equipped = False
                
                classroom_dict['utilization_score'] = utilization_score
                classroom_dict['fully_equipped'] = fully_equipped
                
                result.append(classroom_dict)
            
            logger.info(
                f"Found {len(result)} available classrooms for "
                f"day={day_of_week}, slot={time_slot}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error finding available classrooms: {e}", exc_info=True)
            return []
    
    @track_db_query('select', 'classroom_schedules')
    def check_availability(
        self,
        classroom_id: int,
        day_of_week: int,
        time_slot: int,
        week: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Проверить доступность конкретной аудитории
        
        Args:
            classroom_id: ID аудитории
            day_of_week: День недели (1-6)
            time_slot: Номер пары (1-6)
            week: Номер недели в семестре (1-16), если None - проверка для всех недель
            
        Returns:
            Tuple (доступна ли, причина если нет)
        """
        try:
            result = db.execute_query(
                classroom_queries.CHECK_AVAILABILITY,
                (classroom_id, day_of_week, time_slot, week, week),
                fetch=True
            )
            
            if result and len(result) > 0:
                is_available = result[0]['is_available']
                
                if is_available:
                    return True, None
                else:
                    return False, "Classroom is already occupied at this time"
            
            return False, "Unable to check availability"
            
        except Exception as e:
            logger.error(
                f"Error checking availability for classroom {classroom_id}: {e}"
            )
            return False, f"Error: {str(e)}"
    
    @track_db_query('insert', 'classroom_schedules')
    def reserve_classroom(
        self,
        classroom_id: int,
        day_of_week: int,
        time_slot: int,
        week: int,
        schedule_id: Optional[int] = None,
        discipline_name: Optional[str] = None,
        teacher_name: Optional[str] = None,
        group_name: Optional[str] = None,
        lesson_type: Optional[str] = None,
        status: str = 'occupied'
    ) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Забронировать аудиторию
        
        Args:
            classroom_id: ID аудитории
            day_of_week: День недели (1-6)
            time_slot: Номер пары (1-6)
            week: Номер недели в семестре (1-16)
            schedule_id: ID записи в основном расписании
            discipline_name: Название дисциплины
            teacher_name: Имя преподавателя
            group_name: Название группы
            lesson_type: Тип занятия
            status: Статус бронирования
            
        Returns:
            Tuple (успех, ID записи, сообщение об ошибке)
        """
        try:
            # Check availability first (проверка для конкретной недели)
            is_available, reason = self.check_availability(
                classroom_id, day_of_week, time_slot, week=week
            )
            
            if not is_available:
                return False, None, reason
            
            # Insert schedule record
            params = (
                classroom_id,
                day_of_week,
                time_slot,
                week,
                schedule_id,
                discipline_name,
                teacher_name,
                group_name,
                lesson_type,
                status
            )
            
            result = db.execute_query(
                schedule_queries.INSERT_SCHEDULE,
                params,
                fetch=True
            )
            
            if result and len(result) > 0:
                schedule_record_id = result[0]['id']
                logger.info(
                    f"Reserved classroom {classroom_id} for "
                    f"day={day_of_week}, slot={time_slot}, week={week}"
                )
                return True, schedule_record_id, None
            else:
                return False, None, "Failed to create reservation"
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error reserving classroom {classroom_id}: {e}")
            
            # Handle unique constraint violation
            if 'unique_classroom_time' in error_msg:
                return False, None, "Classroom is already occupied at this time"
            
            return False, None, error_msg
    
    @track_db_query('delete', 'classroom_schedules')
    def cancel_reservation(
        self,
        classroom_id: int,
        day_of_week: int,
        time_slot: int
    ) -> tuple[bool, Optional[str]]:
        """
        Отменить бронирование аудитории
        
        Args:
            classroom_id: ID аудитории
            day_of_week: День недели
            time_slot: Номер пары
            
        Returns:
            Tuple (успех, сообщение об ошибке)
        """
        try:
            db.execute_query(
                schedule_queries.DELETE_SCHEDULE_BY_SLOT,
                (classroom_id, day_of_week, time_slot),
                fetch=False
            )
            
            logger.info(
                f"Cancelled reservation for classroom {classroom_id}, "
                f"day={day_of_week}, slot={time_slot}"
            )
            return True, None
            
        except Exception as e:
            logger.error(f"Error cancelling reservation: {e}")
            return False, str(e)
    
    @track_db_query('select', 'classroom_schedules')
    def get_classroom_schedule(
        self,
        classroom_id: int,
        days_of_week: Optional[List[int]] = None,
        week: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить расписание аудитории
        
        Args:
            classroom_id: ID аудитории
            days_of_week: Список дней недели (опционально)
            week: Номер недели в семестре (1-16), если None - все недели
            
        Returns:
            Список занятий
        """
        try:
            params = (classroom_id, days_of_week, days_of_week, week, week)
            
            result = db.execute_query(
                schedule_queries.SELECT_CLASSROOM_SCHEDULE,
                params,
                fetch=True
            )
            
            return [dict(r) for r in result] if result else []
            
        except Exception as e:
            logger.error(
                f"Error getting schedule for classroom {classroom_id}: {e}"
            )
            return []
    
    def bulk_reserve(
        self,
        reservations: List[Dict[str, Any]],
        validate_only: bool = False
    ) -> Dict[str, Any]:
        """
        Массовое бронирование аудиторий
        
        Args:
            reservations: Список бронирований
            validate_only: Только валидация без сохранения
            
        Returns:
            Результаты бронирования
        """
        results = []
        successful = 0
        failed = 0
        
        for reservation in reservations:
            classroom_id = reservation.get('classroom_id')
            day_of_week = reservation.get('day_of_week')
            time_slot = reservation.get('time_slot')
            
            if validate_only:
                # Only check availability
                is_available, reason = self.check_availability(
                    classroom_id, day_of_week, time_slot
                )
                
                results.append({
                    'classroom_id': classroom_id,
                    'success': is_available,
                    'error_message': reason
                })
                
                if is_available:
                    successful += 1
                else:
                    failed += 1
            else:
                # Actually reserve
                success, schedule_id, error = self.reserve_classroom(
                    classroom_id=classroom_id,
                    day_of_week=day_of_week,
                    time_slot=time_slot,
                    schedule_id=reservation.get('schedule_id'),
                    discipline_name=reservation.get('discipline_name'),
                    teacher_name=reservation.get('teacher_name'),
                    group_name=reservation.get('group_name'),
                    lesson_type=reservation.get('lesson_type')
                )
                
                results.append({
                    'classroom_id': classroom_id,
                    'success': success,
                    'schedule_id': schedule_id,
                    'error_message': error
                })
                
                if success:
                    successful += 1
                else:
                    failed += 1
        
        return {
            'successful_count': successful,
            'failed_count': failed,
            'results': results
        }

