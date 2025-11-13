"""
Event service for ms-events
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime
from db.connection import get_pool
from proto.generated import events_pb2

logger = logging.getLogger(__name__)


class EventService:
    """Service for event management"""
    
    def create_event(self, title: str, description: str, type: str,
                    location: str, start_time: str, end_time: str,
                    max_participants: int, created_by: int):
        """Create a new event"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (title, description, type, location, start_time, end_time, max_participants, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, title, description, type, location, start_time, end_time, max_participants, registered_count, created_by, created_at
                """, (title, description, type, location, start_time, end_time, max_participants, created_by))
                
                row = cur.fetchone()
                conn.commit()
                
                return events_pb2.Event(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    type=row[3],
                    location=row[4] or '',
                    start_time=row[5].isoformat() if row[5] else '',
                    end_time=row[6].isoformat() if row[6] else '',
                    max_participants=row[7] or 0,
                    registered_count=row[8] or 0,
                    created_by=row[9],
                    created_at=row[10].isoformat() if row[10] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_events(self, page: int = 1, page_size: int = 50,
                   type: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> Tuple[List[events_pb2.Event], int]:
        """List events with pagination"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                if type:
                    where_clauses.append("type = %s")
                    params.append(type)
                if start_date:
                    where_clauses.append("start_time >= %s")
                    params.append(start_date)
                if end_date:
                    where_clauses.append("end_time <= %s")
                    params.append(end_date)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                cur.execute(f"SELECT COUNT(*) FROM events {where_sql}", params)
                total = cur.fetchone()[0]
                
                offset = (page - 1) * page_size
                params.append(page_size)
                params.append(offset)
                
                cur.execute(f"""
                    SELECT id, title, description, type, location, start_time, end_time, max_participants, registered_count, created_by, created_at
                    FROM events
                    {where_sql}
                    ORDER BY start_time ASC
                    LIMIT %s OFFSET %s
                """, params)
                
                events = []
                for row in cur.fetchall():
                    events.append(events_pb2.Event(
                        id=row[0],
                        title=row[1],
                        description=row[2] or '',
                        type=row[3],
                        location=row[4] or '',
                        start_time=row[5].isoformat() if row[5] else '',
                        end_time=row[6].isoformat() if row[6] else '',
                        max_participants=row[7] or 0,
                        registered_count=row[8] or 0,
                        created_by=row[9],
                        created_at=row[10].isoformat() if row[10] else ''
                    ))
                
                return events, total
        finally:
            pool.return_connection(conn)
    
    def register_user(self, event_id: int, user_id: int) -> bool:
        """Register user for event"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Check if event exists and has space
                cur.execute("""
                    SELECT max_participants, registered_count
                    FROM events
                    WHERE id = %s
                """, (event_id,))
                
                row = cur.fetchone()
                if not row:
                    return False
                
                max_participants = row[0]
                registered_count = row[1] or 0
                
                if max_participants and registered_count >= max_participants:
                    return False
                
                cur.execute("""
                    INSERT INTO event_registrations (event_id, user_id)
                    VALUES (%s, %s)
                    ON CONFLICT (event_id, user_id) DO NOTHING
                    RETURNING id
                """, (event_id, user_id))
                
                if cur.fetchone():
                    conn.commit()
                    return True
                return False
        finally:
            pool.return_connection(conn)
    
    def get_event(self, event_id: int) -> Optional[events_pb2.Event]:
        """Get event by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, description, type, location, start_time, end_time, max_participants, registered_count, created_by, created_at
                    FROM events
                    WHERE id = %s
                """, (event_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return events_pb2.Event(
                    id=row[0],
                    title=row[1],
                    description=row[2] or '',
                    type=row[3],
                    location=row[4] or '',
                    start_time=row[5].isoformat() if row[5] else '',
                    end_time=row[6].isoformat() if row[6] else '',
                    max_participants=row[7] or 0,
                    registered_count=row[8] or 0,
                    created_by=row[9],
                    created_at=row[10].isoformat() if row[10] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def get_registrations(self, event_id: int) -> List[events_pb2.Registration]:
        """Get registrations for event"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, event_id, user_id, user_name, registered_at
                    FROM event_registrations
                    WHERE event_id = %s
                    ORDER BY registered_at ASC
                """, (event_id,))
                
                registrations = []
                for row in cur.fetchall():
                    registrations.append(events_pb2.Registration(
                        id=row[0],
                        event_id=row[1],
                        user_id=row[2],
                        user_name=row[3] or '',
                        registered_at=row[4].isoformat() if row[4] else ''
                    ))
                
                return registrations
        finally:
            pool.return_connection(conn)

