"""
Document service for ms-documents
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from db.connection import get_pool
from proto.generated import documents_pb2

logger = logging.getLogger(__name__)


class DocumentService:
    def create_request(self, document_type: str, purpose: str, requested_by: int, notes: Optional[str] = None):
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO document_requests (document_type, purpose, requested_by, notes)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, document_type, purpose, status, requested_by, requested_by_name,
                              requested_at, processed_at, file_path, notes
                """, (document_type, purpose, requested_by, notes))
                
                row = cur.fetchone()
                conn.commit()
                
                return documents_pb2.DocumentRequest(
                    id=row[0], document_type=row[1], purpose=row[2] or '',
                    status=row[3], requested_by=row[4], requested_by_name=row[5] or '',
                    requested_at=row[6].isoformat() if row[6] else '',
                    processed_at=row[7].isoformat() if row[7] else '',
                    file_path=row[8] or '', notes=row[9] or ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_requests(self, page: int = 1, page_size: int = 50,
                     requested_by: Optional[int] = None,
                     status: Optional[str] = None,
                     document_type: Optional[str] = None) -> Tuple[List[documents_pb2.DocumentRequest], int]:
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                if requested_by:
                    where_clauses.append("requested_by = %s")
                    params.append(requested_by)
                if status:
                    where_clauses.append("status = %s")
                    params.append(status)
                if document_type:
                    where_clauses.append("document_type = %s")
                    params.append(document_type)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                cur.execute(f"SELECT COUNT(*) FROM document_requests {where_sql}", params)
                total = cur.fetchone()[0]
                
                offset = (page - 1) * page_size
                params.append(page_size)
                params.append(offset)
                
                cur.execute(f"""
                    SELECT id, document_type, purpose, status, requested_by, requested_by_name,
                           requested_at, processed_at, file_path, notes
                    FROM document_requests
                    {where_sql}
                    ORDER BY requested_at DESC
                    LIMIT %s OFFSET %s
                """, params)
                
                requests = []
                for row in cur.fetchall():
                    requests.append(documents_pb2.DocumentRequest(
                        id=row[0], document_type=row[1], purpose=row[2] or '',
                        status=row[3], requested_by=row[4], requested_by_name=row[5] or '',
                        requested_at=row[6].isoformat() if row[6] else '',
                        processed_at=row[7].isoformat() if row[7] else '',
                        file_path=row[8] or '', notes=row[9] or ''
                    ))
                
                return requests, total
        finally:
            pool.return_connection(conn)
    
    def get_request(self, request_id: int) -> Optional[documents_pb2.DocumentRequest]:
        """Get request by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, document_type, purpose, status, requested_by, requested_by_name,
                           requested_at, processed_at, file_path, notes
                    FROM document_requests
                    WHERE id = %s
                """, (request_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return documents_pb2.DocumentRequest(
                    id=row[0], document_type=row[1], purpose=row[2] or '',
                    status=row[3], requested_by=row[4], requested_by_name=row[5] or '',
                    requested_at=row[6].isoformat() if row[6] else '',
                    processed_at=row[7].isoformat() if row[7] else '',
                    file_path=row[8] or '', notes=row[9] or ''
                )
        finally:
            pool.return_connection(conn)

