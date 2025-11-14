from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Event(_message.Message):
    __slots__ = ("id", "title", "description", "type", "location", "start_time", "end_time", "max_participants", "registered_count", "created_by", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    type: str
    location: str
    start_time: str
    end_time: str
    max_participants: int
    registered_count: int
    created_by: int
    created_at: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[str] = ..., location: _Optional[str] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., max_participants: _Optional[int] = ..., registered_count: _Optional[int] = ..., created_by: _Optional[int] = ..., created_at: _Optional[str] = ...) -> None: ...

class Registration(_message.Message):
    __slots__ = ("id", "event_id", "user_id", "user_name", "registered_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    event_id: int
    user_id: int
    user_name: str
    registered_at: str
    def __init__(self, id: _Optional[int] = ..., event_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_name: _Optional[str] = ..., registered_at: _Optional[str] = ...) -> None: ...

class CreateEventRequest(_message.Message):
    __slots__ = ("title", "description", "type", "location", "start_time", "end_time", "max_participants", "created_by")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    type: str
    location: str
    start_time: str
    end_time: str
    max_participants: int
    created_by: int
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[str] = ..., location: _Optional[str] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., max_participants: _Optional[int] = ..., created_by: _Optional[int] = ...) -> None: ...

class GetEventRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListEventsRequest(_message.Message):
    __slots__ = ("page", "page_size", "type", "start_date", "end_date")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    type: str
    start_date: str
    end_date: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., type: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("event_id", "user_id")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    event_id: int
    user_id: int
    def __init__(self, event_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class GetRegistrationsRequest(_message.Message):
    __slots__ = ("event_id",)
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    event_id: int
    def __init__(self, event_id: _Optional[int] = ...) -> None: ...

class EventResponse(_message.Message):
    __slots__ = ("event", "message")
    EVENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    event: Event
    message: str
    def __init__(self, event: _Optional[_Union[Event, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class EventsListResponse(_message.Message):
    __slots__ = ("events", "total_count")
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[Event]
    total_count: int
    def __init__(self, events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RegistrationsResponse(_message.Message):
    __slots__ = ("registrations", "total_count")
    REGISTRATIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    registrations: _containers.RepeatedCompositeFieldContainer[Registration]
    total_count: int
    def __init__(self, registrations: _Optional[_Iterable[_Union[Registration, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

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
