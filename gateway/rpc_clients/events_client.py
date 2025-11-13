"""
Events RPC Client для Gateway
Подключение к ms-events
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

try:
    from rpc_clients.generated import events_pb2, events_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    events_pb2 = None
    events_pb2_grpc = None

logger = logging.getLogger(__name__)


class EventsClient:
    """RPC клиент для ms-events"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('MS_EVENTS_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_EVENTS_PORT', 50057))
        self.address = f'{self.host}:{self.port}'
        
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if events_pb2_grpc:
            self.stub = events_pb2_grpc.EventsServiceStub(self.channel)
            logger.info(f"EventsClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available")
    
    def list_events(self, page: int = 1, page_size: int = 50,
                   type: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> Dict[str, Any]:
        """Список событий"""
        if not self.stub:
            raise Exception("Events service not available")
        
        request = events_pb2.ListEventsRequest(
            page=page,
            page_size=page_size,
            type=type or '',
            start_date=start_date or '',
            end_date=end_date or ''
        )
        
        response = self.stub.ListEvents(request, timeout=10)
        
        events = []
        for event in response.events:
            events.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'type': event.type,
                'location': event.location,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'max_participants': event.max_participants,
                'registered_count': event.registered_count,
                'created_by': event.created_by,
                'created_at': event.created_at
            })
        
        return {
            'events': events,
            'total_count': response.total_count
        }
    
    def register_for_event(self, event_id: int, user_id: int) -> Dict[str, Any]:
        """Зарегистрироваться на событие"""
        if not self.stub:
            raise Exception("Events service not available")
        
        request = events_pb2.RegisterRequest(event_id=event_id, user_id=user_id)
        response = self.stub.RegisterForEvent(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }
    
    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Получить событие по ID"""
        if not self.stub:
            raise Exception("Events service not available")
        
        request = events_pb2.GetEventRequest(id=event_id)
        response = self.stub.GetEvent(request, timeout=10)
        
        if not response.event.id:
            return None
        
        return {
            'id': response.event.id,
            'title': response.event.title,
            'description': response.event.description,
            'type': response.event.type,
            'location': response.event.location,
            'start_time': response.event.start_time,
            'end_time': response.event.end_time,
            'max_participants': response.event.max_participants,
            'registered_count': response.event.registered_count,
            'created_by': response.event.created_by,
            'created_at': response.event.created_at
        }
    
    def get_registrations(self, event_id: int) -> List[Dict[str, Any]]:
        """Получить регистрации на событие"""
        if not self.stub:
            raise Exception("Events service not available")
        
        request = events_pb2.GetRegistrationsRequest(event_id=event_id)
        response = self.stub.GetRegistrations(request, timeout=10)
        
        registrations = []
        for reg in response.registrations:
            registrations.append({
                'id': reg.id,
                'event_id': reg.event_id,
                'user_id': reg.user_id,
                'user_name': reg.user_name,
                'registered_at': reg.registered_at
            })
        
        return registrations


_events_client: Optional[EventsClient] = None


def get_events_client() -> EventsClient:
    """Get singleton events client"""
    global _events_client
    if _events_client is None:
        _events_client = EventsClient()
    return _events_client

