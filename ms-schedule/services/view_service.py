"""
View service for schedule
Сервис для просмотра расписания
"""

from typing import List, Dict, Optional
import logging

from db.connection import get_db_pool
from db.queries import schedules as schedule_queries
from utils.cache import cache, get_cache_key
from utils.metrics import track_view, track_db_query

logger = logging.getLogger(__name__)


class ViewService:
    """Service for viewing schedules"""
    
    def __init__(self):
        """Initialize view service"""
        self.db = get_db_pool()
    
    @track_view('group')
    @track_db_query('select')
    def get_group_schedule(
        self,
        group_id: int,
        semester: int,
        academic_year: str,
        day_of_week: Optional[int] = None,
        week_type: Optional[str] = None,
        only_active: bool = True
    ) -> List[Dict]:
        """
        Get schedule for group
        
        Args:
            group_id: Group ID
            semester: Semester number
            academic_year: Academic year
            day_of_week: Optional day filter
            week_type: Optional week type filter
            only_active: Return only active schedules
            
        Returns:
            List of lessons
        """
        # Check cache
        cache_key = get_cache_key(
            'group', group_id, semester, academic_year,
            day=day_of_week, week=week_type, active=only_active
        )
        
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Returning cached schedule for group {group_id}")
            return cached
        
        # Query database
        logger.info(f"Fetching schedule for group {group_id}")
        
        lessons = self.db.execute_query(
            schedule_queries.GET_SCHEDULE_FOR_GROUP,
            params={
                'group_id': group_id,
                'semester': semester,
                'academic_year': academic_year,
                'day_of_week': day_of_week,
                'week_type': week_type,
                'only_active': only_active
            },
            fetch_all=True
        )
        
        # Cache results
        if lessons:
            cache.set(cache_key, lessons)
        
        logger.info(f"Found {len(lessons)} lessons for group {group_id}")
        return lessons
    
    @track_view('teacher')
    @track_db_query('select')
    def get_teacher_schedule(
        self,
        teacher_id: int,
        semester: int,
        academic_year: str,
        day_of_week: Optional[int] = None,
        week_type: Optional[str] = None,
        only_active: bool = True
    ) -> List[Dict]:
        """Get schedule for teacher"""
        cache_key = get_cache_key(
            'teacher', teacher_id, semester, academic_year,
            day=day_of_week, week=week_type, active=only_active
        )
        
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"Fetching schedule for teacher {teacher_id}")
        
        lessons = self.db.execute_query(
            schedule_queries.GET_SCHEDULE_FOR_TEACHER,
            params={
                'teacher_id': teacher_id,
                'semester': semester,
                'academic_year': academic_year,
                'day_of_week': day_of_week,
                'week_type': week_type,
                'only_active': only_active
            },
            fetch_all=True
        )
        
        if lessons:
            cache.set(cache_key, lessons)
        
        logger.info(f"Found {len(lessons)} lessons for teacher {teacher_id}")
        return lessons
    
    @track_view('classroom')
    @track_db_query('select')
    def get_classroom_schedule(
        self,
        classroom_id: int,
        semester: int,
        academic_year: str,
        day_of_week: Optional[int] = None,
        week_type: Optional[str] = None,
        only_active: bool = True
    ) -> List[Dict]:
        """Get schedule for classroom"""
        cache_key = get_cache_key(
            'classroom', classroom_id, semester, academic_year,
            day=day_of_week, week=week_type, active=only_active
        )
        
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        logger.info(f"Fetching schedule for classroom {classroom_id}")
        
        lessons = self.db.execute_query(
            schedule_queries.GET_SCHEDULE_FOR_CLASSROOM,
            params={
                'classroom_id': classroom_id,
                'semester': semester,
                'academic_year': academic_year,
                'day_of_week': day_of_week,
                'week_type': week_type,
                'only_active': only_active
            },
            fetch_all=True
        )
        
        if lessons:
            cache.set(cache_key, lessons)
        
        logger.info(f"Found {len(lessons)} lessons for classroom {classroom_id}")
        return lessons
    
    @track_db_query('select')
    def get_day_schedule(
        self,
        day_of_week: int,
        semester: int,
        academic_year: str,
        week_type: Optional[str] = None,
        group_ids: Optional[List[int]] = None,
        teacher_ids: Optional[List[int]] = None,
        classroom_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """Get all schedules for specific day"""
        logger.info(f"Fetching schedule for day {day_of_week}")
        
        lessons = self.db.execute_query(
            schedule_queries.GET_SCHEDULE_FOR_DAY,
            params={
                'day_of_week': day_of_week,
                'semester': semester,
                'academic_year': academic_year,
                'week_type': week_type,
                'group_ids': group_ids,
                'teacher_ids': teacher_ids,
                'classroom_ids': classroom_ids
            },
            fetch_all=True
        )
        
        logger.info(f"Found {len(lessons)} lessons for day {day_of_week}")
        return lessons
    
    @track_db_query('select')
    def get_lesson_by_id(self, lesson_id: int) -> Optional[Dict]:
        """Get single lesson by ID"""
        logger.debug(f"Fetching lesson {lesson_id}")
        
        lesson = self.db.execute_query(
            schedule_queries.GET_LESSON_BY_ID,
            params={'id': lesson_id},
            fetch_one=True
        )
        
        return lesson
    
    @track_db_query('select')
    def search_schedule(
        self,
        query: str,
        semester: int,
        academic_year: str,
        limit: int = 50
    ) -> List[Dict]:
        """Full-text search in schedule"""
        logger.info(f"Searching schedule: '{query}'")
        
        results = self.db.execute_query(
            schedule_queries.SEARCH_SCHEDULE,
            params={
                'query': query,
                'semester': semester,
                'academic_year': academic_year,
                'limit': limit
            },
            fetch_all=True
        )
        
        logger.info(f"Found {len(results)} results for query '{query}'")
        return results


# Global instance
view_service = ViewService()

