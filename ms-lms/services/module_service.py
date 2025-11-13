"""
Module service for ms-lms
"""
import logging
from typing import List, Optional
from db.connection import get_pool
from proto.generated import lms_pb2

logger = logging.getLogger(__name__)


class ModuleService:
    """Service for module management"""
    
    def create_module(self, course_id: int, title: str, description: str, order: int):
        """Create a new module"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO modules (course_id, title, description, order_index)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, course_id, title, description, order_index, created_at, updated_at
                """, (course_id, title, description, order))
                
                row = cur.fetchone()
                conn.commit()
                
                return lms_pb2.Module(
                    id=row[0],
                    course_id=row[1],
                    title=row[2],
                    description=row[3] or '',
                    order=row[4],
                    created_at=row[5].isoformat() if row[5] else '',
                    updated_at=row[6].isoformat() if row[6] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_modules(self, course_id: int) -> List[lms_pb2.Module]:
        """List modules for a course"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, course_id, title, description, order_index, created_at, updated_at
                    FROM modules
                    WHERE course_id = %s
                    ORDER BY order_index ASC
                """, (course_id,))
                
                modules = []
                for row in cur.fetchall():
                    modules.append(lms_pb2.Module(
                        id=row[0],
                        course_id=row[1],
                        title=row[2],
                        description=row[3] or '',
                        order=row[4],
                        created_at=row[5].isoformat() if row[5] else '',
                        updated_at=row[6].isoformat() if row[6] else ''
                    ))
                
                return modules
        finally:
            pool.return_connection(conn)
    
    def get_module(self, module_id: int):
        """Get module by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, course_id, title, description, order_index, created_at, updated_at
                    FROM modules
                    WHERE id = %s
                """, (module_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return lms_pb2.Module(
                    id=row[0], course_id=row[1], title=row[2],
                    description=row[3] or '', order=row[4],
                    created_at=row[5].isoformat() if row[5] else '',
                    updated_at=row[6].isoformat() if row[6] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def update_module(self, module_id: int, title: Optional[str] = None,
                     description: Optional[str] = None, order: Optional[int] = None):
        """Update module"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                updates = []
                params = []
                
                if title:
                    updates.append("title = %s")
                    params.append(title)
                if description:
                    updates.append("description = %s")
                    params.append(description)
                if order is not None:
                    updates.append("order_index = %s")
                    params.append(order)
                
                if not updates:
                    return self.get_module(module_id)
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(module_id)
                
                cur.execute(f"""
                    UPDATE modules
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING id, course_id, title, description, order_index, created_at, updated_at
                """, params)
                
                row = cur.fetchone()
                conn.commit()
                
                if not row:
                    return None
                
                return lms_pb2.Module(
                    id=row[0], course_id=row[1], title=row[2],
                    description=row[3] or '', order=row[4],
                    created_at=row[5].isoformat() if row[5] else '',
                    updated_at=row[6].isoformat() if row[6] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def delete_module(self, module_id: int) -> bool:
        """Delete module"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM modules WHERE id = %s RETURNING id", (module_id,))
                if cur.fetchone():
                    conn.commit()
                    return True
                return False
        finally:
            pool.return_connection(conn)

