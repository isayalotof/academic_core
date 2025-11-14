from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Book(_message.Message):
    __slots__ = ("id", "title", "author", "isbn", "category", "total_copies", "available_copies", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ISBN_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COPIES_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_COPIES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int
    available_copies: int
    created_at: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., author: _Optional[str] = ..., isbn: _Optional[str] = ..., category: _Optional[str] = ..., total_copies: _Optional[int] = ..., available_copies: _Optional[int] = ..., created_at: _Optional[str] = ...) -> None: ...

class Reservation(_message.Message):
    __slots__ = ("id", "book_id", "user_id", "user_name", "status", "reserved_at", "due_date", "returned_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESERVED_AT_FIELD_NUMBER: _ClassVar[int]
    DUE_DATE_FIELD_NUMBER: _ClassVar[int]
    RETURNED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    book_id: int
    user_id: int
    user_name: str
    status: str
    reserved_at: str
    due_date: str
    returned_at: str
    def __init__(self, id: _Optional[int] = ..., book_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., status: _Optional[str] = ..., reserved_at: _Optional[str] = ..., due_date: _Optional[str] = ..., returned_at: _Optional[str] = ...) -> None: ...

class AddBookRequest(_message.Message):
    __slots__ = ("title", "author", "isbn", "category", "total_copies")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    ISBN_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COPIES_FIELD_NUMBER: _ClassVar[int]
    title: str
    author: str
    isbn: str
    category: str
    total_copies: int
    def __init__(self, title: _Optional[str] = ..., author: _Optional[str] = ..., isbn: _Optional[str] = ..., category: _Optional[str] = ..., total_copies: _Optional[int] = ...) -> None: ...

class GetBookRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListBooksRequest(_message.Message):
    __slots__ = ("page", "page_size", "author", "category", "search")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    author: str
    category: str
    search: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., author: _Optional[str] = ..., category: _Optional[str] = ..., search: _Optional[str] = ...) -> None: ...

class ReserveBookRequest(_message.Message):
    __slots__ = ("book_id", "user_id", "days")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DAYS_FIELD_NUMBER: _ClassVar[int]
    book_id: int
    user_id: int
    days: int
    def __init__(self, book_id: _Optional[int] = ..., user_id: _Optional[int] = ..., days: _Optional[int] = ...) -> None: ...

class GetReservationsRequest(_message.Message):
    __slots__ = ("user_id", "status")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    status: str
    def __init__(self, user_id: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class ReturnBookRequest(_message.Message):
    __slots__ = ("reservation_id",)
    RESERVATION_ID_FIELD_NUMBER: _ClassVar[int]
    reservation_id: int
    def __init__(self, reservation_id: _Optional[int] = ...) -> None: ...

class BookResponse(_message.Message):
    __slots__ = ("book", "message")
    BOOK_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    book: Book
    message: str
    def __init__(self, book: _Optional[_Union[Book, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class BooksListResponse(_message.Message):
    __slots__ = ("books", "total_count")
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[Book]
    total_count: int
    def __init__(self, books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ReserveResponse(_message.Message):
    __slots__ = ("success", "message", "reservation_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RESERVATION_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    reservation_id: int
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., reservation_id: _Optional[int] = ...) -> None: ...

class ReservationsResponse(_message.Message):
    __slots__ = ("reservations", "total_count")
    RESERVATIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    reservations: _containers.RepeatedCompositeFieldContainer[Reservation]
    total_count: int
    def __init__(self, reservations: _Optional[_Iterable[_Union[Reservation, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ReturnResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "version", "timestamp")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    status: str
    version: str
    timestamp: str
    def __init__(self, status: _Optional[str] = ..., version: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...
