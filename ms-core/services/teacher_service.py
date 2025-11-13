"""
Teacher Service - бизнес-логика для преподавателей
"""
import logging
from typing import List, Dict, Any, Optional

from db.connection import get_pool
from db.queries import teachers as teacher_queries
from utils.cache import get_cache
from utils.validators import (
    validate_email,
    validate_phone,
    validate_employment_type,
    ValidationError
)
from utils.metrics import teachers_created, teachers_updated

logger = logging.getLogger(__name__)


class TeacherService:
    """Сервис для управления преподавателями"""
    
    def __init__(self):
        self.db_pool = get_pool()
        self.cache = get_cache()
    
    def create_teacher(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать преподавателя
        
        Args:
            teacher_data: Данные преподавателя
        
        Returns:
            Dict с созданным преподавателем
        """
        # Валидация
        validate_email(teacher_data.get('email', ''))
        validate_phone(teacher_data.get('phone', ''))
        validate_employment_type(teacher_data['employment_type'])
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(teacher_queries.CREATE_TEACHER, teacher_data)
                result = cur.fetchone()
                conn.commit()
                
                teacher = {
                    'id': result[0],
                    'full_name': result[1],
                    'email': result[2],
                    'employment_type': result[3],
                    'priority': result[4],  # Вычислен автоматически!
                    'created_at': result[5].isoformat() if result[5] else None
                }
                
                # Инвалидировать кэш списков
                self.cache.delete_pattern("teachers:list:*")
                
                # Метрики
                teachers_created.inc()
                
                logger.info(f"Created teacher: {teacher['id']} - {teacher['full_name']}")
                
                return teacher
                
        finally:
            self.db_pool.return_connection(conn)
    
    def get_teacher(
        self,
        teacher_id: Optional[int] = None,
        email: Optional[str] = None,
        user_id: Optional[int] = None,
        include_preferences: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Получить преподавателя
        
        Args:
            teacher_id: ID преподавателя
            email: Email преподавателя
            user_id: ID пользователя
            include_preferences: Включить статистику предпочтений
        
        Returns:
            Dict с преподавателем или None
        """
        # Определить тип поиска
        if teacher_id:
            cache_key = f"teacher:{teacher_id}"
            query = teacher_queries.GET_TEACHER_BY_ID
            params = {'teacher_id': teacher_id}
        elif email:
            cache_key = f"teacher:email:{email}"
            query = teacher_queries.GET_TEACHER_BY_EMAIL
            params = {'email': email}
        elif user_id:
            cache_key = f"teacher:user:{user_id}"
            query = teacher_queries.GET_TEACHER_BY_USER_ID
            params = {'user_id': user_id}
        else:
            raise ValidationError("Must provide teacher_id, email, or user_id")
        
        # Проверить кэш
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Получить из БД
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                
                if not row:
                    return None
                
                # Первичные поля
                if include_preferences and len(row) > 17:
                    # С предпочтениями
                    teacher = {
                        'id': row[0],
                        'full_name': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'middle_name': row[4],
                        'email': row[5],
                        'phone': row[6],
                        'employment_type': row[7],
                        'priority': row[8],
                        'position': row[9],
                        'academic_degree': row[10],
                        'department': row[11],
                        'user_id': row[12],
                        'is_active': row[13],
                        'hire_date': row[14].isoformat() if row[14] else None,
                        'termination_date': row[15].isoformat() if row[15] else None,
                        'created_at': row[16].isoformat() if row[16] else None,
                        'updated_at': row[17].isoformat() if row[17] else None,
                        'preferences_info': {
                            'preferred_slots': row[18] or 0,
                            'total_preferences': row[19] or 0,
                            'preferences_coverage': float(row[20] or 0)
                        }
                    }
                else:
                    teacher = {
                        'id': row[0],
                        'full_name': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'middle_name': row[4],
                        'email': row[5],
                        'phone': row[6],
                        'employment_type': row[7],
                        'priority': row[8],
                        'position': row[9],
                        'academic_degree': row[10],
                        'department': row[11],
                        'user_id': row[12],
                        'is_active': row[13],
                        'hire_date': row[14].isoformat() if row[14] else None,
                        'termination_date': row[15].isoformat() if row[15] else None,
                        'created_at': row[16].isoformat() if row[16] else None,
                        'updated_at': row[17].isoformat() if row[17] else None
                    }
                
                # Сохранить в кэш
                self.cache.set(cache_key, teacher, ttl=1800)  # 30 min
                
                return teacher
                
        finally:
            self.db_pool.return_connection(conn)
    
    def list_teachers(
        self,
        page: int = 1,
        page_size: int = 50,
        employment_types: Optional[List[str]] = None,
        priorities: Optional[List[int]] = None,
        department: Optional[str] = None,
        only_active: bool = False,
        sort_by: str = 'created_at',
        sort_order: str = 'DESC'
    ) -> Dict[str, Any]:
        """
        Список преподавателей с фильтрацией
        
        Returns:
            Dict со списком преподавателей и метаданными
        """
        # Построить фильтры
        filters = teacher_queries.build_filters(
            employment_types=employment_types,
            priorities=priorities,
            department=department,
            only_active=only_active
        )
        
        order_by = teacher_queries.build_order_by(sort_by, sort_order)
        
        # Пагинация
        offset = (page - 1) * page_size
        
        # Кэш ключ
        cache_key = f"teachers:list:{filters}:{order_by}:{page}:{page_size}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Получить список
                list_query = teacher_queries.LIST_TEACHERS.format(
                    filters=filters,
                    order_by=order_by
                )
                cur.execute(list_query, {'limit': page_size, 'offset': offset})
                rows = cur.fetchall()
                
                teachers = []
                for row in rows:
                    teacher = {
                        'id': row[0],
                        'full_name': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'email': row[4],
                        'phone': row[5],
                        'employment_type': row[6],
                        'priority': row[7],
                        'position': row[8],
                        'academic_degree': row[9],
                        'department': row[10],
                        'user_id': row[11],
                        'is_active': row[12],
                        'created_at': row[13].isoformat() if row[13] else None,
                        'preferred_slots': row[14] or 0
                    }
                    teachers.append(teacher)
                
                # Получить общее количество
                count_query = teacher_queries.COUNT_TEACHERS.format(filters=filters)
                cur.execute(count_query)
                total_count = cur.fetchone()[0]
                
                result = {
                    'teachers': teachers,
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
                
                # Кэш
                self.cache.set(cache_key, result, ttl=600)  # 10 min
                
                return result
                
        finally:
            self.db_pool.return_connection(conn)
    
    def update_teacher(
        self,
        teacher_id: int,
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обновить преподавателя"""
        # Валидация
        if 'email' in update_data:
            validate_email(update_data['email'])
        if 'employment_type' in update_data:
            validate_employment_type(update_data['employment_type'])
        
        update_data['teacher_id'] = teacher_id
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(teacher_queries.UPDATE_TEACHER, update_data)
                result = cur.fetchone()
                conn.commit()
                
                # Инвалидировать кэш
                self.cache.delete(f"teacher:{teacher_id}")
                self.cache.delete_pattern("teachers:list:*")
                
                # Метрики
                teachers_updated.inc()
                
                return {
                    'id': result[0],
                    'full_name': result[1],
                    'email': result[2],
                    'employment_type': result[3],
                    'priority': result[4],
                    'updated_at': result[5].isoformat() if result[5] else None
                }
                
        finally:
            self.db_pool.return_connection(conn)
    
    def link_teacher_to_user(self, teacher_id: int, user_id: int) -> bool:
        """Связать преподавателя с пользователем из ms-auth"""
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    teacher_queries.LINK_TEACHER_TO_USER,
                    {'teacher_id': teacher_id, 'user_id': user_id}
                )
                conn.commit()
                
                # Инвалидировать кэш
                self.cache.delete(f"teacher:{teacher_id}")
                self.cache.delete(f"teacher:user:{user_id}")
                
                logger.info(f"Linked teacher {teacher_id} to user {user_id}")
                
                return True
                
        finally:
            self.db_pool.return_connection(conn)

