from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Teacher(_message.Message):
    __slots__ = ("id", "full_name", "first_name", "last_name", "middle_name", "email", "phone", "employment_type", "priority", "position", "academic_degree", "department", "user_id", "is_active", "hire_date", "termination_date", "created_at", "updated_at", "preferences_info")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_DEGREE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    HIRE_DATE_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PREFERENCES_INFO_FIELD_NUMBER: _ClassVar[int]
    id: int
    full_name: str
    first_name: str
    last_name: str
    middle_name: str
    email: str
    phone: str
    employment_type: str
    priority: int
    position: str
    academic_degree: str
    department: str
    user_id: int
    is_active: bool
    hire_date: str
    termination_date: str
    created_at: str
    updated_at: str
    preferences_info: PreferencesInfo
    def __init__(self, id: _Optional[int] = ..., full_name: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., employment_type: _Optional[str] = ..., priority: _Optional[int] = ..., position: _Optional[str] = ..., academic_degree: _Optional[str] = ..., department: _Optional[str] = ..., user_id: _Optional[int] = ..., is_active: bool = ..., hire_date: _Optional[str] = ..., termination_date: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., preferences_info: _Optional[_Union[PreferencesInfo, _Mapping]] = ...) -> None: ...

class PreferencesInfo(_message.Message):
    __slots__ = ("total_preferences", "preferred_slots", "preferences_coverage")
    TOTAL_PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_SLOTS_FIELD_NUMBER: _ClassVar[int]
    PREFERENCES_COVERAGE_FIELD_NUMBER: _ClassVar[int]
    total_preferences: int
    preferred_slots: int
    preferences_coverage: float
    def __init__(self, total_preferences: _Optional[int] = ..., preferred_slots: _Optional[int] = ..., preferences_coverage: _Optional[float] = ...) -> None: ...

class TeacherPreference(_message.Message):
    __slots__ = ("id", "teacher_id", "day_of_week", "time_slot", "is_preferred", "preference_strength", "reason", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    IS_PREFERRED_FIELD_NUMBER: _ClassVar[int]
    PREFERENCE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    teacher_id: int
    day_of_week: int
    time_slot: int
    is_preferred: bool
    preference_strength: str
    reason: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., teacher_id: _Optional[int] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., is_preferred: bool = ..., preference_strength: _Optional[str] = ..., reason: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Group(_message.Message):
    __slots__ = ("id", "name", "short_name", "year", "semester", "size", "program_code", "program_name", "specialization", "level", "curator_teacher_id", "curator_name", "is_active", "enrollment_date", "graduation_date", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_CODE_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_NAME_FIELD_NUMBER: _ClassVar[int]
    SPECIALIZATION_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    CURATOR_TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    CURATOR_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    ENROLLMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    GRADUATION_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    short_name: str
    year: int
    semester: int
    size: int
    program_code: str
    program_name: str
    specialization: str
    level: str
    curator_teacher_id: int
    curator_name: str
    is_active: bool
    enrollment_date: str
    graduation_date: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., short_name: _Optional[str] = ..., year: _Optional[int] = ..., semester: _Optional[int] = ..., size: _Optional[int] = ..., program_code: _Optional[str] = ..., program_name: _Optional[str] = ..., specialization: _Optional[str] = ..., level: _Optional[str] = ..., curator_teacher_id: _Optional[int] = ..., curator_name: _Optional[str] = ..., is_active: bool = ..., enrollment_date: _Optional[str] = ..., graduation_date: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Student(_message.Message):
    __slots__ = ("id", "full_name", "first_name", "last_name", "middle_name", "student_number", "group_id", "group_name", "email", "phone", "user_id", "status", "enrollment_date", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    STUDENT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENROLLMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    full_name: str
    first_name: str
    last_name: str
    middle_name: str
    student_number: str
    group_id: int
    group_name: str
    email: str
    phone: str
    user_id: int
    status: str
    enrollment_date: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., full_name: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., student_number: _Optional[str] = ..., group_id: _Optional[int] = ..., group_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., user_id: _Optional[int] = ..., status: _Optional[str] = ..., enrollment_date: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Discipline(_message.Message):
    __slots__ = ("id", "name", "short_name", "code", "department", "credit_units", "discipline_type", "is_active", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    CREDIT_UNITS_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    short_name: str
    code: str
    department: str
    credit_units: int
    discipline_type: str
    is_active: bool
    created_at: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., short_name: _Optional[str] = ..., code: _Optional[str] = ..., department: _Optional[str] = ..., credit_units: _Optional[int] = ..., discipline_type: _Optional[str] = ..., is_active: bool = ..., created_at: _Optional[str] = ...) -> None: ...

class CourseLoad(_message.Message):
    __slots__ = ("id", "discipline_id", "discipline_name", "discipline_code", "teacher_id", "teacher_name", "teacher_priority", "group_id", "group_name", "group_size", "lesson_type", "hours_per_semester", "weeks_count", "lessons_per_week", "semester", "academic_year", "required_classroom_type", "min_classroom_capacity", "is_active", "source", "import_batch_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_ID_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_NAME_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_CODE_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    TEACHER_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_SIZE_FIELD_NUMBER: _ClassVar[int]
    LESSON_TYPE_FIELD_NUMBER: _ClassVar[int]
    HOURS_PER_SEMESTER_FIELD_NUMBER: _ClassVar[int]
    WEEKS_COUNT_FIELD_NUMBER: _ClassVar[int]
    LESSONS_PER_WEEK_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_CLASSROOM_TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_CLASSROOM_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    IMPORT_BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    discipline_id: int
    discipline_name: str
    discipline_code: str
    teacher_id: int
    teacher_name: str
    teacher_priority: int
    group_id: int
    group_name: str
    group_size: int
    lesson_type: str
    hours_per_semester: int
    weeks_count: int
    lessons_per_week: int
    semester: int
    academic_year: str
    required_classroom_type: str
    min_classroom_capacity: int
    is_active: bool
    source: str
    import_batch_id: str
    created_at: str
    def __init__(self, id: _Optional[int] = ..., discipline_id: _Optional[int] = ..., discipline_name: _Optional[str] = ..., discipline_code: _Optional[str] = ..., teacher_id: _Optional[int] = ..., teacher_name: _Optional[str] = ..., teacher_priority: _Optional[int] = ..., group_id: _Optional[int] = ..., group_name: _Optional[str] = ..., group_size: _Optional[int] = ..., lesson_type: _Optional[str] = ..., hours_per_semester: _Optional[int] = ..., weeks_count: _Optional[int] = ..., lessons_per_week: _Optional[int] = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., required_classroom_type: _Optional[str] = ..., min_classroom_capacity: _Optional[int] = ..., is_active: bool = ..., source: _Optional[str] = ..., import_batch_id: _Optional[str] = ..., created_at: _Optional[str] = ...) -> None: ...

class ImportBatch(_message.Message):
    __slots__ = ("id", "batch_id", "filename", "file_size", "semester", "academic_year", "total_rows", "successful_rows", "failed_rows", "errors", "status", "started_at", "completed_at", "imported_by_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_ROWS_FIELD_NUMBER: _ClassVar[int]
    FAILED_ROWS_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    IMPORTED_BY_NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    batch_id: str
    filename: str
    file_size: int
    semester: int
    academic_year: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    errors: _containers.RepeatedScalarFieldContainer[str]
    status: str
    started_at: str
    completed_at: str
    imported_by_name: str
    def __init__(self, id: _Optional[int] = ..., batch_id: _Optional[str] = ..., filename: _Optional[str] = ..., file_size: _Optional[int] = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., total_rows: _Optional[int] = ..., successful_rows: _Optional[int] = ..., failed_rows: _Optional[int] = ..., errors: _Optional[_Iterable[str]] = ..., status: _Optional[str] = ..., started_at: _Optional[str] = ..., completed_at: _Optional[str] = ..., imported_by_name: _Optional[str] = ...) -> None: ...

class CreateTeacherRequest(_message.Message):
    __slots__ = ("full_name", "first_name", "last_name", "middle_name", "email", "phone", "employment_type", "position", "academic_degree", "department", "hire_date", "created_by")
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_DEGREE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    HIRE_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    full_name: str
    first_name: str
    last_name: str
    middle_name: str
    email: str
    phone: str
    employment_type: str
    position: str
    academic_degree: str
    department: str
    hire_date: str
    created_by: int
    def __init__(self, full_name: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., employment_type: _Optional[str] = ..., position: _Optional[str] = ..., academic_degree: _Optional[str] = ..., department: _Optional[str] = ..., hire_date: _Optional[str] = ..., created_by: _Optional[int] = ...) -> None: ...

class GetTeacherRequest(_message.Message):
    __slots__ = ("id", "email", "user_id", "include_preferences")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    id: int
    email: str
    user_id: int
    include_preferences: bool
    def __init__(self, id: _Optional[int] = ..., email: _Optional[str] = ..., user_id: _Optional[int] = ..., include_preferences: bool = ...) -> None: ...

class UpdateTeacherRequest(_message.Message):
    __slots__ = ("id", "full_name", "email", "phone", "employment_type", "position", "department", "is_active", "updated_by")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    EMPLOYMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    id: int
    full_name: str
    email: str
    phone: str
    employment_type: str
    position: str
    department: str
    is_active: bool
    updated_by: int
    def __init__(self, id: _Optional[int] = ..., full_name: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., employment_type: _Optional[str] = ..., position: _Optional[str] = ..., department: _Optional[str] = ..., is_active: bool = ..., updated_by: _Optional[int] = ...) -> None: ...

class DeleteTeacherRequest(_message.Message):
    __slots__ = ("id", "hard_delete")
    ID_FIELD_NUMBER: _ClassVar[int]
    HARD_DELETE_FIELD_NUMBER: _ClassVar[int]
    id: int
    hard_delete: bool
    def __init__(self, id: _Optional[int] = ..., hard_delete: bool = ...) -> None: ...

class ListTeachersRequest(_message.Message):
    __slots__ = ("page", "page_size", "employment_types", "priorities", "department", "only_active", "sort_by", "sort_order")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    EMPLOYMENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    PRIORITIES_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    employment_types: _containers.RepeatedScalarFieldContainer[str]
    priorities: _containers.RepeatedScalarFieldContainer[int]
    department: str
    only_active: bool
    sort_by: str
    sort_order: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., employment_types: _Optional[_Iterable[str]] = ..., priorities: _Optional[_Iterable[int]] = ..., department: _Optional[str] = ..., only_active: bool = ..., sort_by: _Optional[str] = ..., sort_order: _Optional[str] = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ("query", "limit")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    query: str
    limit: int
    def __init__(self, query: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class TeacherResponse(_message.Message):
    __slots__ = ("teacher", "message")
    TEACHER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    teacher: Teacher
    message: str
    def __init__(self, teacher: _Optional[_Union[Teacher, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class TeachersListResponse(_message.Message):
    __slots__ = ("teachers", "total_count", "page", "page_size")
    TEACHERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    teachers: _containers.RepeatedCompositeFieldContainer[Teacher]
    total_count: int
    page: int
    page_size: int
    def __init__(self, teachers: _Optional[_Iterable[_Union[Teacher, _Mapping]]] = ..., total_count: _Optional[int] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class GetPreferencesRequest(_message.Message):
    __slots__ = ("teacher_id",)
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    def __init__(self, teacher_id: _Optional[int] = ...) -> None: ...

class PreferencesResponse(_message.Message):
    __slots__ = ("teacher_id", "teacher_name", "teacher_priority", "preferences", "total_preferences", "preferred_count", "not_preferred_count", "coverage_percentage")
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    TEACHER_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_COUNT_FIELD_NUMBER: _ClassVar[int]
    NOT_PREFERRED_COUNT_FIELD_NUMBER: _ClassVar[int]
    COVERAGE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    teacher_name: str
    teacher_priority: int
    preferences: _containers.RepeatedCompositeFieldContainer[TeacherPreference]
    total_preferences: int
    preferred_count: int
    not_preferred_count: int
    coverage_percentage: float
    def __init__(self, teacher_id: _Optional[int] = ..., teacher_name: _Optional[str] = ..., teacher_priority: _Optional[int] = ..., preferences: _Optional[_Iterable[_Union[TeacherPreference, _Mapping]]] = ..., total_preferences: _Optional[int] = ..., preferred_count: _Optional[int] = ..., not_preferred_count: _Optional[int] = ..., coverage_percentage: _Optional[float] = ...) -> None: ...

class SetPreferencesRequest(_message.Message):
    __slots__ = ("teacher_id", "preferences", "replace_existing")
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    REPLACE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    preferences: _containers.RepeatedCompositeFieldContainer[PreferenceItem]
    replace_existing: bool
    def __init__(self, teacher_id: _Optional[int] = ..., preferences: _Optional[_Iterable[_Union[PreferenceItem, _Mapping]]] = ..., replace_existing: bool = ...) -> None: ...

class PreferenceItem(_message.Message):
    __slots__ = ("day_of_week", "time_slot", "is_preferred", "preference_strength", "reason")
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    IS_PREFERRED_FIELD_NUMBER: _ClassVar[int]
    PREFERENCE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    day_of_week: int
    time_slot: int
    is_preferred: bool
    preference_strength: str
    reason: str
    def __init__(self, day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., is_preferred: bool = ..., preference_strength: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class SetPreferencesResponse(_message.Message):
    __slots__ = ("success", "created_count", "updated_count", "deleted_count", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CREATED_COUNT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_COUNT_FIELD_NUMBER: _ClassVar[int]
    DELETED_COUNT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    created_count: int
    updated_count: int
    deleted_count: int
    message: str
    def __init__(self, success: bool = ..., created_count: _Optional[int] = ..., updated_count: _Optional[int] = ..., deleted_count: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class UpdatePreferenceRequest(_message.Message):
    __slots__ = ("teacher_id", "day_of_week", "time_slot", "is_preferred", "preference_strength", "reason")
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    IS_PREFERRED_FIELD_NUMBER: _ClassVar[int]
    PREFERENCE_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    day_of_week: int
    time_slot: int
    is_preferred: bool
    preference_strength: str
    reason: str
    def __init__(self, teacher_id: _Optional[int] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., is_preferred: bool = ..., preference_strength: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class PreferenceResponse(_message.Message):
    __slots__ = ("preference", "message")
    PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    preference: TeacherPreference
    message: str
    def __init__(self, preference: _Optional[_Union[TeacherPreference, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class ClearPreferencesRequest(_message.Message):
    __slots__ = ("teacher_id",)
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    def __init__(self, teacher_id: _Optional[int] = ...) -> None: ...

class ClearResponse(_message.Message):
    __slots__ = ("success", "deleted_count")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    DELETED_COUNT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    deleted_count: int
    def __init__(self, success: bool = ..., deleted_count: _Optional[int] = ...) -> None: ...

class GetAllPreferencesRequest(_message.Message):
    __slots__ = ("semester", "academic_year", "teacher_ids")
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    TEACHER_IDS_FIELD_NUMBER: _ClassVar[int]
    semester: int
    academic_year: str
    teacher_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., teacher_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class AllPreferencesResponse(_message.Message):
    __slots__ = ("preferences_sets",)
    PREFERENCES_SETS_FIELD_NUMBER: _ClassVar[int]
    preferences_sets: _containers.RepeatedCompositeFieldContainer[TeacherPreferencesSet]
    def __init__(self, preferences_sets: _Optional[_Iterable[_Union[TeacherPreferencesSet, _Mapping]]] = ...) -> None: ...

class TeacherPreferencesSet(_message.Message):
    __slots__ = ("teacher_id", "teacher_name", "teacher_priority", "preferences")
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    TEACHER_PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    teacher_name: str
    teacher_priority: int
    preferences: _containers.RepeatedCompositeFieldContainer[TeacherPreference]
    def __init__(self, teacher_id: _Optional[int] = ..., teacher_name: _Optional[str] = ..., teacher_priority: _Optional[int] = ..., preferences: _Optional[_Iterable[_Union[TeacherPreference, _Mapping]]] = ...) -> None: ...

class CreateGroupRequest(_message.Message):
    __slots__ = ("name", "short_name", "year", "semester", "program_code", "program_name", "specialization", "level", "curator_teacher_id", "enrollment_date")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_CODE_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_NAME_FIELD_NUMBER: _ClassVar[int]
    SPECIALIZATION_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    CURATOR_TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    ENROLLMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    short_name: str
    year: int
    semester: int
    program_code: str
    program_name: str
    specialization: str
    level: str
    curator_teacher_id: int
    enrollment_date: str
    def __init__(self, name: _Optional[str] = ..., short_name: _Optional[str] = ..., year: _Optional[int] = ..., semester: _Optional[int] = ..., program_code: _Optional[str] = ..., program_name: _Optional[str] = ..., specialization: _Optional[str] = ..., level: _Optional[str] = ..., curator_teacher_id: _Optional[int] = ..., enrollment_date: _Optional[str] = ...) -> None: ...

class GetGroupRequest(_message.Message):
    __slots__ = ("id", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class UpdateGroupRequest(_message.Message):
    __slots__ = ("id", "name", "semester", "curator_teacher_id", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    CURATOR_TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    semester: int
    curator_teacher_id: int
    is_active: bool
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., semester: _Optional[int] = ..., curator_teacher_id: _Optional[int] = ..., is_active: bool = ...) -> None: ...

class DeleteGroupRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListGroupsRequest(_message.Message):
    __slots__ = ("page", "page_size", "year", "level", "only_active", "sort_by")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    year: int
    level: str
    only_active: bool
    sort_by: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., year: _Optional[int] = ..., level: _Optional[str] = ..., only_active: bool = ..., sort_by: _Optional[str] = ...) -> None: ...

class GroupResponse(_message.Message):
    __slots__ = ("group", "message")
    GROUP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    group: Group
    message: str
    def __init__(self, group: _Optional[_Union[Group, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class GroupsListResponse(_message.Message):
    __slots__ = ("groups", "total_count")
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[Group]
    total_count: int
    def __init__(self, groups: _Optional[_Iterable[_Union[Group, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateStudentRequest(_message.Message):
    __slots__ = ("full_name", "first_name", "last_name", "middle_name", "student_number", "group_id", "email", "phone", "enrollment_date")
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    STUDENT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ENROLLMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    full_name: str
    first_name: str
    last_name: str
    middle_name: str
    student_number: str
    group_id: int
    email: str
    phone: str
    enrollment_date: str
    def __init__(self, full_name: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., student_number: _Optional[str] = ..., group_id: _Optional[int] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., enrollment_date: _Optional[str] = ...) -> None: ...

class GetStudentRequest(_message.Message):
    __slots__ = ("id", "student_number", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    STUDENT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    student_number: str
    user_id: int
    def __init__(self, id: _Optional[int] = ..., student_number: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class UpdateStudentRequest(_message.Message):
    __slots__ = ("id", "full_name", "group_id", "email", "phone", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    FULL_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    full_name: str
    group_id: int
    email: str
    phone: str
    status: str
    def __init__(self, id: _Optional[int] = ..., full_name: _Optional[str] = ..., group_id: _Optional[int] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class DeleteStudentRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListStudentsRequest(_message.Message):
    __slots__ = ("page", "page_size", "group_id", "status", "sort_by")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    group_id: int
    status: str
    sort_by: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., group_id: _Optional[int] = ..., status: _Optional[str] = ..., sort_by: _Optional[str] = ...) -> None: ...

class GroupStudentsRequest(_message.Message):
    __slots__ = ("group_id", "status")
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    group_id: int
    status: str
    def __init__(self, group_id: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class StudentResponse(_message.Message):
    __slots__ = ("student", "message")
    STUDENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    student: Student
    message: str
    def __init__(self, student: _Optional[_Union[Student, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class StudentsListResponse(_message.Message):
    __slots__ = ("students", "total_count")
    STUDENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    students: _containers.RepeatedCompositeFieldContainer[Student]
    total_count: int
    def __init__(self, students: _Optional[_Iterable[_Union[Student, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateDisciplineRequest(_message.Message):
    __slots__ = ("name", "short_name", "code", "department", "credit_units", "discipline_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    CREDIT_UNITS_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    short_name: str
    code: str
    department: str
    credit_units: int
    discipline_type: str
    def __init__(self, name: _Optional[str] = ..., short_name: _Optional[str] = ..., code: _Optional[str] = ..., department: _Optional[str] = ..., credit_units: _Optional[int] = ..., discipline_type: _Optional[str] = ...) -> None: ...

class GetDisciplineRequest(_message.Message):
    __slots__ = ("id", "code", "name")
    ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    id: int
    code: str
    name: str
    def __init__(self, id: _Optional[int] = ..., code: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class ListDisciplinesRequest(_message.Message):
    __slots__ = ("page", "page_size", "department", "only_active")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    department: str
    only_active: bool
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., department: _Optional[str] = ..., only_active: bool = ...) -> None: ...

class DisciplineResponse(_message.Message):
    __slots__ = ("discipline", "message")
    DISCIPLINE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    discipline: Discipline
    message: str
    def __init__(self, discipline: _Optional[_Union[Discipline, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class DisciplinesListResponse(_message.Message):
    __slots__ = ("disciplines", "total_count")
    DISCIPLINES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    disciplines: _containers.RepeatedCompositeFieldContainer[Discipline]
    total_count: int
    def __init__(self, disciplines: _Optional[_Iterable[_Union[Discipline, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateCourseLoadRequest(_message.Message):
    __slots__ = ("discipline_name", "discipline_code", "discipline_id", "teacher_id", "group_id", "lesson_type", "hours_per_semester", "weeks_count", "semester", "academic_year", "required_classroom_type", "min_classroom_capacity")
    DISCIPLINE_NAME_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_CODE_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    LESSON_TYPE_FIELD_NUMBER: _ClassVar[int]
    HOURS_PER_SEMESTER_FIELD_NUMBER: _ClassVar[int]
    WEEKS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_CLASSROOM_TYPE_FIELD_NUMBER: _ClassVar[int]
    MIN_CLASSROOM_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    discipline_name: str
    discipline_code: str
    discipline_id: int
    teacher_id: int
    group_id: int
    lesson_type: str
    hours_per_semester: int
    weeks_count: int
    semester: int
    academic_year: str
    required_classroom_type: str
    min_classroom_capacity: int
    def __init__(self, discipline_name: _Optional[str] = ..., discipline_code: _Optional[str] = ..., discipline_id: _Optional[int] = ..., teacher_id: _Optional[int] = ..., group_id: _Optional[int] = ..., lesson_type: _Optional[str] = ..., hours_per_semester: _Optional[int] = ..., weeks_count: _Optional[int] = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., required_classroom_type: _Optional[str] = ..., min_classroom_capacity: _Optional[int] = ...) -> None: ...

class GetCourseLoadRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class ListCourseLoadsRequest(_message.Message):
    __slots__ = ("page", "page_size", "semester", "academic_year", "teacher_ids", "group_ids", "lesson_types", "only_active")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    TEACHER_IDS_FIELD_NUMBER: _ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    LESSON_TYPES_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    semester: int
    academic_year: str
    teacher_ids: _containers.RepeatedScalarFieldContainer[int]
    group_ids: _containers.RepeatedScalarFieldContainer[int]
    lesson_types: _containers.RepeatedScalarFieldContainer[str]
    only_active: bool
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., teacher_ids: _Optional[_Iterable[int]] = ..., group_ids: _Optional[_Iterable[int]] = ..., lesson_types: _Optional[_Iterable[str]] = ..., only_active: bool = ...) -> None: ...

class DeleteCourseLoadRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class CourseLoadResponse(_message.Message):
    __slots__ = ("course_load", "message")
    COURSE_LOAD_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    course_load: CourseLoad
    message: str
    def __init__(self, course_load: _Optional[_Union[CourseLoad, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class CourseLoadsListResponse(_message.Message):
    __slots__ = ("course_loads", "total_count")
    COURSE_LOADS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    course_loads: _containers.RepeatedCompositeFieldContainer[CourseLoad]
    total_count: int
    def __init__(self, course_loads: _Optional[_Iterable[_Union[CourseLoad, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class ImportRequest(_message.Message):
    __slots__ = ("file_data", "filename", "semester", "academic_year", "validate_only", "imported_by")
    FILE_DATA_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    IMPORTED_BY_FIELD_NUMBER: _ClassVar[int]
    file_data: bytes
    filename: str
    semester: int
    academic_year: str
    validate_only: bool
    imported_by: int
    def __init__(self, file_data: _Optional[bytes] = ..., filename: _Optional[str] = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., validate_only: bool = ..., imported_by: _Optional[int] = ...) -> None: ...

class ImportResponse(_message.Message):
    __slots__ = ("success", "batch_id", "total_rows", "successful_rows", "failed_rows", "errors", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_ROWS_FIELD_NUMBER: _ClassVar[int]
    FAILED_ROWS_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    batch_id: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    errors: _containers.RepeatedScalarFieldContainer[str]
    message: str
    def __init__(self, success: bool = ..., batch_id: _Optional[str] = ..., total_rows: _Optional[int] = ..., successful_rows: _Optional[int] = ..., failed_rows: _Optional[int] = ..., errors: _Optional[_Iterable[str]] = ..., message: _Optional[str] = ...) -> None: ...

class ImportStatusRequest(_message.Message):
    __slots__ = ("batch_id",)
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    def __init__(self, batch_id: _Optional[str] = ...) -> None: ...

class ImportStatusResponse(_message.Message):
    __slots__ = ("batch",)
    BATCH_FIELD_NUMBER: _ClassVar[int]
    batch: ImportBatch
    def __init__(self, batch: _Optional[_Union[ImportBatch, _Mapping]] = ...) -> None: ...

class ImportBatchesRequest(_message.Message):
    __slots__ = ("limit", "status")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    limit: int
    status: str
    def __init__(self, limit: _Optional[int] = ..., status: _Optional[str] = ...) -> None: ...

class ImportBatchesResponse(_message.Message):
    __slots__ = ("batches",)
    BATCHES_FIELD_NUMBER: _ClassVar[int]
    batches: _containers.RepeatedCompositeFieldContainer[ImportBatch]
    def __init__(self, batches: _Optional[_Iterable[_Union[ImportBatch, _Mapping]]] = ...) -> None: ...

class LinkRequest(_message.Message):
    __slots__ = ("entity_id", "user_id")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    user_id: int
    def __init__(self, entity_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class LinkResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class UserIdRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    def __init__(self, user_id: _Optional[int] = ...) -> None: ...

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
