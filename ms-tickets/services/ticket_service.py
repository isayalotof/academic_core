"""
Ticket service for ms-tickets
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from db.connection import get_pool
from proto.generated import tickets_pb2

logger = logging.getLogger(__name__)


class TicketService:
    """Service for ticket management"""
    
    def create_ticket(self, title: str, description: str, category: str,
                     created_by: int, created_by_name: str = '', priority: int = 3):
        """Create a new ticket"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tickets (title, description, category, created_by, created_by_name, priority)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, title, description, category, status, created_by,
                              created_by_name, assigned_to, assigned_to_name, priority,
                              created_at, updated_at
                """, (title, description, category, created_by, created_by_name or '', priority))
                
                row = cur.fetchone()
                conn.commit()
                
                return tickets_pb2.Ticket(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    category=row[3],
                    status=row[4],
                    created_by=row[5],
                    created_by_name=row[6] or '',
                    assigned_to=row[7] or 0,
                    assigned_to_name=row[8] or '',
                    priority=row[9],
                    created_at=row[10].isoformat() if row[10] else '',
                    updated_at=row[11].isoformat() if row[11] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def get_ticket(self, ticket_id: int) -> Optional[tickets_pb2.Ticket]:
        """Get ticket by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, category, status, created_by,
                           created_by_name, assigned_to, assigned_to_name, priority,
                           created_at, updated_at
                    FROM tickets
                    WHERE id = %s
                """, (ticket_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return tickets_pb2.Ticket(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    category=row[3],
                    status=row[4],
                    created_by=row[5],
                    created_by_name=row[6] or '',
                    assigned_to=row[7] or 0,
                    assigned_to_name=row[8] or '',
                    priority=row[9],
                    created_at=row[10].isoformat() if row[10] else '',
                    updated_at=row[11].isoformat() if row[11] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_tickets(self, page: int = 1, page_size: int = 50,
                    created_by: Optional[int] = None,
                    assigned_to: Optional[int] = None,
                    status: Optional[str] = None,
                    category: Optional[str] = None) -> Tuple[List[tickets_pb2.Ticket], int]:
        """List tickets with pagination"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                # -1 означает "не фильтровать", None тоже означает "не фильтровать"
                # Только если передан валидный положительный ID, фильтруем
                if created_by is not None and created_by > 0:
                    where_clauses.append("created_by = %s")
                    params.append(created_by)
                if assigned_to is not None and assigned_to > 0:
                    where_clauses.append("assigned_to = %s")
                    params.append(assigned_to)
                if status:
                    where_clauses.append("status = %s")
                    params.append(status)
                if category:
                    where_clauses.append("category = %s")
                    params.append(category)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                cur.execute(f"SELECT COUNT(*) FROM tickets {where_sql}", params)
                total = cur.fetchone()[0]
                
                offset = (page - 1) * page_size
                params.append(page_size)
                params.append(offset)
                
                cur.execute(f"""
                    SELECT id, title, description, category, status, created_by,
                           created_by_name, assigned_to, assigned_to_name, priority,
                           created_at, updated_at
                    FROM tickets
                    {where_sql}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """, params)
                
                tickets = []
                for row in cur.fetchall():
                    tickets.append(tickets_pb2.Ticket(
                        id=row[0],
                        title=row[1],
                        description=row[2] or '',
                        category=row[3],
                        status=row[4],
                        created_by=row[5],
                        created_by_name=row[6] or '',
                        assigned_to=row[7] or 0,
                        assigned_to_name=row[8] or '',
                        priority=row[9],
                        created_at=row[10].isoformat() if row[10] else '',
                        updated_at=row[11].isoformat() if row[11] else ''
                    ))
                
                return tickets, total
        finally:
            pool.return_connection(conn)
    
    def add_comment(self, ticket_id: int, user_id: int, content: str):
        """Add comment to ticket"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO ticket_comments (ticket_id, user_id, content)
                    VALUES (%s, %s, %s)
                    RETURNING id, ticket_id, user_id, user_name, content, created_at
                """, (ticket_id, user_id, content))
                
                row = cur.fetchone()
                conn.commit()
                
                return tickets_pb2.Comment(
                    id=row[0],
                    ticket_id=row[1],
                    user_id=row[2],
                    user_name=row[3] or '',
                    content=row[4],
                    created_at=row[5].isoformat() if row[5] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_comments(self, ticket_id: int) -> List[tickets_pb2.Comment]:
        """List comments for ticket"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, ticket_id, user_id, user_name, content, created_at
                    FROM ticket_comments
                    WHERE ticket_id = %s
                    ORDER BY created_at ASC
                """, (ticket_id,))
                
                comments = []
                for row in cur.fetchall():
                    comments.append(tickets_pb2.Comment(
                        id=row[0],
                        ticket_id=row[1],
                        user_id=row[2],
                        user_name=row[3] or '',
                        content=row[4],
                        created_at=row[5].isoformat() if row[5] else ''
                    ))
                
                return comments
        finally:
            pool.return_connection(conn)
    
    def update_ticket(self, ticket_id: int, status: Optional[str] = None,
                     assigned_to: Optional[int] = None,
                     priority: Optional[int] = None) -> Optional[tickets_pb2.Ticket]:
        """Update ticket"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                updates = []
                params = []
                
                if status:
                    updates.append("status = %s")
                    params.append(status)
                if assigned_to:
                    updates.append("assigned_to = %s")
                    params.append(assigned_to)
                if priority:
                    updates.append("priority = %s")
                    params.append(priority)
                
                if not updates:
                    return self.get_ticket(ticket_id)
                
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(ticket_id)
                
                cur.execute(f"""
                    UPDATE tickets
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING id, title, description, category, status, created_by,
                              created_by_name, assigned_to, assigned_to_name, priority,
                              created_at, updated_at
                """, params)
                
                row = cur.fetchone()
                conn.commit()
                
                if not row:
                    return None
                
                return tickets_pb2.Ticket(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    category=row[3],
                    status=row[4],
                    created_by=row[5],
                    created_by_name=row[6] or '',
                    assigned_to=row[7] or 0,
                    assigned_to_name=row[8] or '',
                    priority=row[9],
                    created_at=row[10].isoformat() if row[10] else '',
                    updated_at=row[11].isoformat() if row[11] else ''
                )
        finally:
            pool.return_connection(conn)

