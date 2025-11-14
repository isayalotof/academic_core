from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Classroom(_message.Message):
    __slots__ = ("id", "name", "code", "building_id", "building_name", "floor", "wing", "capacity", "actual_area", "classroom_type", "has_projector", "has_whiteboard", "has_blackboard", "has_markers", "has_chalk", "has_computers", "computers_count", "has_audio_system", "has_video_recording", "has_air_conditioning", "is_accessible", "has_windows", "is_active", "description", "notes", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    BUILDING_ID_FIELD_NUMBER: _ClassVar[int]
    BUILDING_NAME_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    WING_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_AREA_FIELD_NUMBER: _ClassVar[int]
    CLASSROOM_TYPE_FIELD_NUMBER: _ClassVar[int]
    HAS_PROJECTOR_FIELD_NUMBER: _ClassVar[int]
    HAS_WHITEBOARD_FIELD_NUMBER: _ClassVar[int]
    HAS_BLACKBOARD_FIELD_NUMBER: _ClassVar[int]
    HAS_MARKERS_FIELD_NUMBER: _ClassVar[int]
    HAS_CHALK_FIELD_NUMBER: _ClassVar[int]
    HAS_COMPUTERS_FIELD_NUMBER: _ClassVar[int]
    COMPUTERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    HAS_AUDIO_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    HAS_VIDEO_RECORDING_FIELD_NUMBER: _ClassVar[int]
    HAS_AIR_CONDITIONING_FIELD_NUMBER: _ClassVar[int]
    IS_ACCESSIBLE_FIELD_NUMBER: _ClassVar[int]
    HAS_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    code: str
    building_id: int
    building_name: str
    floor: int
    wing: str
    capacity: int
    actual_area: float
    classroom_type: str
    has_projector: bool
    has_whiteboard: bool
    has_blackboard: bool
    has_markers: bool
    has_chalk: bool
    has_computers: bool
    computers_count: int
    has_audio_system: bool
    has_video_recording: bool
    has_air_conditioning: bool
    is_accessible: bool
    has_windows: bool
    is_active: bool
    description: str
    notes: str
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., building_id: _Optional[int] = ..., building_name: _Optional[str] = ..., floor: _Optional[int] = ..., wing: _Optional[str] = ..., capacity: _Optional[int] = ..., actual_area: _Optional[float] = ..., classroom_type: _Optional[str] = ..., has_projector: bool = ..., has_whiteboard: bool = ..., has_blackboard: bool = ..., has_markers: bool = ..., has_chalk: bool = ..., has_computers: bool = ..., computers_count: _Optional[int] = ..., has_audio_system: bool = ..., has_video_recording: bool = ..., has_air_conditioning: bool = ..., is_accessible: bool = ..., has_windows: bool = ..., is_active: bool = ..., description: _Optional[str] = ..., notes: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class Building(_message.Message):
    __slots__ = ("id", "name", "short_name", "code", "address", "campus", "latitude", "longitude", "total_floors", "has_elevator", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FLOORS_FIELD_NUMBER: _ClassVar[int]
    HAS_ELEVATOR_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    short_name: str
    code: str
    address: str
    campus: str
    latitude: float
    longitude: float
    total_floors: int
    has_elevator: bool
    created_at: str
    updated_at: str
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., short_name: _Optional[str] = ..., code: _Optional[str] = ..., address: _Optional[str] = ..., campus: _Optional[str] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., total_floors: _Optional[int] = ..., has_elevator: bool = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ...) -> None: ...

class CreateClassroomRequest(_message.Message):
    __slots__ = ("name", "code", "building_id", "floor", "wing", "capacity", "actual_area", "classroom_type", "has_projector", "has_whiteboard", "has_blackboard", "has_markers", "has_chalk", "has_computers", "computers_count", "has_audio_system", "has_video_recording", "has_air_conditioning", "is_accessible", "has_windows", "description", "created_by")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    BUILDING_ID_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    WING_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_AREA_FIELD_NUMBER: _ClassVar[int]
    CLASSROOM_TYPE_FIELD_NUMBER: _ClassVar[int]
    HAS_PROJECTOR_FIELD_NUMBER: _ClassVar[int]
    HAS_WHITEBOARD_FIELD_NUMBER: _ClassVar[int]
    HAS_BLACKBOARD_FIELD_NUMBER: _ClassVar[int]
    HAS_MARKERS_FIELD_NUMBER: _ClassVar[int]
    HAS_CHALK_FIELD_NUMBER: _ClassVar[int]
    HAS_COMPUTERS_FIELD_NUMBER: _ClassVar[int]
    COMPUTERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    HAS_AUDIO_SYSTEM_FIELD_NUMBER: _ClassVar[int]
    HAS_VIDEO_RECORDING_FIELD_NUMBER: _ClassVar[int]
    HAS_AIR_CONDITIONING_FIELD_NUMBER: _ClassVar[int]
    IS_ACCESSIBLE_FIELD_NUMBER: _ClassVar[int]
    HAS_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    name: str
    code: str
    building_id: int
    floor: int
    wing: str
    capacity: int
    actual_area: float
    classroom_type: str
    has_projector: bool
    has_whiteboard: bool
    has_blackboard: bool
    has_markers: bool
    has_chalk: bool
    has_computers: bool
    computers_count: int
    has_audio_system: bool
    has_video_recording: bool
    has_air_conditioning: bool
    is_accessible: bool
    has_windows: bool
    description: str
    created_by: int
    def __init__(self, name: _Optional[str] = ..., code: _Optional[str] = ..., building_id: _Optional[int] = ..., floor: _Optional[int] = ..., wing: _Optional[str] = ..., capacity: _Optional[int] = ..., actual_area: _Optional[float] = ..., classroom_type: _Optional[str] = ..., has_projector: bool = ..., has_whiteboard: bool = ..., has_blackboard: bool = ..., has_markers: bool = ..., has_chalk: bool = ..., has_computers: bool = ..., computers_count: _Optional[int] = ..., has_audio_system: bool = ..., has_video_recording: bool = ..., has_air_conditioning: bool = ..., is_accessible: bool = ..., has_windows: bool = ..., description: _Optional[str] = ..., created_by: _Optional[int] = ...) -> None: ...

class GetClassroomRequest(_message.Message):
    __slots__ = ("id", "code", "include_schedule")
    ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    id: int
    code: str
    include_schedule: bool
    def __init__(self, id: _Optional[int] = ..., code: _Optional[str] = ..., include_schedule: bool = ...) -> None: ...

class UpdateClassroomRequest(_message.Message):
    __slots__ = ("id", "updates", "updated_by")
    class UpdatesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    UPDATED_BY_FIELD_NUMBER: _ClassVar[int]
    id: int
    updates: _containers.ScalarMap[str, str]
    updated_by: int
    def __init__(self, id: _Optional[int] = ..., updates: _Optional[_Mapping[str, str]] = ..., updated_by: _Optional[int] = ...) -> None: ...

class DeleteClassroomRequest(_message.Message):
    __slots__ = ("id", "hard_delete")
    ID_FIELD_NUMBER: _ClassVar[int]
    HARD_DELETE_FIELD_NUMBER: _ClassVar[int]
    id: int
    hard_delete: bool
    def __init__(self, id: _Optional[int] = ..., hard_delete: bool = ...) -> None: ...

class ListClassroomsRequest(_message.Message):
    __slots__ = ("page", "page_size", "building_ids", "classroom_types", "min_capacity", "max_capacity", "search_query", "only_active", "sort_by", "sort_order")
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    BUILDING_IDS_FIELD_NUMBER: _ClassVar[int]
    CLASSROOM_TYPES_FIELD_NUMBER: _ClassVar[int]
    MIN_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    MAX_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    SEARCH_QUERY_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    page: int
    page_size: int
    building_ids: _containers.RepeatedScalarFieldContainer[int]
    classroom_types: _containers.RepeatedScalarFieldContainer[str]
    min_capacity: int
    max_capacity: int
    search_query: str
    only_active: bool
    sort_by: str
    sort_order: str
    def __init__(self, page: _Optional[int] = ..., page_size: _Optional[int] = ..., building_ids: _Optional[_Iterable[int]] = ..., classroom_types: _Optional[_Iterable[str]] = ..., min_capacity: _Optional[int] = ..., max_capacity: _Optional[int] = ..., search_query: _Optional[str] = ..., only_active: bool = ..., sort_by: _Optional[str] = ..., sort_order: _Optional[str] = ...) -> None: ...

class FindAvailableRequest(_message.Message):
    __slots__ = ("day_of_week", "time_slot", "min_capacity", "need_projector", "need_whiteboard", "need_computers", "building_ids", "classroom_types", "sort_by")
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    MIN_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    NEED_PROJECTOR_FIELD_NUMBER: _ClassVar[int]
    NEED_WHITEBOARD_FIELD_NUMBER: _ClassVar[int]
    NEED_COMPUTERS_FIELD_NUMBER: _ClassVar[int]
    BUILDING_IDS_FIELD_NUMBER: _ClassVar[int]
    CLASSROOM_TYPES_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    day_of_week: int
    time_slot: int
    min_capacity: int
    need_projector: bool
    need_whiteboard: bool
    need_computers: bool
    building_ids: _containers.RepeatedScalarFieldContainer[int]
    classroom_types: _containers.RepeatedScalarFieldContainer[str]
    sort_by: str
    def __init__(self, day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., min_capacity: _Optional[int] = ..., need_projector: bool = ..., need_whiteboard: bool = ..., need_computers: bool = ..., building_ids: _Optional[_Iterable[int]] = ..., classroom_types: _Optional[_Iterable[str]] = ..., sort_by: _Optional[str] = ...) -> None: ...

class CheckAvailabilityRequest(_message.Message):
    __slots__ = ("classroom_id", "day_of_week", "time_slot")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    day_of_week: int
    time_slot: int
    def __init__(self, classroom_id: _Optional[int] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ...) -> None: ...

class ReserveRequest(_message.Message):
    __slots__ = ("classroom_id", "day_of_week", "time_slot", "week", "schedule_id", "discipline_name", "teacher_name", "group_name", "lesson_type")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    WEEK_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_NAME_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    LESSON_TYPE_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    day_of_week: int
    time_slot: int
    week: int
    schedule_id: int
    discipline_name: str
    teacher_name: str
    group_name: str
    lesson_type: str
    def __init__(self, classroom_id: _Optional[int] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., week: _Optional[int] = ..., schedule_id: _Optional[int] = ..., discipline_name: _Optional[str] = ..., teacher_name: _Optional[str] = ..., group_name: _Optional[str] = ..., lesson_type: _Optional[str] = ...) -> None: ...

class BulkReserveRequest(_message.Message):
    __slots__ = ("reservations", "validate_only")
    RESERVATIONS_FIELD_NUMBER: _ClassVar[int]
    VALIDATE_ONLY_FIELD_NUMBER: _ClassVar[int]
    reservations: _containers.RepeatedCompositeFieldContainer[ReserveRequest]
    validate_only: bool
    def __init__(self, reservations: _Optional[_Iterable[_Union[ReserveRequest, _Mapping]]] = ..., validate_only: bool = ...) -> None: ...

class CancelReservationRequest(_message.Message):
    __slots__ = ("schedule_record_id", "slot")
    SCHEDULE_RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    schedule_record_id: int
    slot: TimeSlot
    def __init__(self, schedule_record_id: _Optional[int] = ..., slot: _Optional[_Union[TimeSlot, _Mapping]] = ...) -> None: ...

class TimeSlot(_message.Message):
    __slots__ = ("classroom_id", "day_of_week", "time_slot")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    day_of_week: int
    time_slot: int
    def __init__(self, classroom_id: _Optional[int] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ...) -> None: ...

class GetScheduleRequest(_message.Message):
    __slots__ = ("classroom_id", "days_of_week", "week")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    DAYS_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    WEEK_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    days_of_week: _containers.RepeatedScalarFieldContainer[int]
    week: int
    def __init__(self, classroom_id: _Optional[int] = ..., days_of_week: _Optional[_Iterable[int]] = ..., week: _Optional[int] = ...) -> None: ...

class DistanceRequest(_message.Message):
    __slots__ = ("from_classroom_id", "to_classroom_id")
    FROM_CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    TO_CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    from_classroom_id: int
    to_classroom_id: int
    def __init__(self, from_classroom_id: _Optional[int] = ..., to_classroom_id: _Optional[int] = ...) -> None: ...

class StatisticsRequest(_message.Message):
    __slots__ = ("classroom_id", "building_id", "all")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    BUILDING_ID_FIELD_NUMBER: _ClassVar[int]
    ALL_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    building_id: int
    all: bool
    def __init__(self, classroom_id: _Optional[int] = ..., building_id: _Optional[int] = ..., all: bool = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateBuildingRequest(_message.Message):
    __slots__ = ("name", "short_name", "code", "address", "campus", "latitude", "longitude", "total_floors", "has_elevator")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FLOORS_FIELD_NUMBER: _ClassVar[int]
    HAS_ELEVATOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    short_name: str
    code: str
    address: str
    campus: str
    latitude: float
    longitude: float
    total_floors: int
    has_elevator: bool
    def __init__(self, name: _Optional[str] = ..., short_name: _Optional[str] = ..., code: _Optional[str] = ..., address: _Optional[str] = ..., campus: _Optional[str] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., total_floors: _Optional[int] = ..., has_elevator: bool = ...) -> None: ...

class GetBuildingRequest(_message.Message):
    __slots__ = ("building_id",)
    BUILDING_ID_FIELD_NUMBER: _ClassVar[int]
    building_id: int
    def __init__(self, building_id: _Optional[int] = ...) -> None: ...

class UpdateBuildingRequest(_message.Message):
    __slots__ = ("building_id", "name", "short_name", "code", "address", "campus", "latitude", "longitude", "total_floors", "has_elevator")
    BUILDING_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CAMPUS_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FLOORS_FIELD_NUMBER: _ClassVar[int]
    HAS_ELEVATOR_FIELD_NUMBER: _ClassVar[int]
    building_id: int
    name: str
    short_name: str
    code: str
    address: str
    campus: str
    latitude: float
    longitude: float
    total_floors: int
    has_elevator: bool
    def __init__(self, building_id: _Optional[int] = ..., name: _Optional[str] = ..., short_name: _Optional[str] = ..., code: _Optional[str] = ..., address: _Optional[str] = ..., campus: _Optional[str] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ..., total_floors: _Optional[int] = ..., has_elevator: bool = ...) -> None: ...

class DeleteBuildingRequest(_message.Message):
    __slots__ = ("building_id",)
    BUILDING_ID_FIELD_NUMBER: _ClassVar[int]
    building_id: int
    def __init__(self, building_id: _Optional[int] = ...) -> None: ...

class ListBuildingsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClassroomResponse(_message.Message):
    __slots__ = ("classroom", "message")
    CLASSROOM_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    classroom: Classroom
    message: str
    def __init__(self, classroom: _Optional[_Union[Classroom, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class ListClassroomsResponse(_message.Message):
    __slots__ = ("classrooms", "total_count", "page", "page_size")
    CLASSROOMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    classrooms: _containers.RepeatedCompositeFieldContainer[Classroom]
    total_count: int
    page: int
    page_size: int
    def __init__(self, classrooms: _Optional[_Iterable[_Union[Classroom, _Mapping]]] = ..., total_count: _Optional[int] = ..., page: _Optional[int] = ..., page_size: _Optional[int] = ...) -> None: ...

class AvailableClassroomsResponse(_message.Message):
    __slots__ = ("classrooms",)
    CLASSROOMS_FIELD_NUMBER: _ClassVar[int]
    classrooms: _containers.RepeatedCompositeFieldContainer[AvailableClassroom]
    def __init__(self, classrooms: _Optional[_Iterable[_Union[AvailableClassroom, _Mapping]]] = ...) -> None: ...

class AvailableClassroom(_message.Message):
    __slots__ = ("classroom", "utilization_score", "fully_equipped")
    CLASSROOM_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_SCORE_FIELD_NUMBER: _ClassVar[int]
    FULLY_EQUIPPED_FIELD_NUMBER: _ClassVar[int]
    classroom: Classroom
    utilization_score: float
    fully_equipped: bool
    def __init__(self, classroom: _Optional[_Union[Classroom, _Mapping]] = ..., utilization_score: _Optional[float] = ..., fully_equipped: bool = ...) -> None: ...

class AvailabilityResponse(_message.Message):
    __slots__ = ("is_available", "reason")
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    is_available: bool
    reason: str
    def __init__(self, is_available: bool = ..., reason: _Optional[str] = ...) -> None: ...

class ReserveResponse(_message.Message):
    __slots__ = ("success", "schedule_id", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    schedule_id: int
    message: str
    def __init__(self, success: bool = ..., schedule_id: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class BulkReserveResponse(_message.Message):
    __slots__ = ("successful_count", "failed_count", "results")
    SUCCESSFUL_COUNT_FIELD_NUMBER: _ClassVar[int]
    FAILED_COUNT_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    successful_count: int
    failed_count: int
    results: _containers.RepeatedCompositeFieldContainer[ReservationResult]
    def __init__(self, successful_count: _Optional[int] = ..., failed_count: _Optional[int] = ..., results: _Optional[_Iterable[_Union[ReservationResult, _Mapping]]] = ...) -> None: ...

class ReservationResult(_message.Message):
    __slots__ = ("classroom_id", "success", "error_message")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    success: bool
    error_message: str
    def __init__(self, classroom_id: _Optional[int] = ..., success: bool = ..., error_message: _Optional[str] = ...) -> None: ...

class DeleteResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class CancelResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ScheduleResponse(_message.Message):
    __slots__ = ("classroom_id", "slots", "total_occupied", "utilization_percentage")
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    SLOTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_OCCUPIED_FIELD_NUMBER: _ClassVar[int]
    UTILIZATION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    classroom_id: int
    slots: _containers.RepeatedCompositeFieldContainer[ScheduleSlot]
    total_occupied: int
    utilization_percentage: float
    def __init__(self, classroom_id: _Optional[int] = ..., slots: _Optional[_Iterable[_Union[ScheduleSlot, _Mapping]]] = ..., total_occupied: _Optional[int] = ..., utilization_percentage: _Optional[float] = ...) -> None: ...

class ScheduleSlot(_message.Message):
    __slots__ = ("day_of_week", "time_slot", "week", "discipline_name", "teacher_name", "group_name", "lesson_type")
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    WEEK_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_NAME_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    LESSON_TYPE_FIELD_NUMBER: _ClassVar[int]
    day_of_week: int
    time_slot: int
    week: int
    discipline_name: str
    teacher_name: str
    group_name: str
    lesson_type: str
    def __init__(self, day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., week: _Optional[int] = ..., discipline_name: _Optional[str] = ..., teacher_name: _Optional[str] = ..., group_name: _Optional[str] = ..., lesson_type: _Optional[str] = ...) -> None: ...

class DistanceResponse(_message.Message):
    __slots__ = ("distance_meters", "walking_time_seconds", "requires_building_change")
    DISTANCE_METERS_FIELD_NUMBER: _ClassVar[int]
    WALKING_TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_BUILDING_CHANGE_FIELD_NUMBER: _ClassVar[int]
    distance_meters: int
    walking_time_seconds: int
    requires_building_change: bool
    def __init__(self, distance_meters: _Optional[int] = ..., walking_time_seconds: _Optional[int] = ..., requires_building_change: bool = ...) -> None: ...

class StatisticsResponse(_message.Message):
    __slots__ = ("total_classrooms", "total_capacity", "average_utilization", "by_type")
    class ByTypeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    TOTAL_CLASSROOMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    BY_TYPE_FIELD_NUMBER: _ClassVar[int]
    total_classrooms: int
    total_capacity: int
    average_utilization: float
    by_type: _containers.ScalarMap[str, int]
    def __init__(self, total_classrooms: _Optional[int] = ..., total_capacity: _Optional[int] = ..., average_utilization: _Optional[float] = ..., by_type: _Optional[_Mapping[str, int]] = ...) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status", "version")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    status: str
    version: str
    def __init__(self, status: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class BuildingResponse(_message.Message):
    __slots__ = ("building", "message")
    BUILDING_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    building: Building
    message: str
    def __init__(self, building: _Optional[_Union[Building, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class BuildingsResponse(_message.Message):
    __slots__ = ("buildings", "total_count", "message")
    BUILDINGS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    buildings: _containers.RepeatedCompositeFieldContainer[Building]
    total_count: int
    message: str
    def __init__(self, buildings: _Optional[_Iterable[_Union[Building, _Mapping]]] = ..., total_count: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...
