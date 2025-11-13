"""
gRPC service implementation for ms-events
"""
import logging
from datetime import datetime
import grpc

from proto.generated import events_pb2, events_pb2_grpc
from services.event_service import EventService

logger = logging.getLogger(__name__)


class EventsServicer(events_pb2_grpc.EventsServiceServicer):
    """gRPC servicer for event operations"""
    
    def __init__(self):
        self.event_service = EventService()
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        return events_pb2.HealthCheckResponse(
            status='healthy',
            version='1.0.0',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def CreateEvent(self, request, context):
        """Create a new event"""
        try:
            event = self.event_service.create_event(
                title=request.title,
                description=request.description,
                type=request.type,
                location=request.location,
                start_time=request.start_time,
                end_time=request.end_time,
                max_participants=request.max_participants,
                created_by=request.created_by
            )
            return events_pb2.EventResponse(event=event, message="Event created successfully")
        except Exception as e:
            logger.error(f"CreateEvent error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return events_pb2.EventResponse()
    
    def ListEvents(self, request, context):
        """List events"""
        try:
            events, total = self.event_service.list_events(
                page=request.page or 1,
                page_size=request.page_size or 50,
                type=request.type if request.type else None,
                start_date=request.start_date if request.start_date else None,
                end_date=request.end_date if request.end_date else None
            )
            return events_pb2.EventsListResponse(events=events, total_count=total)
        except Exception as e:
            logger.error(f"ListEvents error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return events_pb2.EventsListResponse()
    
    def RegisterForEvent(self, request, context):
        """Register user for event"""
        try:
            success = self.event_service.register_user(
                event_id=request.event_id,
                user_id=request.user_id
            )
            return events_pb2.RegisterResponse(
                success=success,
                message="Registered successfully" if success else "Already registered or event full"
            )
        except Exception as e:
            logger.error(f"RegisterForEvent error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return events_pb2.RegisterResponse(success=False, message=str(e))
    
    def GetEvent(self, request, context):
        """Get event by ID"""
        try:
            event = self.event_service.get_event(request.id)
            if not event:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Event {request.id} not found")
                return events_pb2.EventResponse()
            return events_pb2.EventResponse(event=event)
        except Exception as e:
            logger.error(f"GetEvent error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return events_pb2.EventResponse()
    
    def GetRegistrations(self, request, context):
        """Get registrations for event"""
        try:
            registrations = self.event_service.get_registrations(request.event_id)
            return events_pb2.RegistrationsResponse(registrations=registrations, total_count=len(registrations))
        except Exception as e:
            logger.error(f"GetRegistrations error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return events_pb2.RegistrationsResponse()

