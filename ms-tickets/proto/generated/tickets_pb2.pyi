from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ticket(_message.Message):
    __slots__ = ("id", "title", "description", "category", "status", "created_by", "created_by_name", "assigned_to", "assigned_to_name", "priority", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_NAME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    category: str
    status: str
    created_by: int
    created_by_name: str
    assigned_to: int
    assigned_to_name: str
    priority: int
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., category: _Optional[str] = ..., status: _Optional[str] = ..., created_by: _Optional[int] = ..., created_by_name: _Optional[str] = ..., assigned_to: _Optional[int] = ..., assigned_to_name: _Optional[str] = ..., priority: _Optional[int] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Comment(_message.Message):
    __slots__ = ("id", "ticket_id", "user_id", "user_name", "content", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TICKET_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    ticket_id: int
    user_id: int
    user_name: str
    content: str
    created_at: str
    def __init__(self, id: _Optional[int] = ..., ticket_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., content: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class CreateTicketRequest(_message.Message):
    __slots__ = ("title", "description", "category", "created_by", "created_by_name", "priority")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_NAME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    category: str
    created_by: int
    created_by_name: str
    priority: int
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., category: _Optional[str] = ..., created_by: _Optional[int] = ..., created_by_name: _Optional[str] = ..., priority: _Optional[int] = ...) -> None: ...

class GetTicketRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class UpdateTicketRequest(_message.Message):
    __slots__ = ("id", "status", "assigned_to", "priority")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: str
    assigned_to: int
    priority: int
    def __init__(self, id: _Optional[int] = ..., status: _Optional[str] = ..., assigned_to: _Optional[int] = ..., priority: _Optional[int] = ...) -> None: ...

class ListTicketsRequest(_message.Message):
    __slots__ = ("page", "page_size", "created_by", "assigned_to", "status", "category")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    created_by: int
    assigned_to: int
    status: str
    category: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., created_by: _Optional[int] = ..., assigned_to: _Optional[int] = ..., status: _Optional[str] = ..., category: _Optional[str] = ...) -> None: ...

class AddCommentRequest(_message.Message):
    __slots__ = ("ticket_id", "user_id", "content")
    TICKET_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ticket_id: int
    user_id: int
    content: str
    def __init__(self, ticket_id: _Optional[int] = ..., user_id: _Optional[int] = ..., content: _Optional[str] = ...) -> None: ...

class ListCommentsRequest(_message.Message):
    __slots__ = ("ticket_id",)
    TICKET_ID_FIELD_NUMBER: _ClassVar[int]
    ticket_id: int
    def __init__(self, ticket_id: _Optional[int] = ...) -> None: ...

class TicketResponse(_message.Message):
    __slots__ = ("ticket", "message")
    TICKET_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ticket: Ticket
    message: str
    def __init__(self, ticket: _Optional[_Union[Ticket, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class TicketsListResponse(_message.Message):
    __slots__ = ("tickets", "total_count")
    TICKETS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    tickets: _containers.RepeatedCompositeFieldContainer[Ticket]
    total_count: int
    def __init__(self, tickets: _Optional[_Iterable[_Union[Ticket, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CommentResponse(_message.Message):
    __slots__ = ("comment", "message")
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    comment: Comment
    message: str
    def __init__(self, comment: _Optional[_Union[Comment, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class CommentsListResponse(_message.Message):
    __slots__ = ("comments", "total_count")
    COMMENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    comments: _containers.RepeatedCompositeFieldContainer[Comment]
    total_count: int
    def __init__(self, comments: _Optional[_Iterable[_Union[Comment, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

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
