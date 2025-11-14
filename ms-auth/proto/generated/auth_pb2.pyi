from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("id", "username", "email", "full_name", "phone", "primary_role", "roles", "teacher_id", "staff_id", "student_group_id", "is_active", "is_verified", "last_login_at", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_ROLE_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    STAFF_ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    email: str
    full_name: str
    phone: str
    primary_role: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    teacher_id: int
    staff_id: int
    student_group_id: int
    is_active: bool
    is_verified: bool
    last_login_at: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., email: _Optional[str] = ..., full_name: _Optional[str] = ..., phone: _Optional[str] = ..., primary_role: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ..., teacher_id: _Optional[int] = ..., staff_id: _Optional[int] = ..., student_group_id: _Optional[int] = ..., is_active: bool = ..., is_verified: bool = ..., last_login_at: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("id", "name", "code", "description", "permissions")
    class PermissionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    code: str
    description: str
    permissions: _containers.ScalarMap[str, bool]
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., permissions: _Optional[_Mapping[str, bool]] = ...) -> None: ...

class TokenPair(_message.Message):
    __slots__ = ("access_token", "refresh_token", "expires_in", "token_type")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    def __init__(self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., expires_in: _Optional[int] = ..., token_type: _Optional[str] = ...) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("username", "email", "password", "full_name", "phone", "primary_role", "teacher_id", "student_group_id")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_ROLE_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    username: str
    email: str
    password: str
    full_name: str
    phone: str
    primary_role: str
    teacher_id: int
    student_group_id: int
    def __init__(self, username: _Optional[str] = ..., email: _Optional[str] = ..., password: _Optional[str] = ..., full_name: _Optional[str] = ..., phone: _Optional[str] = ..., primary_role: _Optional[str] = ..., teacher_id: _Optional[int] = ..., student_group_id: _Optional[int] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("success", "user", "tokens", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    user: User
    tokens: TokenPair
    message: str
    def __init__(self, success: bool = ..., user: _Optional[_Union[User, _Mapping]] = ..., tokens: _Optional[_Union[TokenPair, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("username", "password", "ip_address", "user_agent", "device_id")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    ip_address: str
    user_agent: str
    device_id: str
    def __init__(self, username: _Optional[str] = ..., password: _Optional[str] = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("success", "user", "tokens", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    user: User
    tokens: TokenPair
    message: str
    def __init__(self, success: bool = ..., user: _Optional[_Union[User, _Mapping]] = ..., tokens: _Optional[_Union[TokenPair, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ("refresh_token", "user_id")
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    user_id: int
    def __init__(self, refresh_token: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RefreshTokenRequest(_message.Message):
    __slots__ = ("refresh_token", "ip_address", "user_agent")
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    ip_address: str
    user_agent: str
    def __init__(self, refresh_token: _Optional[str] = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ...) -> None: ...

class RefreshTokenResponse(_message.Message):
    __slots__ = ("success", "tokens", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    tokens: TokenPair
    message: str
    def __init__(self, success: bool = ..., tokens: _Optional[_Union[TokenPair, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class ValidateTokenRequest(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class ValidateTokenResponse(_message.Message):
    __slots__ = ("valid", "user_id", "username", "primary_role", "roles", "expires_at", "message")
    VALID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_ROLE_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    user_id: int
    username: str
    primary_role: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    expires_at: int
    message: str
    def __init__(self, valid: bool = ..., user_id: _Optional[int] = ..., username: _Optional[str] = ..., primary_role: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ..., expires_at: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class GetCurrentUserRequest(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class GetUserRequest(_message.Message):
    __slots__ = ("id", "username", "email")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    email: str
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...

class UserResponse(_message.Message):
    __slots__ = ("user", "message")
    USER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    user: User
    message: str
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("id", "full_name", "email", "phone", "is_active", "updated_by")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    id: int
    full_name: str
    email: str
    phone: str
    is_active: bool
    updated_by: int
    def __init__(self, id: _Optional[int] = ..., full_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., is_active: bool = ..., updated_by: _Optional[int] = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("id", "hard_delete")
    ID_FIELD_NUMBER: _ClassVar[int]
    HARD_DELETE_FIELD_NUMBER: _ClassVar[int]
    id: int
    hard_delete: bool
    def __init__(self, id: _Optional[int] = ..., hard_delete: bool = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ListUsersRequest(_message.Message):
    __slots__ = ("page", "page_size", "roles", "only_active", "search_query", "sort_by", "sort_order")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_QUERY_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    roles: _containers.RepeatedScalarFieldContainer[str]
    only_active: bool
    search_query: str
    sort_by: str
    sort_order: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., roles: _Optional[_Iterable[str]] = ..., only_active: bool = ..., search_query: _Optional[str] = ..., sort_by: _Optional[str] = ..., sort_order: _Optional[str] = ...) -> None: ...

class ListUsersResponse(_message.Message):
    __slots__ = ("users", "total_count", "page", "page_size")
    USERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    users: _containers.RepeatedCompositeFieldContainer[User]
    total_count: int
    page: int
    page_size: int
    def __init__(self, users: _Optional[_Iterable[_Union[User, _Mapping]]] = ..., total_count: _Optional[int] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class ChangePasswordRequest(_message.Message):
    __slots__ = ("user_id", "old_password", "new_password")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OLD_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    old_password: str
    new_password: str
    def __init__(self, user_id: _Optional[int] = ..., old_password: _Optional[str] = ..., new_password: _Optional[str] = ...) -> None: ...

class ChangePasswordResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class PasswordResetRequest(_message.Message):
    __slots__ = ("email", "ip_address")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    email: str
    ip_address: str
    def __init__(self, email: _Optional[str] = ..., ip_address: _Optional[str] = ...) -> None: ...

class PasswordResetResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ResetPasswordRequest(_message.Message):
    __slots__ = ("token", "new_password")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    token: str
    new_password: str
    def __init__(self, token: _Optional[str] = ..., new_password: _Optional[str] = ...) -> None: ...

class ResetPasswordResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class AssignRoleRequest(_message.Message):
    __slots__ = ("user_id", "role_code", "granted_by")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_CODE_FIELD_NUMBER: _ClassVar[int]
    GRANTED_BY_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    role_code: str
    granted_by: int
    def __init__(self, user_id: _Optional[int] = ..., role_code: _Optional[str] = ..., granted_by: _Optional[int] = ...) -> None: ...

class AssignRoleResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class RevokeRoleRequest(_message.Message):
    __slots__ = ("user_id", "role_code")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_CODE_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    role_code: str
    def __init__(self, user_id: _Optional[int] = ..., role_code: _Optional[str] = ...) -> None: ...

class RevokeRoleResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetUserRolesRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

class UserRolesResponse(_message.Message):
    __slots__ = ("roles",)
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, roles: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class LoginHistoryRequest(_message.Message):
    __slots__ = ("user_id", "limit", "only_successful")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ONLY_SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    limit: int
    only_successful: bool
    def __init__(self, user_id: _Optional[int] = ..., limit: _Optional[int] = ..., only_successful: bool = ...) -> None: ...

class LoginHistoryResponse(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[LoginHistoryEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[LoginHistoryEntry, _Mapping]]] = ...) -> None: ...

class LoginHistoryEntry(_message.Message):
    __slots__ = ("id", "username", "success", "ip_address", "user_agent", "failure_reason", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    username: str
    success: bool
    ip_address: str
    user_agent: str
    failure_reason: str
    created_at: str
    def __init__(self, id: _Optional[int] = ..., username: _Optional[str] = ..., success: bool = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ..., failure_reason: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: str
    version: str
    def __init__(self, status: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...
