"""
Book service for ms-library
"""
import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from db.connection import get_pool
from proto.generated import library_pb2

logger = logging.getLogger(__name__)


class BookService:
    def add_book(self, title: str, author: str, isbn: str, category: str, total_copies: int):
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO books (title, author, isbn, category, total_copies, available_copies)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, title, author, isbn, category, total_copies, available_copies, created_at
                """, (title, author, isbn, category, total_copies, total_copies))
                
                row = cur.fetchone()
                conn.commit()
                
                return library_pb2.Book(
                    id=row[0], title=row[1], author=row[2] or '',
                    isbn=row[3] or '', category=row[4] or '',
                    total_copies=row[5], available_copies=row[6],
                    created_at=row[7].isoformat() if row[7] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_books(self, page: int = 1, page_size: int = 50,
                  author: Optional[str] = None, category: Optional[str] = None,
                  search: Optional[str] = None) -> Tuple[List[library_pb2.Book], int]:
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                if author:
                    where_clauses.append("author ILIKE %s")
                    params.append(f"%{author}%")
                if category:
                    where_clauses.append("category = %s")
                    params.append(category)
                if search:
                    where_clauses.append("(title ILIKE %s OR author ILIKE %s)")
                    params.extend([f"%{search}%", f"%{search}%"])
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                cur.execute(f"SELECT COUNT(*) FROM books {where_sql}", params)
                total = cur.fetchone()[0]
                
                offset = (page - 1) * page_size
                params.append(page_size)
                params.append(offset)
                
                cur.execute(f"""
                    SELECT id, title, author, isbn, category, total_copies, available_copies, created_at
                    FROM books
                    {where_sql}
                    ORDER BY title ASC
                    LIMIT %s OFFSET %s
                """, params)
                
                books = []
                for row in cur.fetchall():
                    books.append(library_pb2.Book(
                        id=row[0], title=row[1], author=row[2] or '',
                        isbn=row[3] or '', category=row[4] or '',
                        total_copies=row[5], available_copies=row[6],
                        created_at=row[7].isoformat() if row[7] else ''
                    ))
                
                return books, total
        finally:
            pool.return_connection(conn)
    
    def reserve_book(self, book_id: int, user_id: int, days: int = 14) -> Optional[int]:
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Check availability
                cur.execute("SELECT available_copies FROM books WHERE id = %s", (book_id,))
                row = cur.fetchone()
                if not row or row[0] <= 0:
                    return None
                
                due_date = datetime.now() + timedelta(days=days)
                cur.execute("""
                    INSERT INTO book_reservations (book_id, user_id, status, due_date)
                    VALUES (%s, %s, 'borrowed', %s)
                    RETURNING id
                """, (book_id, user_id, due_date))
                
                reservation_id = cur.fetchone()[0]
                
                # Update available copies
                cur.execute("""
                    UPDATE books
                    SET available_copies = available_copies - 1
                    WHERE id = %s
                """, (book_id,))
                
                conn.commit()
                return reservation_id
        finally:
            pool.return_connection(conn)
    
    def get_book(self, book_id: int) -> Optional[library_pb2.Book]:
        """Get book by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, author, isbn, category, total_copies, available_copies, created_at
                    FROM books
                    WHERE id = %s
                """, (book_id,))
                
                row = cur.fetchone()
                if not row:
                    return None
                
                return library_pb2.Book(
                    id=row[0], title=row[1], author=row[2] or '',
                    isbn=row[3] or '', category=row[4] or '',
                    total_copies=row[5], available_copies=row[6],
                    created_at=row[7].isoformat() if row[7] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def get_reservations(self, user_id: Optional[int] = None,
                        status: Optional[str] = None) -> List[library_pb2.Reservation]:
        """Get reservations"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                if user_id:
                    where_clauses.append("user_id = %s")
                    params.append(user_id)
                if status:
                    where_clauses.append("status = %s")
                    params.append(status)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                cur.execute(f"""
                    SELECT id, book_id, user_id, user_name, status, reserved_at, due_date, returned_at
                    FROM book_reservations
                    {where_sql}
                    ORDER BY reserved_at DESC
                """, params)
                
                reservations = []
                for row in cur.fetchall():
                    reservations.append(library_pb2.Reservation(
                        id=row[0], book_id=row[1], user_id=row[2],
                        user_name=row[3] or '', status=row[4],
                        reserved_at=row[5].isoformat() if row[5] else '',
                        due_date=row[6].isoformat() if row[6] else '',
                        returned_at=row[7].isoformat() if row[7] else ''
                    ))
                
                return reservations
        finally:
            pool.return_connection(conn)
    
    def return_book(self, reservation_id: int) -> bool:
        """Return book"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                # Get book_id before updating
                cur.execute("""
                    SELECT book_id FROM book_reservations
                    WHERE id = %s AND status != 'returned'
                """, (reservation_id,))
                
                row = cur.fetchone()
                if not row:
                    return False
                
                book_id = row[0]
                
                # Update reservation
                cur.execute("""
                    UPDATE book_reservations
                    SET status = 'returned', returned_at = CURRENT_TIMESTAMP
                    WHERE id = %s AND status != 'returned'
                    RETURNING id
                """, (reservation_id,))
                
                if cur.fetchone():
                    # Update available copies
                    cur.execute("""
                        UPDATE books
                        SET available_copies = available_copies + 1
                        WHERE id = %s
                    """, (book_id,))
                    
                    conn.commit()
                    return True
                return False
        finally:
            pool.return_connection(conn)

