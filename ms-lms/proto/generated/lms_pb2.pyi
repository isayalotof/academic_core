from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Course(_message.Message):
    __slots__ = ("id", "title", "description", "code", "teacher_id", "teacher_name", "status", "enrolled_count", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENROLLED_COUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    code: str
    teacher_id: int
    teacher_name: str
    status: str
    enrolled_count: int
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., code: _Optional[str] = ..., teacher_id: _Optional[int] = ..., teacher_name: _Optional[str] = ..., status: _Optional[str] = ..., enrolled_count: _Optional[int] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Module(_message.Message):
    __slots__ = ("id", "course_id", "title", "description", "order", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    course_id: int
    title: str
    description: str
    order: int
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., course_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., order: _Optional[int] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Material(_message.Message):
    __slots__ = ("id", "module_id", "title", "type", "content", "file_path", "order", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    module_id: int
    title: str
    type: str
    content: str
    file_path: str
    order: int
    created_at: str
    def __init__(self, id: _Optional[int] = ..., module_id: _Optional[int] = ..., title: _Optional[str] = ..., type: _Optional[str] = ..., content: _Optional[str] = ..., file_path: _Optional[str] = ..., order: _Optional[int] = ..., created_at: _Optional[str] = ...) -> None: ...

class Progress(_message.Message):
    __slots__ = ("id", "student_id", "course_id", "module_id", "completed", "progress_percentage", "completed_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    student_id: int
    course_id: int
    module_id: int
    completed: bool
    progress_percentage: float
    completed_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., student_id: _Optional[int] = ..., course_id: _Optional[int] = ..., module_id: _Optional[int] = ..., completed: bool = ..., progress_percentage: _Optional[float] = ..., completed_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class CreateCourseRequest(_message.Message):
    __slots__ = ("title", "description", "code", "teacher_id", "status")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    title: str
    description: str
    code: str
    teacher_id: int
    status: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., code: _Optional[str] = ..., teacher_id: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class GetCourseRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class UpdateCourseRequest(_message.Message):
    __slots__ = ("id", "title", "description", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    status: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class DeleteCourseRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListCoursesRequest(_message.Message):
    __slots__ = ("page", "page_size", "teacher_id", "status")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    teacher_id: int
    status: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., teacher_id: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class EnrollRequest(_message.Message):
    __slots__ = ("course_id", "student_id")
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    course_id: int
    student_id: int
    def __init__(self, course_id: _Optional[int] = ..., student_id: _Optional[int] = ...) -> None: ...

class EnrollResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class CreateModuleRequest(_message.Message):
    __slots__ = ("course_id", "title", "description", "order")
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    course_id: int
    title: str
    description: str
    order: int
    def __init__(self, course_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., order: _Optional[int] = ...) -> None: ...

class GetModuleRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class UpdateModuleRequest(_message.Message):
    __slots__ = ("id", "title", "description", "order")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    description: str
    order: int
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., order: _Optional[int] = ...) -> None: ...

class DeleteModuleRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListModulesRequest(_message.Message):
    __slots__ = ("course_id",)
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    course_id: int
    def __init__(self, course_id: _Optional[int] = ...) -> None: ...

class AddMaterialRequest(_message.Message):
    __slots__ = ("module_id", "title", "type", "content", "file_path", "order")
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    module_id: int
    title: str
    type: str
    content: str
    file_path: str
    order: int
    def __init__(self, module_id: _Optional[int] = ..., title: _Optional[str] = ..., type: _Optional[str] = ..., content: _Optional[str] = ..., file_path: _Optional[str] = ..., order: _Optional[int] = ...) -> None: ...

class GetMaterialRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class DeleteMaterialRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListMaterialsRequest(_message.Message):
    __slots__ = ("module_id",)
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    module_id: int
    def __init__(self, module_id: _Optional[int] = ...) -> None: ...

class GetProgressRequest(_message.Message):
    __slots__ = ("student_id", "course_id")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    student_id: int
    course_id: int
    def __init__(self, student_id: _Optional[int] = ..., course_id: _Optional[int] = ...) -> None: ...

class UpdateProgressRequest(_message.Message):
    __slots__ = ("student_id", "course_id", "module_id", "completed")
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    COURSE_ID_FIELD_NUMBER: _ClassVar[int]
    MODULE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_FIELD_NUMBER: _ClassVar[int]
    student_id: int
    course_id: int
    module_id: int
    completed: bool
    def __init__(self, student_id: _Optional[int] = ..., course_id: _Optional[int] = ..., module_id: _Optional[int] = ..., completed: bool = ...) -> None: ...

class GetStudentCoursesRequest(_message.Message):
    __slots__ = ("student_id",)
    STUDENT_ID_FIELD_NUMBER: _ClassVar[int]
    student_id: int
    def __init__(self, student_id: _Optional[int] = ...) -> None: ...

class CourseResponse(_message.Message):
    __slots__ = ("course", "message")
    COURSE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    course: Course
    message: str
    def __init__(self, course: _Optional[_Union[Course, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class CoursesListResponse(_message.Message):
    __slots__ = ("courses", "total_count")
    COURSES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    courses: _containers.RepeatedCompositeFieldContainer[Course]
    total_count: int
    def __init__(self, courses: _Optional[_Iterable[_Union[Course, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ModuleResponse(_message.Message):
    __slots__ = ("module", "message")
    MODULE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    module: Module
    message: str
    def __init__(self, module: _Optional[_Union[Module, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class ModulesListResponse(_message.Message):
    __slots__ = ("modules", "total_count")
    MODULES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    modules: _containers.RepeatedCompositeFieldContainer[Module]
    total_count: int
    def __init__(self, modules: _Optional[_Iterable[_Union[Module, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class MaterialResponse(_message.Message):
    __slots__ = ("material", "message")
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    material: Material
    message: str
    def __init__(self, material: _Optional[_Union[Material, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class MaterialsListResponse(_message.Message):
    __slots__ = ("materials", "total_count")
    MATERIALS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    materials: _containers.RepeatedCompositeFieldContainer[Material]
    total_count: int
    def __init__(self, materials: _Optional[_Iterable[_Union[Material, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ProgressResponse(_message.Message):
    __slots__ = ("progress", "overall_progress", "message")
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    OVERALL_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    progress: Progress
    overall_progress: float
    message: str
    def __init__(self, progress: _Optional[_Union[Progress, _Mapping]] = ..., overall_progress: _Optional[float] = ..., message: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
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
