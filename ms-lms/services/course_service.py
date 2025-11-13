"""
Course service for ms-lms
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from db.connection import get_pool
from proto.generated import lms_pb2

logger = logging.getLogger(__name__)


class CourseService:
    """Service for course management"""
    
    def create_course(self, title: str, description: str, code: str, 
                     teacher_id: int, status: str = 'draft'):
        """Create a new course"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO courses (title, description, code, teacher_id, status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, title, description, code, teacher_id, status, 
                              enrolled_count, created_at, updated_at
                """, (title, description, code, teacher_id, status))
                
                row = cur.fetchone()
                conn.commit()
                
                return lms_pb2.Course(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    code=row[3] or '',
                    teacher_id=row[4] or 0,
                    status=row[5],
                    enrolled_count=row[6] or 0,
                    created_at=row[7].isoformat() if row[7] else '',
                    updated_at=row[8].isoformat() if row[8] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def get_course(self, course_id: int) -> Optional[lms_pb2.Course]:
        """Get course by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, code, teacher_id, teacher_name,
                           status, enrolled_count, created_at, updated_at
                    FROM courses
                    WHERE id = %s
                """, (course_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return lms_pb2.Course(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    code=row[3] or '',
                    teacher_id=row[4] or 0,
                    teacher_name=row[5] or '',
                    status=row[6],
                    enrolled_count=row[7] or 0,
                    created_at=row[8].isoformat() if row[8] else '',
                    updated_at=row[9].isoformat() if row[9] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_courses(self, page: int = 1, page_size: int = 50,
                    teacher_id: Optional[int] = None,
                    status: Optional[str] = None) -> Tuple[List[lms_pb2.Course], int]:
        """List courses with pagination"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                if teacher_id:
                    where_clauses.append("teacher_id = %s")
                    params.append(teacher_id)
                
                if status:
                    where_clauses.append("status = %s")
                    params.append(status)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                # Count total
                cur.execute(f"SELECT COUNT(*) FROM courses {where_sql}", params)
                total = cur.fetchone()[0]
                
                # Get courses
                offset = (page - 1) * page_size
                params.append(page_size)
                params.append(offset)
                
                cur.execute(f"""
                    SELECT id, title, description, code, teacher_id, teacher_name,
                           status, enrolled_count, created_at, updated_at
                    FROM courses
                    {where_sql}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, params)
                
                courses = []
                for row in cur.fetchall():
                    courses.append(lms_pb2.Course(
                        id=row[0],
                        title=row[1],
                        description=row[2] or '',
                        code=row[3] or '',
                        teacher_id=row[4] or 0,
                        teacher_name=row[5] or '',
                        status=row[6],
                        enrolled_count=row[7] or 0,
                        created_at=row[8].isoformat() if row[8] else '',
                        updated_at=row[9].isoformat() if row[9] else ''
                    ))
                
                return courses, total
        finally:
            pool.return_connection(conn)
    
    def enroll_student(self, course_id: int, student_id: int) -> bool:
        """Enroll student in course"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO course_enrollments (course_id, student_id)
                    VALUES (%s, %s)
                    ON CONFLICT (course_id, student_id) DO NOTHING
                    RETURNING id
                """, (course_id, student_id))
                
                if cur.fetchone():
                    conn.commit()
                    return True
                return False
        finally:
            pool.return_connection(conn)

