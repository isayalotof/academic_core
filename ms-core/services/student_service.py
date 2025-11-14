"""
Student Service - бизнес-логика для студентов
"""
import logging
from typing import Dict, Any, Optional

from db.connection import get_pool
from db.queries import students as student_queries
from utils.cache import get_cache
from utils.validators import validate_email, validate_student_status, ValidationError

logger = logging.getLogger(__name__)


class StudentService:
    """Сервис для управления студентами"""
    
    def __init__(self):
        self.db_pool = get_pool()
        self.cache = get_cache()
    
    def create_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать студента"""
        # Валидация
        if 'email' in student_data:
            validate_email(student_data['email'])
        
        # Убеждаемся, что статус установлен (по умолчанию 'active')
        if 'status' not in student_data:
            student_data['status'] = 'active'
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Создать студента
                logger.info(f"Creating student: {student_data.get('full_name')} for group_id={student_data.get('group_id')} with status={student_data.get('status', 'active')}")
                cur.execute(student_queries.CREATE_STUDENT, student_data)
                result = cur.fetchone()
                
                student = {
                    'id': result[0],
                    'full_name': result[1],
                    'student_number': result[2],
                    'group_id': result[3],
                    'status': result[4],  # Теперь статус возвращается из БД
                    'created_at': result[5].isoformat() if result[5] else None
                }
                
                logger.info(f"Student created: id={student['id']}, status={student['status']}, group_id={student['group_id']}")
                
                # Явно обновить размер группы (на случай, если триггер не сработал)
                # Триггер должен автоматически обновить group.size при INSERT,
                # но явно пересчитываем для гарантии
                from db.queries import groups as group_queries
                try:
                    logger.info(f"Recalculating group size for group_id={result[3]}")
                    cur.execute(
                        group_queries.RECALCULATE_GROUP_SIZE,
                        {'group_id': result[3]}
                    )
                    size_result = cur.fetchone()
                    if size_result:
                        new_size = size_result[1]
                        logger.info(f"✅ Updated group {result[3]} size to {new_size} (trigger should also update it)")
                    else:
                        logger.warning(f"⚠️ Group size update returned no result for group_id={result[3]}")
                except Exception as e:
                    logger.error(f"❌ Failed to recalculate group size: {e}", exc_info=True)
                    # Не прерываем выполнение, размер обновится триггером
                
                # Коммитим всё вместе
                conn.commit()
                logger.info(f"Transaction committed for student {student['id']}")
                
                # Инвалидировать кэш после коммита
                self.cache.delete_pattern("students:*")
                self.cache.delete(f"group:{result[3]}")
                logger.info(f"Cache invalidated for group {result[3]}")
                
                logger.info(f"✅ Created student: {student['id']} - {student['full_name']} (group_id={result[3]}, status={student['status']})")
                
                return student
                
        finally:
            self.db_pool.return_connection(conn)
    
    def link_student_to_user(self, student_id: int, user_id: int) -> bool:
        """Связать студента с пользователем из ms-auth"""
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    student_queries.LINK_STUDENT_TO_USER,
                    {'student_id': student_id, 'user_id': user_id}
                )
                conn.commit()
                
                self.cache.delete(f"student:{student_id}")
                self.cache.delete(f"student:user:{user_id}")
                
                logger.info(f"Linked student {student_id} to user {user_id}")
                
                return True
                
        finally:
            self.db_pool.return_connection(conn)
    
    def get_student(
        self,
        student_id: Optional[int] = None,
        student_number: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Получить студента"""
        if student_id:
            cache_key = f"student:{student_id}"
            query = student_queries.GET_STUDENT_BY_ID
            params = {'student_id': student_id}
        elif student_number:
            cache_key = f"student:number:{student_number}"
            query = student_queries.GET_STUDENT_BY_NUMBER
            params = {'student_number': student_number}
        elif user_id:
            cache_key = f"student:user:{user_id}"
            query = student_queries.GET_STUDENT_BY_USER_ID
            params = {'user_id': user_id}
        else:
            raise ValidationError("Must provide student_id, student_number, or user_id")
        
        # Кэш
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                
                if not row:
                    return None
                
                if student_id:
                    student = {
                        'id': row[0],
                        'full_name': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'middle_name': row[4],
                        'student_number': row[5],
                        'group_id': row[6],
                        'group_name': row[7],
                        'email': row[8],
                        'phone': row[9],
                        'user_id': row[10],
                        'status': row[11],
                        'enrollment_date': row[12].isoformat() if row[12] else None,
                        'created_at': row[13].isoformat() if row[13] else None,
                        'updated_at': row[14].isoformat() if row[14] else None
                    }
                else:
                    student = {
                        'id': row[0],
                        'full_name': row[1],
                        'student_number': row[2],
                        'group_id': row[3],
                        'group_name': row[4],
                        'email': row[5],
                        'phone': row[6] if len(row) > 6 else None,
                        'user_id': row[7] if len(row) > 7 else None,
                        'status': row[8] if len(row) > 8 else 'active',
                        'created_at': row[9].isoformat() if len(row) > 9 and row[9] else None
                    }
                
                self.cache.set(cache_key, student, ttl=1800)
                
                return student
                
        finally:
            self.db_pool.return_connection(conn)
    
    def list_students(
        self,
        page: int = 1,
        page_size: int = 50,
        group_id: Optional[int] = None,
        status: Optional[str] = None,
        sort_by: str = 'created_at',
        sort_order: str = 'DESC'
    ) -> Dict[str, Any]:
        """
        Список студентов с фильтрацией
        
        Returns:
            Dict со списком студентов и метаданными
        """
        # Построить фильтры
        filters = student_queries.build_filters(
            group_id=group_id,
            status=status
        )
        
        order_by = student_queries.build_order_by(sort_by, sort_order)
        
        # Пагинация
        offset = (page - 1) * page_size
        
        # Кэш ключ
        cache_key = f"students:list:{filters}:{order_by}:{page}:{page_size}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Получить список
                list_query = student_queries.LIST_STUDENTS.format(
                    filters=filters,
                    order_by=order_by
                )
                cur.execute(list_query, {'limit': page_size, 'offset': offset})
                rows = cur.fetchall()
                
                students = []
                for row in rows:
                    student = {
                        'id': row[0],
                        'full_name': row[1],
                        'student_number': row[2],
                        'group_id': row[3],
                        'group_name': row[4],
                        'email': row[5],
                        'status': row[6],
                        'created_at': row[7].isoformat() if row[7] else None
                    }
                    students.append(student)
                
                # Получить общее количество
                count_query = student_queries.COUNT_STUDENTS.format(filters=filters)
                cur.execute(count_query)
                total_count = cur.fetchone()[0]
                
                result = {
                    'students': students,
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
    
    def get_group_students(
        self,
        group_id: int,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получить список студентов группы
        
        Returns:
            Dict со списком студентов группы
        """
        cache_key = f"group:{group_id}:students:{status or 'all'}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    student_queries.GET_GROUP_STUDENTS,
                    {'group_id': group_id, 'status': status}
                )
                rows = cur.fetchall()
                
                students = []
                for row in rows:
                    student = {
                        'id': row[0],
                        'full_name': row[1],
                        'student_number': row[2],
                        'email': row[3],
                        'phone': row[4],
                        'status': row[5],
                        'enrollment_date': row[6].isoformat() if row[6] else None,
                        'created_at': row[7].isoformat() if row[7] else None
                    }
                    students.append(student)
                
                result = {
                    'group_id': group_id,
                    'students': students,
                    'total_count': len(students)
                }
                
                # Кэш
                self.cache.set(cache_key, result, ttl=600)  # 10 min
                
                return result
                
        finally:
            self.db_pool.return_connection(conn)

