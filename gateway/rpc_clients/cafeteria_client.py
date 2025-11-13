"""
Cafeteria RPC Client для Gateway
Подключение к ms-cafeteria
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

try:
    from rpc_clients.generated import cafeteria_pb2, cafeteria_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    cafeteria_pb2 = None
    cafeteria_pb2_grpc = None

logger = logging.getLogger(__name__)


class CafeteriaClient:
    """RPC клиент для ms-cafeteria"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('MS_CAFETERIA_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_CAFETERIA_PORT', 50060))
        self.address = f'{self.host}:{self.port}'
        
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if cafeteria_pb2_grpc:
            self.stub = cafeteria_pb2_grpc.CafeteriaServiceStub(self.channel)
            logger.info(f"CafeteriaClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available")
    
    def get_menu(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить меню"""
        if not self.stub:
            raise Exception("Cafeteria service not available")
        
        request = cafeteria_pb2.GetMenuRequest(date=date or '')
        response = self.stub.GetMenu(request, timeout=10)
        
        items = []
        for item in response.items:
            items.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'category': item.category,
                'price': item.price,
                'available': item.available,
                'date': item.date
            })
        
        return items
    
    def create_order(self, user_id: int, items: List[Dict[str, int]]) -> Dict[str, Any]:
        """Создать заказ"""
        if not self.stub:
            raise Exception("Cafeteria service not available")
        
        order_items = []
        for item in items:
            order_items.append(
                cafeteria_pb2.OrderItemRequest(
                    menu_item_id=item['menu_item_id'],
                    quantity=item['quantity']
                )
            )
        
        request = cafeteria_pb2.CreateOrderRequest(
            user_id=user_id,
            items=order_items
        )
        
        response = self.stub.CreateOrder(request, timeout=10)
        
        if not response.order.id:
            raise Exception(response.message or "Failed to create order")
        
        order_items_list = []
        for item in response.order.items:
            order_items_list.append({
                'menu_item_id': item.menu_item_id,
                'menu_item_name': item.menu_item_name,
                'quantity': item.quantity,
                'price': item.price
            })
        
        return {
            'id': response.order.id,
            'user_id': response.order.user_id,
            'user_name': response.order.user_name,
            'items': order_items_list,
            'total_amount': response.order.total_amount,
            'status': response.order.status,
            'order_date': response.order.order_date,
            'created_at': response.order.created_at
        }
    
    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Получить заказ по ID"""
        if not self.stub:
            raise Exception("Cafeteria service not available")
        
        request = cafeteria_pb2.GetOrderRequest(id=order_id)
        response = self.stub.GetOrder(request, timeout=10)
        
        if not response.order.id:
            return None
        
        order_items_list = []
        for item in response.order.items:
            order_items_list.append({
                'menu_item_id': item.menu_item_id,
                'menu_item_name': item.menu_item_name,
                'quantity': item.quantity,
                'price': item.price
            })
        
        return {
            'id': response.order.id,
            'user_id': response.order.user_id,
            'user_name': response.order.user_name,
            'items': order_items_list,
            'total_amount': response.order.total_amount,
            'status': response.order.status,
            'order_date': response.order.order_date,
            'created_at': response.order.created_at
        }
    
    def list_orders(self, page: int = 1, page_size: int = 50,
                   user_id: Optional[int] = None,
                   status: Optional[str] = None,
                   date: Optional[str] = None) -> Dict[str, Any]:
        """Список заказов"""
        if not self.stub:
            raise Exception("Cafeteria service not available")
        
        request = cafeteria_pb2.ListOrdersRequest(
            page=page,
            page_size=page_size,
            user_id=user_id or 0,
            status=status or '',
            date=date or ''
        )
        
        response = self.stub.ListOrders(request, timeout=10)
        
        orders = []
        for order in response.orders:
            order_items_list = []
            for item in order.items:
                order_items_list.append({
                    'menu_item_id': item.menu_item_id,
                    'menu_item_name': item.menu_item_name,
                    'quantity': item.quantity,
                    'price': item.price
                })
            
            orders.append({
                'id': order.id,
                'user_id': order.user_id,
                'user_name': order.user_name,
                'items': order_items_list,
                'total_amount': order.total_amount,
                'status': order.status,
                'order_date': order.order_date,
                'created_at': order.created_at
            })
        
        return {
            'orders': orders,
            'total_count': response.total_count
        }


_cafeteria_client: Optional[CafeteriaClient] = None


def get_cafeteria_client() -> CafeteriaClient:
    """Get singleton cafeteria client"""
    global _cafeteria_client
    if _cafeteria_client is None:
        _cafeteria_client = CafeteriaClient()
    return _cafeteria_client

