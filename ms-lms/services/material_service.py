"""
Material service for ms-lms
"""
import logging
from typing import List
from db.connection import get_pool
from proto.generated import lms_pb2

logger = logging.getLogger(__name__)


class MaterialService:
    """Service for material management"""
    
    def add_material(self, module_id: int, title: str, type: str, 
                    content: str, file_path: str, order: int):
        """Add material to module"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO materials (module_id, title, type, content, file_path, order_index)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, module_id, title, type, content, file_path, order_index, created_at
                """, (module_id, title, type, content, file_path, order))
                
                row = cur.fetchone()
                conn.commit()
                
                return lms_pb2.Material(
                    id=row[0],
                    module_id=row[1],
                    title=row[2],
                    type=row[3],
                    content=row[4] or '',
                    file_path=row[5] or '',
                    order=row[6],
                    created_at=row[7].isoformat() if row[7] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_materials(self, module_id: int) -> List[lms_pb2.Material]:
        """List materials for a module"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, module_id, title, type, content, file_path, order_index, created_at
                    FROM materials
                    WHERE module_id = %s
                    ORDER BY order_index ASC
                """, (module_id,))
                
                materials = []
                for row in cur.fetchall():
                    materials.append(lms_pb2.Material(
                        id=row[0],
                        module_id=row[1],
                        title=row[2],
                        type=row[3],
                        content=row[4] or '',
                        file_path=row[5] or '',
                        order=row[6],
                        created_at=row[7].isoformat() if row[7] else ''
                    ))
                
                return materials
        finally:
            pool.return_connection(conn)
    
    def get_material(self, material_id: int):
        """Get material by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, module_id, title, type, content, file_path, order_index, created_at
                    FROM materials
                    WHERE id = %s
                """, (material_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return lms_pb2.Material(
                    id=row[0], module_id=row[1], title=row[2],
                    type=row[3], content=row[4] or '',
                    file_path=row[5] or '', order=row[6],
                    created_at=row[7].isoformat() if row[7] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def delete_material(self, material_id: int) -> bool:
        """Delete material"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM materials WHERE id = %s RETURNING id", (material_id,))
                if cur.fetchone():
                    conn.commit()
                    return True
                return False
        finally:
            pool.return_connection(conn)

