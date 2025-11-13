"""
Menu service for ms-cafeteria
"""
import logging
from typing import List, Tuple, Optional
from datetime import datetime, date
from db.connection import get_pool
from proto.generated import cafeteria_pb2

logger = logging.getLogger(__name__)


class MenuService:
    def get_menu(self, menu_date: str = None) -> List[cafeteria_pb2.MenuItem]:
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                target_date = menu_date or date.today().isoformat()
                cur.execute("""
                    SELECT id, name, description, category, price, available, date
                    FROM menu_items
                    WHERE date = %s AND available = TRUE
                    ORDER BY category, name
                """, (target_date,))
                
                items = []
                for row in cur.fetchall():
                    items.append(cafeteria_pb2.MenuItem(
                        id=row[0], name=row[1], description=row[2] or '',
                        category=row[3], price=float(row[4]), available=row[5],
                        date=row[6].isoformat() if row[6] else ''
                    ))
                
                return items
        finally:
            pool.return_connection(conn)
    
    def create_order(self, user_id: int, items: List[Tuple[int, int]]):
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                total_amount = 0.0
                order_items_data = []
                
                # Calculate total and get item names
                for menu_item_id, quantity in items:
                    cur.execute("SELECT name, price FROM menu_items WHERE id = %s AND available = TRUE", (menu_item_id,))
                    row = cur.fetchone()
                    if row:
                        item_name, item_price = row[0], float(row[1])
                        total_amount += item_price * quantity
                        order_items_data.append((menu_item_id, item_name, quantity, item_price))
                
                # Create order
                cur.execute("""
                    INSERT INTO orders (user_id, total_amount, order_date)
                    VALUES (%s, %s, %s)
                    RETURNING id, user_id, user_name, total_amount, status, order_date, created_at
                """, (user_id, total_amount, date.today()))
                
                order_row = cur.fetchone()
                order_id = order_row[0]
                
                # Create order items
                for menu_item_id, item_name, quantity, price in order_items_data:
                    cur.execute("""
                        INSERT INTO order_items (order_id, menu_item_id, menu_item_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, menu_item_id, item_name, quantity, price))
                
                conn.commit()
                
                # Build order items for response
                order_items = []
                for menu_item_id, item_name, quantity, price in order_items_data:
                    order_items.append(cafeteria_pb2.OrderItem(
                        menu_item_id=menu_item_id, menu_item_name=item_name,
                        quantity=quantity, price=price
                    ))
                
                return cafeteria_pb2.Order(
                    id=order_id, user_id=order_row[1], user_name=order_row[2] or '',
                    items=order_items, total_amount=float(order_row[3]),
                    status=order_row[4], order_date=order_row[5].isoformat() if order_row[5] else '',
                    created_at=order_row[6].isoformat() if order_row[6] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def get_order(self, order_id: int) -> Optional[cafeteria_pb2.Order]:
        """Get order by ID"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT o.id, o.user_id, o.user_name, o.total_amount, o.status, o.order_date, o.created_at
                    FROM orders o
                    WHERE o.id = %s
                """, (order_id,))
                
                order_row = cur.fetchone()
                if not order_row:
                    return None
                
                cur.execute("""
                    SELECT menu_item_id, menu_item_name, quantity, price
                    FROM order_items
                    WHERE order_id = %s
                """, (order_id,))
                
                order_items = []
                for row in cur.fetchall():
                    order_items.append(cafeteria_pb2.OrderItem(
                        menu_item_id=row[0], menu_item_name=row[1],
                        quantity=row[2], price=float(row[3])
                    ))
                
                return cafeteria_pb2.Order(
                    id=order_row[0], user_id=order_row[1], user_name=order_row[2] or '',
                    items=order_items, total_amount=float(order_row[3]),
                    status=order_row[4], order_date=order_row[5].isoformat() if order_row[5] else '',
                    created_at=order_row[6].isoformat() if order_row[6] else ''
                )
        finally:
            pool.return_connection(conn)
    
    def list_orders(self, page: int = 1, page_size: int = 50,
                   user_id: Optional[int] = None,
                   status: Optional[str] = None,
                   order_date: Optional[str] = None) -> Tuple[List[cafeteria_pb2.Order], int]:
        """List orders"""
        pool = get_pool()
        conn = pool.get_connection()
        try:
            with conn.cursor() as cur:
                where_clauses = []
                params = []
                
                if user_id:
                    where_clauses.append("o.user_id = %s")
                    params.append(user_id)
                if status:
                    where_clauses.append("o.status = %s")
                    params.append(status)
                if order_date:
                    where_clauses.append("o.order_date = %s")
                    params.append(order_date)
                
                where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                cur.execute(f"SELECT COUNT(*) FROM orders o {where_sql}", params)
                total = cur.fetchone()[0]
                
                offset = (page - 1) * page_size
                params.append(page_size)
                params.append(offset)
                
                cur.execute(f"""
                    SELECT o.id, o.user_id, o.user_name, o.total_amount, o.status, o.order_date, o.created_at
                    FROM orders o
                    {where_sql}
                    ORDER BY o.created_at DESC
                    LIMIT %s OFFSET %s
                """, params)
                
                orders = []
                for order_row in cur.fetchall():
                    order_id = order_row[0]
                    
                    cur.execute("""
                        SELECT menu_item_id, menu_item_name, quantity, price
                        FROM order_items
                        WHERE order_id = %s
                    """, (order_id,))
                    
                    order_items = []
                    for row in cur.fetchall():
                        order_items.append(cafeteria_pb2.OrderItem(
                            menu_item_id=row[0], menu_item_name=row[1],
                            quantity=row[2], price=float(row[3])
                        ))
                    
                    orders.append(cafeteria_pb2.Order(
                        id=order_row[0], user_id=order_row[1], user_name=order_row[2] or '',
                        items=order_items, total_amount=float(order_row[3]),
                        status=order_row[4], order_date=order_row[5].isoformat() if order_row[5] else '',
                        created_at=order_row[6].isoformat() if order_row[6] else ''
                    ))
                
                return orders, total
        finally:
            pool.return_connection(conn)

