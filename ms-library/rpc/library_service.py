"""
gRPC service implementation for ms-library
"""
import logging
from datetime import datetime, timedelta
import grpc
from proto.generated import library_pb2, library_pb2_grpc
from services.book_service import BookService

logger = logging.getLogger(__name__)


class LibraryServicer(library_pb2_grpc.LibraryServiceServicer):
    def __init__(self):
        self.book_service = BookService()
    
    def HealthCheck(self, request, context):
        return library_pb2.HealthCheckResponse(
            status='healthy', version='1.0.0',
            timestamp=datetime.utcnow().isoformat() + 'Z'
        )
    
    def AddBook(self, request, context):
        try:
            book = self.book_service.add_book(
                title=request.title, author=request.author,
                isbn=request.isbn, category=request.category,
                total_copies=request.total_copies
            )
            return library_pb2.BookResponse(book=book, message="Book added successfully")
        except Exception as e:
            logger.error(f"AddBook error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.BookResponse()
    
    def ListBooks(self, request, context):
        try:
            books, total = self.book_service.list_books(
                page=request.page or 1, page_size=request.page_size or 50,
                author=request.author if request.author else None,
                category=request.category if request.category else None,
                search=request.search if request.search else None
            )
            return library_pb2.BooksListResponse(books=books, total_count=total)
        except Exception as e:
            logger.error(f"ListBooks error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.BooksListResponse()
    
    def ReserveBook(self, request, context):
        try:
            reservation_id = self.book_service.reserve_book(
                book_id=request.book_id, user_id=request.user_id,
                days=request.days or 14
            )
            return library_pb2.ReserveResponse(
                success=reservation_id is not None,
                message="Book reserved successfully" if reservation_id else "Book not available",
                reservation_id=reservation_id or 0
            )
        except Exception as e:
            logger.error(f"ReserveBook error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ReserveResponse(success=False, message=str(e))
    
    def GetBook(self, request, context):
        try:
            book = self.book_service.get_book(request.id)
            if not book:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Book {request.id} not found")
                return library_pb2.BookResponse()
            return library_pb2.BookResponse(book=book)
        except Exception as e:
            logger.error(f"GetBook error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.BookResponse()
    
    def GetReservations(self, request, context):
        try:
            reservations = self.book_service.get_reservations(
                user_id=request.user_id if request.user_id else None,
                status=request.status if request.status else None
            )
            return library_pb2.ReservationsResponse(reservations=reservations, total_count=len(reservations))
        except Exception as e:
            logger.error(f"GetReservations error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ReservationsResponse()
    
    def ReturnBook(self, request, context):
        try:
            success = self.book_service.return_book(request.reservation_id)
            return library_pb2.ReturnResponse(
                success=success,
                message="Book returned successfully" if success else "Reservation not found or already returned"
            )
        except Exception as e:
            logger.error(f"ReturnBook error: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return library_pb2.ReturnResponse(success=False, message=str(e))

