"""
Tickets RPC Client для Gateway
Подключение к ms-tickets
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

try:
    from rpc_clients.generated import tickets_pb2, tickets_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    tickets_pb2 = None
    tickets_pb2_grpc = None

logger = logging.getLogger(__name__)


class TicketsClient:
    """RPC клиент для ms-tickets"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('MS_TICKETS_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_TICKETS_PORT', 50056))
        self.address = f'{self.host}:{self.port}'
        
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if tickets_pb2_grpc:
            self.stub = tickets_pb2_grpc.TicketsServiceStub(self.channel)
            logger.info(f"TicketsClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available")
    
    def create_ticket(self, title: str, description: str, category: str, created_by: int, priority: int = 3) -> Dict[str, Any]:
        """Создать тикет"""
        if not self.stub:
            raise Exception("Tickets service not available")
        
        request = tickets_pb2.CreateTicketRequest(
            title=title,
            description=description,
            category=category,
            created_by=created_by,
            priority=priority
        )
        
        response = self.stub.CreateTicket(request, timeout=10)
        
        if not response.ticket.id:
            raise Exception(response.message or "Failed to create ticket")
        
        return {
            'id': response.ticket.id,
            'title': response.ticket.title,
            'description': response.ticket.description,
            'category': response.ticket.category,
            'status': response.ticket.status,
            'created_by': response.ticket.created_by,
            'created_by_name': response.ticket.created_by_name,
            'assigned_to': response.ticket.assigned_to or 0,
            'assigned_to_name': response.ticket.assigned_to_name or '',
            'priority': response.ticket.priority,
            'created_at': response.ticket.created_at,
            'updated_at': response.ticket.updated_at
        }
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Получить тикет по ID"""
        if not self.stub:
            raise Exception("Tickets service not available")
        
        request = tickets_pb2.GetTicketRequest(id=ticket_id)
        response = self.stub.GetTicket(request, timeout=10)
        
        if not response.ticket.id:
            return None
        
        return {
            'id': response.ticket.id,
            'title': response.ticket.title,
            'description': response.ticket.description,
            'category': response.ticket.category,
            'status': response.ticket.status,
            'created_by': response.ticket.created_by,
            'created_by_name': response.ticket.created_by_name,
            'assigned_to': response.ticket.assigned_to or 0,
            'assigned_to_name': response.ticket.assigned_to_name or '',
            'priority': response.ticket.priority,
            'created_at': response.ticket.created_at,
            'updated_at': response.ticket.updated_at
        }
    
    def list_tickets(self, page: int = 1, page_size: int = 50,
                     created_by: Optional[int] = None,
                     assigned_to: Optional[int] = None,
                     status: Optional[str] = None,
                     category: Optional[str] = None) -> Dict[str, Any]:
        """Список тикетов"""
        if not self.stub:
            raise Exception("Tickets service not available")
        
        request = tickets_pb2.ListTicketsRequest(
            page=page,
            page_size=page_size,
            created_by=created_by or 0,
            assigned_to=assigned_to or 0,
            status=status or '',
            category=category or ''
        )
        
        response = self.stub.ListTickets(request, timeout=10)
        
        tickets = []
        for ticket in response.tickets:
            tickets.append({
                'id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'category': ticket.category,
                'status': ticket.status,
                'created_by': ticket.created_by,
                'created_by_name': ticket.created_by_name,
                'assigned_to': ticket.assigned_to or 0,
                'assigned_to_name': ticket.assigned_to_name or '',
                'priority': ticket.priority,
                'created_at': ticket.created_at,
                'updated_at': ticket.updated_at
            })
        
        return {
            'tickets': tickets,
            'total_count': response.total_count
        }
    
    def add_comment(self, ticket_id: int, user_id: int, content: str) -> Dict[str, Any]:
        """Добавить комментарий к тикету"""
        if not self.stub:
            raise Exception("Tickets service not available")
        
        request = tickets_pb2.AddCommentRequest(
            ticket_id=ticket_id,
            user_id=user_id,
            content=content
        )
        
        response = self.stub.AddComment(request, timeout=10)
        
        if not response.comment.id:
            raise Exception(response.message or "Failed to add comment")
        
        return {
            'id': response.comment.id,
            'ticket_id': response.comment.ticket_id,
            'user_id': response.comment.user_id,
            'user_name': response.comment.user_name,
            'content': response.comment.content,
            'created_at': response.comment.created_at
        }
    
    def list_comments(self, ticket_id: int) -> List[Dict[str, Any]]:
        """Список комментариев для тикета"""
        if not self.stub:
            raise Exception("Tickets service not available")
        
        request = tickets_pb2.ListCommentsRequest(ticket_id=ticket_id)
        response = self.stub.ListComments(request, timeout=10)
        
        comments = []
        for comment in response.comments:
            comments.append({
                'id': comment.id,
                'ticket_id': comment.ticket_id,
                'user_id': comment.user_id,
                'user_name': comment.user_name,
                'content': comment.content,
                'created_at': comment.created_at
            })
        
        return comments
    
    def update_ticket(self, ticket_id: int, status: Optional[str] = None,
                     assigned_to: Optional[int] = None,
                     priority: Optional[int] = None) -> Dict[str, Any]:
        """Обновить тикет"""
        if not self.stub:
            raise Exception("Tickets service not available")
        
        request = tickets_pb2.UpdateTicketRequest(
            id=ticket_id,
            status=status or '',
            assigned_to=assigned_to or 0,
            priority=priority or 0
        )
        
        response = self.stub.UpdateTicket(request, timeout=10)
        
        if not response.ticket.id:
            raise Exception(response.message or "Failed to update ticket")
        
        return {
            'id': response.ticket.id,
            'title': response.ticket.title,
            'description': response.ticket.description,
            'category': response.ticket.category,
            'status': response.ticket.status,
            'created_by': response.ticket.created_by,
            'created_by_name': response.ticket.created_by_name,
            'assigned_to': response.ticket.assigned_to or 0,
            'assigned_to_name': response.ticket.assigned_to_name or '',
            'priority': response.ticket.priority,
            'created_at': response.ticket.created_at,
            'updated_at': response.ticket.updated_at
        }


# Singleton instance
_tickets_client: Optional[TicketsClient] = None


def get_tickets_client() -> TicketsClient:
    """Get singleton tickets client"""
    global _tickets_client
    if _tickets_client is None:
        _tickets_client = TicketsClient()
    return _tickets_client

