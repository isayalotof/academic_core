from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DocumentRequest(_message.Message):
    __slots__ = ("id", "document_type", "purpose", "status", "requested_by", "requested_by_name", "requested_at", "processed_at", "file_path", "notes")
    ID_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_AT_FIELD_NUMBER: _ClassVar[int]
    PROCESSED_AT_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    id: int
    document_type: str
    purpose: str
    status: str
    requested_by: int
    requested_by_name: str
    requested_at: str
    processed_at: str
    file_path: str
    notes: str
    def __init__(self, id: _Optional[int] = ..., document_type: _Optional[str] = ..., purpose: _Optional[str] = ..., status: _Optional[str] = ..., requested_by: _Optional[int] = ..., requested_by_name: _Optional[str] = ..., requested_at: _Optional[str] = ..., processed_at: _Optional[str] = ..., file_path: _Optional[str] = ..., notes: _Optional[str] = ...) -> None: ...

class RequestDocumentRequest(_message.Message):
    __slots__ = ("document_type", "purpose", "requested_by", "notes")
    DOCUMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    document_type: str
    purpose: str
    requested_by: int
    notes: str
    def __init__(self, document_type: _Optional[str] = ..., purpose: _Optional[str] = ..., requested_by: _Optional[int] = ..., notes: _Optional[str] = ...) -> None: ...

class GetRequestRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListRequestsRequest(_message.Message):
    __slots__ = ("page", "page_size", "requested_by", "status", "document_type")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DOCUMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    requested_by: int
    status: str
    document_type: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., requested_by: _Optional[int] = ..., status: _Optional[str] = ..., document_type: _Optional[str] = ...) -> None: ...

class UpdateStatusRequest(_message.Message):
    __slots__ = ("id", "status", "file_path", "notes")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: str
    file_path: str
    notes: str
    def __init__(self, id: _Optional[int] = ..., status: _Optional[str] = ..., file_path: _Optional[str] = ..., notes: _Optional[str] = ...) -> None: ...

class DownloadRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DocumentRequestResponse(_message.Message):
    __slots__ = ("request", "message")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    request: DocumentRequest
    message: str
    def __init__(self, request: _Optional[_Union[DocumentRequest, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class RequestsListResponse(_message.Message):
    __slots__ = ("requests", "total_count")
    REQUESTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    requests: _containers.RepeatedCompositeFieldContainer[DocumentRequest]
    total_count: int
    def __init__(self, requests: _Optional[_Iterable[_Union[DocumentRequest, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class UpdateStatusResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DownloadResponse(_message.Message):
    __slots__ = ("success", "file_data", "file_name", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    file_data: bytes
    file_name: str
    message: str
    def __init__(self, success: bool = ..., file_data: _Optional[bytes] = ..., file_name: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

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
