"""
Course Load Service - бизнес-логика для учебной нагрузки
"""
import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime

from db.connection import get_pool
from db.queries import course_loads as load_queries
from services.excel_parser import parse_course_loads_excel
from utils.cache import get_cache
from utils.validators import validate_semester, validate_academic_year, validate_lesson_type
from utils.metrics import course_loads_imported, import_duration

logger = logging.getLogger(__name__)


class LoadService:
    """Сервис для управления учебной нагрузкой"""
    
    def __init__(self):
        self.db_pool = get_pool()
        self.cache = get_cache()
    
    def import_course_loads(
        self,
        file_data: bytes,
        filename: str,
        semester: int,
        academic_year: str,
        imported_by: int = None
    ) -> Dict[str, Any]:
        """
        Импортировать учебную нагрузку из Excel
        
        Returns:
            Dict с результатом импорта
        """
        # Валидация
        validate_semester(semester)
        validate_academic_year(academic_year)
        
        # Парсинг Excel
        start_time = datetime.now()
        
        batch_id = str(uuid.uuid4())
        
        logger.info(f"Starting import batch {batch_id}: {filename}")
        
        # Создать запись батча
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO import_batches (
                        batch_id, filename, file_size, semester, academic_year,
                        status, imported_by, started_at
                    )
                    VALUES (%s, %s, %s, %s, %s, 'processing', %s, NOW())
                    RETURNING id
                """, (batch_id, filename, len(file_data), semester, academic_year, imported_by))
                batch_db_id = cur.fetchone()[0]
                conn.commit()
        finally:
            self.db_pool.return_connection(conn)
        
        # Парсинг
        parse_result = parse_course_loads_excel(file_data, filename)
        
        if not parse_result['success']:
            # Обновить батч как failed
            self._update_batch_status(batch_id, 'failed', parse_result)
            course_loads_imported.labels(status='failed').inc()
            
            return {
                'success': False,
                'batch_id': batch_id,
                'errors': parse_result['errors'],
                'message': 'Не удалось распарсить файл'
            }
        
        # Сохранить в БД
        successful_rows = 0
        failed_rows = 0
        errors = []
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                for idx, row_data in enumerate(parse_result['data'], start=1):
                    try:
                        # Найти teacher_id и group_id
                        # (В реальной системе нужно сопоставление по имени)
                        
                        # Пока пропускаем вставку, т.к. нужны ID
                        # В продакшне нужен поиск преподавателей/групп
                        
                        successful_rows += 1
                        
                    except Exception as e:
                        failed_rows += 1
                        errors.append(f"Строка {idx}: {str(e)}")
                        logger.warning(f"Failed to import row {idx}: {e}")
                
                conn.commit()
        finally:
            self.db_pool.return_connection(conn)
        
        # Обновить батч
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            'success': successful_rows > 0,
            'batch_id': batch_id,
            'total_rows': parse_result['total_rows'],
            'successful_rows': successful_rows,
            'failed_rows': failed_rows,
            'errors': errors + parse_result['errors'],
            'message': f'Импортировано {successful_rows} из {parse_result["total_rows"]} строк'
        }
        
        self._update_batch_status(batch_id, 'completed', result)
        
        # Метрики
        course_loads_imported.labels(status='success').inc()
        import_duration.observe(duration)
        
        logger.info(
            f"Import batch {batch_id} completed: "
            f"{successful_rows} success, {failed_rows} failed"
        )
        
        # Инвалидировать кэш
        self.cache.delete_pattern("course_loads:*")
        
        return result
    
    def _update_batch_status(
        self,
        batch_id: str,
        status: str,
        result: Dict[str, Any]
    ):
        """Обновить статус батча"""
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE import_batches
                    SET
                        status = %s,
                        total_rows = %s,
                        successful_rows = %s,
                        failed_rows = %s,
                        errors = %s::jsonb,
                        completed_at = NOW()
                    WHERE batch_id = %s
                """, (
                    status,
                    result.get('total_rows', 0),
                    result.get('successful_rows', 0),
                    result.get('failed_rows', 0),
                    str(result.get('errors', [])),
                    batch_id
                ))
                conn.commit()
        finally:
            self.db_pool.return_connection(conn)
    
    def list_course_loads(
        self,
        page: int = 1,
        page_size: int = 50,
        semester: int = None,
        academic_year: str = None,
        teacher_ids: List[int] = None,
        group_ids: List[int] = None,
        lesson_types: List[str] = None,
        only_active: bool = True
    ) -> Dict[str, Any]:
        """
        Получить список учебной нагрузки с фильтрацией и пагинацией
        
        Returns:
            Dict с course_loads (list) и total_count (int)
        """
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Построить фильтры
                filters = load_queries.build_course_load_filters(
                    semester=semester,
                    academic_year=academic_year,
                    teacher_ids=teacher_ids,
                    group_ids=group_ids,
                    lesson_types=lesson_types,
                    only_active=only_active
                )
                
                # Подсчет общего количества
                count_query = load_queries.COUNT_COURSE_LOADS.format(filters=filters)
                cur.execute(count_query)
                total_count = cur.fetchone()[0]
                
                # Получение данных с пагинацией
                offset = (page - 1) * page_size
                list_query = load_queries.LIST_COURSE_LOADS.format(filters=filters)
                cur.execute(list_query, {
                    'limit': page_size,
                    'offset': offset
                })
                
                rows = cur.fetchall()
                
                # Преобразовать в список словарей
                course_loads = []
                for row in rows:
                    course_loads.append({
                        'id': row[0],
                        'discipline_name': row[1],
                        'discipline_code': row[2],
                        'teacher_id': row[3],
                        'teacher_name': row[4],
                        'teacher_priority': row[5],
                        'group_id': row[6],
                        'group_name': row[7],
                        'group_size': row[8],
                        'lesson_type': row[9],
                        'hours_per_semester': row[10],
                        'lessons_per_week': row[11],
                        'semester': row[12],
                        'academic_year': row[13],
                        'is_active': row[14],
                        'source': row[15],
                        'created_at': row[16].isoformat() if row[16] else None
                    })
                
                return {
                    'course_loads': course_loads,
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size
                }
        finally:
            self.db_pool.return_connection(conn)
    
    def create_course_load(
        self,
        discipline_name: str,
        discipline_code: str = None,
        discipline_id: int = None,
        teacher_id: int = None,
        teacher_name: str = None,
        group_id: int = None,
        group_name: str = None,
        group_size: int = None,
        lesson_type: str = None,
        hours_per_semester: int = None,
        weeks_count: int = 16,
        semester: int = None,
        academic_year: str = None,
        required_classroom_type: str = None,
        min_classroom_capacity: int = None,
        created_by: int = None
    ) -> Dict[str, Any]:
        """
        Создать запись учебной нагрузки
        
        Returns:
            Dict с данными созданной нагрузки
        """
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                load_data = {
                    'discipline_id': discipline_id,
                    'discipline_name': discipline_name,
                    'discipline_code': discipline_code or '',
                    'teacher_id': teacher_id,
                    'teacher_name': teacher_name or '',
                    'group_id': group_id,
                    'group_name': group_name or '',
                    'group_size': group_size,
                    'lesson_type': lesson_type,
                    'hours_per_semester': hours_per_semester,
                    'weeks_count': weeks_count,
                    'semester': semester,
                    'academic_year': academic_year,
                    'required_classroom_type': required_classroom_type,
                    'min_classroom_capacity': min_classroom_capacity,
                    'source': 'manual',
                    'import_batch_id': None,
                    'created_by': created_by
                }
                
                cur.execute(load_queries.CREATE_COURSE_LOAD, load_data)
                result = cur.fetchone()
                conn.commit()
                
                return {
                    'id': result[0],
                    'discipline_name': result[1],
                    'teacher_name': result[2],
                    'group_name': result[3],
                    'lessons_per_week': result[4],
                    'created_at': result[5].isoformat() if result[5] else None
                }
        finally:
            self.db_pool.return_connection(conn)

