"""
Context Builder для генетического алгоритма
Получение данных из ms-core и ms-audit
"""
import logging
from typing import Dict, List, Any, Optional
from rpc_clients.core_client import get_core_client
from db.connection import db
from db.queries import course_loads as load_queries

logger = logging.getLogger(__name__)


class ScheduleContextBuilder:
    """Построение контекста для генерации расписания"""
    
    def __init__(self):
        self.core_client = get_core_client()
    
    async def build_context(self,
                          semester: int,
                          academic_year: str,
                          group_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Построить контекст для генерации
        
        Returns:
            {
                'course_loads': List[Dict],  # из БД (распарсенные из Excel)
                'teacher_preferences': Dict,  # из ms-core
                'classrooms': List[Dict],     # из ms-audit
                'teachers': Dict,             # из ms-core
                'groups': Dict                # из ms-core
            }
        """
        logger.info(f"Building context for semester {semester}, year {academic_year}")
        
        context = {
            'course_loads': [],
            'teacher_preferences': {},
            'classrooms': [],
            'teachers': {},
            'groups': {}
        }
        
        # 1. Получить course_loads из БД (уже распарсенные из Excel)
        course_loads = db.execute_query(
            load_queries.SELECT_COURSE_LOADS_BY_SEMESTER,
            {'semester': semester},
            fetch=True
        )
        
        logger.info(f"Loaded {len(course_loads)} course loads from DB")
        
        # Преобразовать в нужный формат
        for load in course_loads:
            context['course_loads'].append({
                'id': load.get('id'),
                'discipline_name': load.get('discipline_name'),
                'discipline_code': load.get('discipline_code'),
                'teacher_id': load.get('teacher_id', 0),
                'teacher_name': load.get('teacher_name', ''),
                'teacher_priority': load.get('teacher_priority', 4),
                'group_id': load.get('group_id', 0),
                'group_name': load.get('group_name', ''),
                'group_size': load.get('group_size'),
                'lesson_type': load.get('lesson_type', 'Практика'),
                'hours_per_semester': load.get('hours_per_semester', 0),
                'lessons_per_week': load.get('lessons_per_week', 1),
                'semester': load.get('semester', semester),
                'academic_year': load.get('academic_year', academic_year)
            })
        
        # 2. Получить предпочтения преподавателей из ms-core ⭐
        teacher_prefs = self.core_client.get_all_preferences(
            semester=semester,
            academic_year=academic_year
        )
        
        logger.info(f"Loaded preferences for {len(teacher_prefs)} teachers")
        
        for pref_set in teacher_prefs:
            teacher_id = pref_set['teacher_id']
            context['teacher_preferences'][teacher_id] = {
                'priority': pref_set.get('teacher_priority', 4),
                'name': pref_set.get('teacher_name', f'Teacher {teacher_id}'),
                'preferences': pref_set.get('preferences', [])
            }
        
        # 3. Получить аудитории (пока из БД, потом можно через ms-audit)
        # TODO: получить через ms-audit gRPC
        classrooms = db.execute_query(
            "SELECT id, name, capacity, classroom_type FROM classrooms WHERE is_active = true",
            {},
            fetch=True
        )
        
        logger.info(f"Loaded {len(classrooms)} classrooms")
        
        for classroom in classrooms:
            context['classrooms'].append({
                'id': classroom.get('id'),
                'name': classroom.get('name'),
                'capacity': classroom.get('capacity', 0),
                'classroom_type': classroom.get('classroom_type', '')
            })
        
        # 4. Получить информацию о преподавателях
        teacher_ids = set(load.get('teacher_id', 0) for load in course_loads if load.get('teacher_id', 0) > 0)
        
        for teacher_id in teacher_ids:
            if teacher_id in context['teacher_preferences']:
                context['teachers'][teacher_id] = context['teacher_preferences'][teacher_id]
            else:
                context['teachers'][teacher_id] = {
                    'priority': 4,
                    'name': f'Teacher {teacher_id}',
                    'preferences': []
                }
        
        # 5. Получить информацию о группах
        group_ids_from_loads = set(load.get('group_id', 0) for load in course_loads if load.get('group_id', 0) > 0)
        
        for group_id in group_ids_from_loads:
            # TODO: получить через ms-core gRPC
            context['groups'][group_id] = {
                'id': group_id,
                'name': f'Group {group_id}',
                'size': None
            }
        
        logger.info(
            f"Context built: {len(context['course_loads'])} loads, "
            f"{len(context['teacher_preferences'])} teachers with preferences, "
            f"{len(context['classrooms'])} classrooms"
        )
        
        return context

