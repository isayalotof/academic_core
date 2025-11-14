"""
gRPC service implementation for ms-tickets
"""
import logging
from datetime import datetime
import grpc

from proto.generated import tickets_pb2, tickets_pb2_grpc
from services.ticket_service import TicketService

logger = logging.getLogger(__name__)


class TicketsServicer(tickets_pb2_grpc.TicketsServiceServicer):
    """gRPC servicer for ticket operations"""
    
    def __init__(self):
        self.ticket_service = TicketService()
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        return tickets_pb2.HealthCheckResponse(
            status='healthy',
            version='1.0.0',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def CreateTicket(self, request, context):
        """Create a new ticket"""
        try:
            ticket = self.ticket_service.create_ticket(
                title=request.title,
                description=request.description,
                category=request.category,
                created_by=request.created_by,
                created_by_name=request.created_by_name or '',
                priority=request.priority or 3
            )
            return tickets_pb2.TicketResponse(ticket=ticket, message="Ticket created successfully")
        except Exception as e:
            logger.error(f"CreateTicket error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tickets_pb2.TicketResponse()
    
    def GetTicket(self, request, context):
        """Get ticket by ID"""
        try:
            ticket = self.ticket_service.get_ticket(request.id)
            if not ticket:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Ticket {request.id} not found")
                return tickets_pb2.TicketResponse()
            return tickets_pb2.TicketResponse(ticket=ticket)
        except Exception as e:
            logger.error(f"GetTicket error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tickets_pb2.TicketResponse()
    
    def ListTickets(self, request, context):
        """List tickets"""
        try:
            # В protobuf int32 по умолчанию равен 0, поэтому 0 означает "не фильтровать"
            # Преобразуем 0 в None для service слоя
            created_by = request.created_by if request.created_by > 0 else None
            assigned_to = request.assigned_to if request.assigned_to > 0 else None
            
            tickets, total = self.ticket_service.list_tickets(
                page=request.page or 1,
                page_size=request.page_size or 50,
                created_by=created_by,
                assigned_to=assigned_to,
                status=request.status if request.status else None,
                category=request.category if request.category else None
            )
            return tickets_pb2.TicketsListResponse(tickets=tickets, total_count=total)
        except Exception as e:
            logger.error(f"ListTickets error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tickets_pb2.TicketsListResponse()
    
    def AddComment(self, request, context):
        """Add comment to ticket"""
        try:
            comment = self.ticket_service.add_comment(
                ticket_id=request.ticket_id,
                user_id=request.user_id,
                content=request.content
            )
            return tickets_pb2.CommentResponse(comment=comment, message="Comment added successfully")
        except Exception as e:
            logger.error(f"AddComment error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tickets_pb2.CommentResponse()
    
    def ListComments(self, request, context):
        """List comments for ticket"""
        try:
            comments = self.ticket_service.list_comments(request.ticket_id)
            return tickets_pb2.CommentsListResponse(comments=comments, total_count=len(comments))
        except Exception as e:
            logger.error(f"ListComments error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tickets_pb2.CommentsListResponse()
    
    def UpdateTicket(self, request, context):
        """Update ticket"""
        try:
            ticket = self.ticket_service.update_ticket(
                ticket_id=request.id,
                status=request.status if request.status else None,
                assigned_to=request.assigned_to if request.assigned_to else None,
                priority=request.priority if request.priority else None
            )
            if not ticket:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Ticket {request.id} not found")
                return tickets_pb2.TicketResponse()
            return tickets_pb2.TicketResponse(ticket=ticket, message="Ticket updated successfully")
        except Exception as e:
            logger.error(f"UpdateTicket error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return tickets_pb2.TicketResponse()

