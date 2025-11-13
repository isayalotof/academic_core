"""
⭐ Preference Service - KEY FEATURE!
Бизнес-логика для работы с предпочтениями преподавателей
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from db.connection import get_pool
from db.queries import preferences as pref_queries
from utils.cache import get_cache
from utils.validators import (
    validate_day_of_week,
    validate_time_slot,
    validate_preference_strength,
    ValidationError
)
from utils.metrics import teacher_preferences_set, preferred_slots_total

logger = logging.getLogger(__name__)


class PreferenceService:
    """Сервис для управления предпочтениями преподавателей"""
    
    def __init__(self):
        self.db_pool = get_pool()
        self.cache = get_cache()
    
    def get_teacher_preferences(self, teacher_id: int) -> Dict[str, Any]:
        """
        Получить предпочтения преподавателя с статистикой
        
        Args:
            teacher_id: ID преподавателя
        
        Returns:
            Dict с предпочтениями и статистикой
        """
        # Проверить кэш
        cache_key = f"preferences:teacher:{teacher_id}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for teacher {teacher_id} preferences")
            return cached
        
        # Получить из БД
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Получить предпочтения с информацией о преподавателе
                cur.execute(
                    pref_queries.GET_PREFERENCES_WITH_TEACHER_INFO,
                    {'teacher_id': teacher_id}
                )
                
                rows = cur.fetchall()
                if not rows:
                    return {
                        'teacher_id': teacher_id,
                        'preferences': [],
                        'total_preferences': 0,
                        'preferred_count': 0,
                        'coverage_percentage': 0.0
                    }
                
                # Первая строка содержит информацию о преподавателе
                first_row = rows[0]
                teacher_name = first_row[1]  # t.full_name
                teacher_priority = first_row[2]  # t.priority
                
                # Собрать предпочтения
                preferences = []
                preferred_count = 0
                not_preferred_count = 0
                
                for row in rows:
                    if row[3] is None:  # tp.id - Нет предпочтений
                        continue
                    
                    pref = {
                        'id': row[3],  # tp.id
                        'day_of_week': row[4],  # tp.day_of_week
                        'time_slot': row[5],  # tp.time_slot
                        'is_preferred': row[6],  # tp.is_preferred
                        'preference_strength': row[7] or '',  # tp.preference_strength
                        'reason': row[8] or ''  # tp.reason
                    }
                    preferences.append(pref)
                    
                    if pref['is_preferred']:
                        preferred_count += 1
                    else:
                        not_preferred_count += 1
                
                # Вычислить coverage
                total_slots = 36  # 6 дней × 6 пар
                coverage = (len(preferences) / total_slots * 100) if preferences else 0.0
                
                result = {
                    'teacher_id': teacher_id,
                    'teacher_name': teacher_name,
                    'teacher_priority': teacher_priority,
                    'preferences': preferences,
                    'total_preferences': len(preferences),
                    'preferred_count': preferred_count,
                    'not_preferred_count': not_preferred_count,
                    'coverage_percentage': round(coverage, 2)
                }
                
                # Сохранить в кэш
                self.cache.set(cache_key, result, ttl=900)  # 15 min
                
                return result
                
        finally:
            self.db_pool.return_connection(conn)
    
    def set_teacher_preferences(
        self,
        teacher_id: int,
        preferences: List[Dict[str, Any]],
        replace_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Установить предпочтения преподавателя
        
        Args:
            teacher_id: ID преподавателя
            preferences: Список предпочтений
            replace_existing: Удалить существующие предпочтения
        
        Returns:
            Dict с результатом операции
        """
        # Валидация
        for pref in preferences:
            validate_day_of_week(pref['day_of_week'])
            validate_time_slot(pref['time_slot'])
            validate_preference_strength(pref.get('preference_strength'))
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                created_count = 0
                updated_count = 0
                deleted_count = 0
                
                # Удалить существующие если нужно
                if replace_existing:
                    cur.execute(
                        pref_queries.DELETE_PREFERENCES_BY_TEACHER,
                        {'teacher_id': teacher_id}
                    )
                    deleted_count = cur.rowcount
                
                # Вставить новые
                for pref in preferences:
                    cur.execute(
                        pref_queries.UPSERT_PREFERENCE,
                        {
                            'teacher_id': teacher_id,
                            'day_of_week': pref['day_of_week'],
                            'time_slot': pref['time_slot'],
                            'is_preferred': pref['is_preferred'],
                            'preference_strength': pref.get('preference_strength', ''),
                            'reason': pref.get('reason', '')
                        }
                    )
                    created_count += 1
                
                conn.commit()
                
                # Инвалидировать кэш
                cache_key = f"preferences:teacher:{teacher_id}"
                self.cache.delete(cache_key)
                self.cache.delete("preferences:all")
                
                # Обновить метрики
                teacher_preferences_set.labels(teacher_id=str(teacher_id)).inc()
                
                logger.info(
                    f"Set preferences for teacher {teacher_id}: "
                    f"created={created_count}, deleted={deleted_count}"
                )
                
                return {
                    'success': True,
                    'created_count': created_count,
                    'updated_count': updated_count,
                    'deleted_count': deleted_count,
                    'message': f'Successfully set {created_count} preferences'
                }
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Error setting preferences: {e}", exc_info=True)
            raise
        finally:
            self.db_pool.return_connection(conn)
    
    def get_all_preferences(
        self,
        semester: Optional[int] = None,
        academic_year: Optional[str] = None,
        teacher_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        ⭐ KEY METHOD для ms-agent!
        Получить ВСЕ предпочтения преподавателей для fitness-функции
        
        Args:
            semester: Фильтр по семестру (опционально)
            academic_year: Фильтр по учебному году (опционально)
            teacher_ids: Фильтр по преподавателям (опционально)
        
        Returns:
            Список преподавателей с их предпочтениями
        """
        # Проверить кэш
        cache_key = f"preferences:all:{semester}:{academic_year}"
        cached = self.cache.get(cache_key)
        if cached and not teacher_ids:
            logger.debug("Cache hit for all preferences")
            return cached
        
        # Построить фильтры
        filters = pref_queries.build_preferences_filters(
            teacher_ids=teacher_ids,
            semester=semester,
            academic_year=academic_year
        )
        
        # Получить из БД
        query = pref_queries.GET_ALL_PREFERENCES.format(filters=filters)
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                
                # Группировать по преподавателям
                teachers_dict = {}
                
                for row in rows:
                    teacher_id = row[0]
                    
                    if teacher_id not in teachers_dict:
                        teachers_dict[teacher_id] = {
                            'teacher_id': teacher_id,
                            'teacher_name': row[1],
                            'teacher_priority': row[2],
                            'employment_type': row[3],
                            'preferences': []
                        }
                    
                    # Добавить предпочтение если есть
                    if row[4] is not None:  # preference_id
                        pref = {
                            'id': row[4],
                            'day_of_week': row[5],
                            'time_slot': row[6],
                            'is_preferred': row[7],
                            'preference_strength': row[8] or ''
                        }
                        teachers_dict[teacher_id]['preferences'].append(pref)
                
                result = list(teachers_dict.values())
                
                # Сохранить в кэш
                if not teacher_ids:
                    self.cache.set(cache_key, result, ttl=900)  # 15 min
                
                logger.info(f"Retrieved preferences for {len(result)} teachers")
                
                return result
                
        finally:
            self.db_pool.return_connection(conn)
    
    def clear_preferences(self, teacher_id: int) -> Dict[str, Any]:
        """
        Удалить все предпочтения преподавателя
        
        Args:
            teacher_id: ID преподавателя
        
        Returns:
            Dict с результатом
        """
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    pref_queries.DELETE_PREFERENCES_BY_TEACHER,
                    {'teacher_id': teacher_id}
                )
                deleted_count = cur.rowcount
                conn.commit()
                
                # Инвалидировать кэш
                self.cache.delete(f"preferences:teacher:{teacher_id}")
                self.cache.delete("preferences:all")
                
                logger.info(f"Cleared {deleted_count} preferences for teacher {teacher_id}")
                
                return {
                    'success': True,
                    'deleted_count': deleted_count
                }
                
        finally:
            self.db_pool.return_connection(conn)

