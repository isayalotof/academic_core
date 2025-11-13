"""
Library RPC Client для Gateway
Подключение к ms-library
"""
import grpc
import logging
from typing import Optional, Dict, Any, List
import os

try:
    from rpc_clients.generated import library_pb2, library_pb2_grpc
except ImportError as e:
    logger_module = logging.getLogger(__name__)
    logger_module.error(f"Failed to import protobuf files: {e}")
    library_pb2 = None
    library_pb2_grpc = None

logger = logging.getLogger(__name__)


class LibraryClient:
    """RPC клиент для ms-library"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.getenv('MS_LIBRARY_HOST', 'localhost')
        self.port = port or int(os.getenv('MS_LIBRARY_PORT', 50058))
        self.address = f'{self.host}:{self.port}'
        
        self.channel = grpc.insecure_channel(
            self.address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ]
        )
        
        if library_pb2_grpc:
            self.stub = library_pb2_grpc.LibraryServiceStub(self.channel)
            logger.info(f"LibraryClient initialized: {self.address}")
        else:
            self.stub = None
            logger.warning("Proto files not available")
    
    def list_books(self, page: int = 1, page_size: int = 50,
                  author: Optional[str] = None,
                  category: Optional[str] = None,
                  search: Optional[str] = None) -> Dict[str, Any]:
        """Список книг"""
        if not self.stub:
            raise Exception("Library service not available")
        
        request = library_pb2.ListBooksRequest(
            page=page,
            page_size=page_size,
            author=author or '',
            category=category or '',
            search=search or ''
        )
        
        response = self.stub.ListBooks(request, timeout=10)
        
        books = []
        for book in response.books:
            books.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'category': book.category,
                'total_copies': book.total_copies,
                'available_copies': book.available_copies,
                'created_at': book.created_at
            })
        
        return {
            'books': books,
            'total_count': response.total_count
        }
    
    def reserve_book(self, book_id: int, user_id: int, days: int = 14) -> Dict[str, Any]:
        """Забронировать книгу"""
        if not self.stub:
            raise Exception("Library service not available")
        
        request = library_pb2.ReserveBookRequest(
            book_id=book_id,
            user_id=user_id,
            days=days
        )
        
        response = self.stub.ReserveBook(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message,
            'reservation_id': response.reservation_id
        }
    
    def get_book(self, book_id: int) -> Optional[Dict[str, Any]]:
        """Получить книгу по ID"""
        if not self.stub:
            raise Exception("Library service not available")
        
        request = library_pb2.GetBookRequest(id=book_id)
        response = self.stub.GetBook(request, timeout=10)
        
        if not response.book.id:
            return None
        
        return {
            'id': response.book.id,
            'title': response.book.title,
            'author': response.book.author,
            'isbn': response.book.isbn,
            'category': response.book.category,
            'total_copies': response.book.total_copies,
            'available_copies': response.book.available_copies,
            'created_at': response.book.created_at
        }
    
    def get_reservations(self, user_id: Optional[int] = None,
                        status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получить бронирования"""
        if not self.stub:
            raise Exception("Library service not available")
        
        request = library_pb2.GetReservationsRequest(
            user_id=user_id or 0,
            status=status or ''
        )
        
        response = self.stub.GetReservations(request, timeout=10)
        
        reservations = []
        for res in response.reservations:
            reservations.append({
                'id': res.id,
                'book_id': res.book_id,
                'user_id': res.user_id,
                'user_name': res.user_name,
                'status': res.status,
                'reserved_at': res.reserved_at,
                'due_date': res.due_date,
                'returned_at': res.returned_at
            })
        
        return reservations
    
    def return_book(self, reservation_id: int) -> Dict[str, Any]:
        """Вернуть книгу"""
        if not self.stub:
            raise Exception("Library service not available")
        
        request = library_pb2.ReturnBookRequest(reservation_id=reservation_id)
        response = self.stub.ReturnBook(request, timeout=10)
        
        return {
            'success': response.success,
            'message': response.message
        }


_library_client: Optional[LibraryClient] = None


def get_library_client() -> LibraryClient:
    """Get singleton library client"""
    global _library_client
    if _library_client is None:
        _library_client = LibraryClient()
    return _library_client

