"""
Group Service - бизнес-логика для групп
"""
import logging
from typing import Dict, Any, Optional

from db.connection import get_pool
from db.queries import groups as group_queries
from utils.cache import get_cache
from utils.validators import validate_group_level, ValidationError

logger = logging.getLogger(__name__)


class GroupService:
    """Сервис для управления группами"""
    
    def __init__(self):
        self.db_pool = get_pool()
        self.cache = get_cache()
    
    def create_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать группу"""
        # Валидация
        if 'level' in group_data:
            validate_group_level(group_data['level'])
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(group_queries.CREATE_GROUP, group_data)
                result = cur.fetchone()
                conn.commit()
                
                group = {
                    'id': result[0],
                    'name': result[1],
                    'short_name': result[2],
                    'year': result[3],
                    'level': result[4],
                    'created_at': result[5].isoformat() if result[5] else None
                }
                
                # Инвалидировать кэш
                self.cache.delete_pattern("groups:*")
                
                logger.info(f"Created group: {group['id']} - {group['name']}")
                
                return group
                
        finally:
            self.db_pool.return_connection(conn)
    
    def get_group(
        self,
        group_id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Получить группу"""
        if group_id:
            cache_key = f"group:{group_id}"
            query = group_queries.GET_GROUP_BY_ID
            params = {'group_id': group_id}
        elif name:
            cache_key = f"group:name:{name}"
            query = group_queries.GET_GROUP_BY_NAME
            params = {'name': name}
        else:
            raise ValidationError("Must provide group_id or name")
        
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
                
                group = {
                    'id': row[0],
                    'name': row[1],
                    'short_name': row[2],
                    'year': row[3],
                    'semester': row[4],
                    'size': row[5],
                    'program_code': row[6],
                    'program_name': row[7],
                    'specialization': row[8],
                    'level': row[9],
                    'curator_teacher_id': row[10],
                    'curator_name': row[11],
                    'is_active': row[12],
                    'enrollment_date': row[13].isoformat() if row[13] else None,
                    'graduation_date': row[14].isoformat() if row[14] else None,
                    'created_at': row[15].isoformat() if row[15] else None,
                    'updated_at': row[16].isoformat() if row[16] else None
                }
                
                self.cache.set(cache_key, group, ttl=1800)
                
                return group
                
        finally:
            self.db_pool.return_connection(conn)
    
    def list_groups(
        self,
        page: int = 1,
        page_size: int = 50,
        year: Optional[int] = None,
        level: Optional[str] = None,
        only_active: bool = False,
        sort_by: str = 'created_at',
        sort_order: str = 'DESC'
    ) -> Dict[str, Any]:
        """
        Список групп с фильтрацией
        
        Returns:
            Dict со списком групп и метаданными
        """
        # Построить фильтры
        filters = group_queries.build_filters(
            year=year,
            level=level,
            only_active=only_active
        )
        
        order_by = group_queries.build_order_by(sort_by, sort_order)
        
        # Пагинация
        offset = (page - 1) * page_size
        
        # Кэш ключ
        cache_key = f"groups:list:{filters}:{order_by}:{page}:{page_size}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        conn = self.db_pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Получить список
                list_query = group_queries.LIST_GROUPS.format(
                    filters=filters,
                    order_by=order_by
                )
                cur.execute(list_query, {'limit': page_size, 'offset': offset})
                rows = cur.fetchall()
                
                groups = []
                for row in rows:
                    group = {
                        'id': row[0],
                        'name': row[1],
                        'short_name': row[2],
                        'year': row[3],
                        'semester': row[4],
                        'size': row[5],
                        'program_code': row[6],
                        'program_name': row[7],
                        'level': row[8],
                        'curator_teacher_id': row[9],
                        'curator_name': row[10],
                        'is_active': row[11],
                        'created_at': row[12].isoformat() if row[12] else None
                    }
                    groups.append(group)
                
                # Получить общее количество
                count_query = group_queries.COUNT_GROUPS.format(filters=filters)
                cur.execute(count_query)
                total_count = cur.fetchone()[0]
                
                result = {
                    'groups': groups,
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

