"""
gRPC service implementation for ms-cafeteria
"""
import logging
from datetime import datetime
import grpc
from proto.generated import cafeteria_pb2, cafeteria_pb2_grpc
from services.menu_service import MenuService

logger = logging.getLogger(__name__)


class CafeteriaServicer(cafeteria_pb2_grpc.CafeteriaServiceServicer):
    def __init__(self):
        self.menu_service = MenuService()
    
    def HealthCheck(self, request, context):
        return cafeteria_pb2.HealthCheckResponse(
            status='healthy', version='1.0.0',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def GetMenu(self, request, context):
        try:
            items = self.menu_service.get_menu(request.date if request.date else None)
            return cafeteria_pb2.MenuResponse(items=items, date=request.date or datetime.now().date().isoformat())
        except Exception as e:
            logger.error(f"GetMenu error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafeteria_pb2.MenuResponse()
    
    def CreateOrder(self, request, context):
        try:
            order = self.menu_service.create_order(
                user_id=request.user_id,
                items=[(item.menu_item_id, item.quantity) for item in request.items]
            )
            return cafeteria_pb2.OrderResponse(order=order, message="Order created successfully")
        except Exception as e:
            logger.error(f"CreateOrder error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafeteria_pb2.OrderResponse()
    
    def GetOrder(self, request, context):
        try:
            order = self.menu_service.get_order(request.id)
            if not order:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Order {request.id} not found")
                return cafeteria_pb2.OrderResponse()
            return cafeteria_pb2.OrderResponse(order=order)
        except Exception as e:
            logger.error(f"GetOrder error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafeteria_pb2.OrderResponse()
    
    def ListOrders(self, request, context):
        try:
            orders, total = self.menu_service.list_orders(
                page=request.page or 1,
                page_size=request.page_size or 50,
                user_id=request.user_id if request.user_id else None,
                status=request.status if request.status else None,
                order_date=request.date if request.date else None
            )
            return cafeteria_pb2.OrdersListResponse(orders=orders, total_count=total)
        except Exception as e:
            logger.error(f"ListOrders error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return cafeteria_pb2.OrdersListResponse()

