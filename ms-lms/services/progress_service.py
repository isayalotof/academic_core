"""
Progress service for ms-lms
"""
import logging
from typing import Optional
from db.connection import get_pool
from proto.generated import lms_pb2

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for student progress tracking"""
    
    def get_progress(self, student_id: int, course_id: int) -> Optional[lms_pb2.Progress]:
        """Get student progress for a course"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Get overall progress
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT m.id) as total_modules,
                        COUNT(DISTINCT CASE WHEN sp.completed THEN sp.module_id END) as completed_modules
                    FROM modules m
                    LEFT JOIN student_progress sp ON sp.module_id = m.id AND sp.student_id = %s
                    WHERE m.course_id = %s
                """, (student_id, course_id))
                
                row = cur.fetchone()
                total = row[0] or 0
                completed = row[1] or 0
                percentage = (completed / total * 100) if total > 0 else 0.0
                
                return lms_pb2.ProgressResponse(
                    overall_progress=float(percentage),
                    message="Progress retrieved successfully"
                )
        finally:
            pool.return_connection(conn)
    
    def update_progress(self, student_id: int, course_id: int, 
                       module_id: int, completed: bool):
        """Update student progress"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO student_progress (student_id, course_id, module_id, completed, completed_at)
                    VALUES (%s, %s, %s, %s, CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE NULL END)
                    ON CONFLICT (student_id, course_id, module_id)
                    DO UPDATE SET completed = %s, 
                                  completed_at = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE completed_at,
                                  updated_at = CURRENT_TIMESTAMP
                """, (student_id, course_id, module_id, completed, completed, completed, completed))
                
                conn.commit()
                return True
        finally:
            pool.return_connection(conn)

