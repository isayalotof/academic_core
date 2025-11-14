from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CourseLoad(_message.Message):
    __slots__ = ("id", "discipline_name", "discipline_code", "teacher_id", "teacher_name", "teacher_priority", "group_id", "group_name", "group_size", "lesson_type", "hours_per_semester", "lessons_per_week", "semester", "academic_year")
    ID_FIELD_NUMBER: _ClassVar[int]
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
    LESSONS_PER_WEEK_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    id: int
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
    lessons_per_week: int
    semester: int
    academic_year: str
    def __init__(self, id: _Optional[int] = ..., discipline_name: _Optional[str] = ..., discipline_code: _Optional[str] = ..., teacher_id: _Optional[int] = ..., teacher_name: _Optional[str] = ..., teacher_priority: _Optional[int] = ..., group_id: _Optional[int] = ..., group_name: _Optional[str] = ..., group_size: _Optional[int] = ..., lesson_type: _Optional[str] = ..., hours_per_semester: _Optional[int] = ..., lessons_per_week: _Optional[int] = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ...) -> None: ...

class Schedule(_message.Message):
    __slots__ = ("id", "course_load_id", "day_of_week", "time_slot", "classroom_id", "classroom_name", "teacher_id", "teacher_name", "group_id", "group_name", "discipline_name", "lesson_type", "generation_id", "is_active", "semester", "academic_year", "week_type")
    ID_FIELD_NUMBER: _ClassVar[int]
    COURSE_LOAD_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    CLASSROOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLASSROOM_NAME_FIELD_NUMBER: _ClassVar[int]
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    TEACHER_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    DISCIPLINE_NAME_FIELD_NUMBER: _ClassVar[int]
    LESSON_TYPE_FIELD_NUMBER: _ClassVar[int]
    GENERATION_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    ACADEMIC_YEAR_FIELD_NUMBER: _ClassVar[int]
    WEEK_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    course_load_id: int
    day_of_week: int
    time_slot: int
    classroom_id: int
    classroom_name: str
    teacher_id: int
    teacher_name: str
    group_id: int
    group_name: str
    discipline_name: str
    lesson_type: str
    generation_id: int
    is_active: bool
    semester: int
    academic_year: str
    week_type: str
    def __init__(self, id: _Optional[int] = ..., course_load_id: _Optional[int] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., classroom_id: _Optional[int] = ..., classroom_name: _Optional[str] = ..., teacher_id: _Optional[int] = ..., teacher_name: _Optional[str] = ..., group_id: _Optional[int] = ..., group_name: _Optional[str] = ..., discipline_name: _Optional[str] = ..., lesson_type: _Optional[str] = ..., generation_id: _Optional[int] = ..., is_active: bool = ..., semester: _Optional[int] = ..., academic_year: _Optional[str] = ..., week_type: _Optional[str] = ...) -> None: ...

class GenerationHistory(_message.Message):
    __slots__ = ("id", "job_id", "stage", "stage_name", "status", "current_iteration", "max_iterations", "initial_score", "current_score", "best_score", "metrics", "last_reasoning", "total_actions", "started_at", "completed_at", "duration_seconds", "error_message")
    class MetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    STAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ITERATION_FIELD_NUMBER: _ClassVar[int]
    MAX_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_SCORE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_SCORE_FIELD_NUMBER: _ClassVar[int]
    BEST_SCORE_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    LAST_REASONING_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    id: int
    job_id: str
    stage: int
    stage_name: str
    status: str
    current_iteration: int
    max_iterations: int
    initial_score: int
    current_score: int
    best_score: int
    metrics: _containers.ScalarMap[str, int]
    last_reasoning: str
    total_actions: int
    started_at: str
    completed_at: str
    duration_seconds: int
    error_message: str
    def __init__(self, id: _Optional[int] = ..., job_id: _Optional[str] = ..., stage: _Optional[int] = ..., stage_name: _Optional[str] = ..., status: _Optional[str] = ..., current_iteration: _Optional[int] = ..., max_iterations: _Optional[int] = ..., initial_score: _Optional[int] = ..., current_score: _Optional[int] = ..., best_score: _Optional[int] = ..., metrics: _Optional[_Mapping[str, int]] = ..., last_reasoning: _Optional[str] = ..., total_actions: _Optional[int] = ..., started_at: _Optional[str] = ..., completed_at: _Optional[str] = ..., duration_seconds: _Optional[int] = ..., error_message: _Optional[str] = ...) -> None: ...

class AgentAction(_message.Message):
    __slots__ = ("id", "generation_id", "iteration", "action_type", "action_params", "success", "score_before", "score_after", "score_delta", "reasoning", "created_at", "execution_time_ms")
    ID_FIELD_NUMBER: _ClassVar[int]
    GENERATION_ID_FIELD_NUMBER: _ClassVar[int]
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACTION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SCORE_BEFORE_FIELD_NUMBER: _ClassVar[int]
    SCORE_AFTER_FIELD_NUMBER: _ClassVar[int]
    SCORE_DELTA_FIELD_NUMBER: _ClassVar[int]
    REASONING_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_MS_FIELD_NUMBER: _ClassVar[int]
    id: int
    generation_id: int
    iteration: int
    action_type: str
    action_params: str
    success: bool
    score_before: int
    score_after: int
    score_delta: int
    reasoning: str
    created_at: str
    execution_time_ms: int
    def __init__(self, id: _Optional[int] = ..., generation_id: _Optional[int] = ..., iteration: _Optional[int] = ..., action_type: _Optional[str] = ..., action_params: _Optional[str] = ..., success: bool = ..., score_before: _Optional[int] = ..., score_after: _Optional[int] = ..., score_delta: _Optional[int] = ..., reasoning: _Optional[str] = ..., created_at: _Optional[str] = ..., execution_time_ms: _Optional[int] = ...) -> None: ...

class GenerateRequest(_message.Message):
    __slots__ = ("semester", "max_iterations", "skip_stage1", "skip_stage2", "building_ids", "created_by")
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    MAX_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    SKIP_STAGE1_FIELD_NUMBER: _ClassVar[int]
    SKIP_STAGE2_FIELD_NUMBER: _ClassVar[int]
    BUILDING_IDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    semester: int
    max_iterations: int
    skip_stage1: bool
    skip_stage2: bool
    building_ids: _containers.RepeatedScalarFieldContainer[int]
    created_by: int
    def __init__(self, semester: _Optional[int] = ..., max_iterations: _Optional[int] = ..., skip_stage1: bool = ..., skip_stage2: bool = ..., building_ids: _Optional[_Iterable[int]] = ..., created_by: _Optional[int] = ...) -> None: ...

class GenerateResponse(_message.Message):
    __slots__ = ("success", "job_id", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    job_id: str
    message: str
    def __init__(self, success: bool = ..., job_id: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class StatusRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("generation", "progress_percentage", "estimated_seconds_remaining", "recent_actions")
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_SECONDS_REMAINING_FIELD_NUMBER: _ClassVar[int]
    RECENT_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    generation: GenerationHistory
    progress_percentage: float
    estimated_seconds_remaining: int
    recent_actions: _containers.RepeatedCompositeFieldContainer[AgentAction]
    def __init__(self, generation: _Optional[_Union[GenerationHistory, _Mapping]] = ..., progress_percentage: _Optional[float] = ..., estimated_seconds_remaining: _Optional[int] = ..., recent_actions: _Optional[_Iterable[_Union[AgentAction, _Mapping]]] = ...) -> None: ...

class HistoryRequest(_message.Message):
    __slots__ = ("job_id", "limit")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    limit: int
    def __init__(self, job_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class HistoryResponse(_message.Message):
    __slots__ = ("generation", "actions")
    GENERATION_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    generation: GenerationHistory
    actions: _containers.RepeatedCompositeFieldContainer[AgentAction]
    def __init__(self, generation: _Optional[_Union[GenerationHistory, _Mapping]] = ..., actions: _Optional[_Iterable[_Union[AgentAction, _Mapping]]] = ...) -> None: ...

class StopRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class StopResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetCourseLoadsRequest(_message.Message):
    __slots__ = ("semester", "teacher_ids", "group_ids")
    SEMESTER_FIELD_NUMBER: _ClassVar[int]
    TEACHER_IDS_FIELD_NUMBER: _ClassVar[int]
    GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    semester: int
    teacher_ids: _containers.RepeatedScalarFieldContainer[int]
    group_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, semester: _Optional[int] = ..., teacher_ids: _Optional[_Iterable[int]] = ..., group_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class CourseLoadsResponse(_message.Message):
    __slots__ = ("course_loads", "total_count")
    COURSE_LOADS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    course_loads: _containers.RepeatedCompositeFieldContainer[CourseLoad]
    total_count: int
    def __init__(self, course_loads: _Optional[_Iterable[_Union[CourseLoad, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetScheduleRequest(_message.Message):
    __slots__ = ("generation_id", "only_active")
    GENERATION_ID_FIELD_NUMBER: _ClassVar[int]
    ONLY_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    generation_id: int
    only_active: bool
    def __init__(self, generation_id: _Optional[int] = ..., only_active: bool = ...) -> None: ...

class GroupScheduleRequest(_message.Message):
    __slots__ = ("group_id", "day_of_week")
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    group_id: int
    day_of_week: int
    def __init__(self, group_id: _Optional[int] = ..., day_of_week: _Optional[int] = ...) -> None: ...

class TeacherScheduleRequest(_message.Message):
    __slots__ = ("teacher_id", "day_of_week")
    TEACHER_ID_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    teacher_id: int
    day_of_week: int
    def __init__(self, teacher_id: _Optional[int] = ..., day_of_week: _Optional[int] = ...) -> None: ...

class ScheduleResponse(_message.Message):
    __slots__ = ("schedules", "total_count")
    SCHEDULES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    schedules: _containers.RepeatedCompositeFieldContainer[Schedule]
    total_count: int
    def __init__(self, schedules: _Optional[_Iterable[_Union[Schedule, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class AnalyzeRequest(_message.Message):
    __slots__ = ("generation_id", "current_active")
    GENERATION_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    generation_id: int
    current_active: bool
    def __init__(self, generation_id: _Optional[int] = ..., current_active: bool = ...) -> None: ...

class AnalysisResponse(_message.Message):
    __slots__ = ("conflicts", "total_lessons", "preference_violations", "isolated_lessons", "gaps_count", "total_score", "teacher_metrics_json")
    class TeacherMetricsJsonEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: str
        def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...
    CONFLICTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_LESSONS_FIELD_NUMBER: _ClassVar[int]
    PREFERENCE_VIOLATIONS_FIELD_NUMBER: _ClassVar[int]
    ISOLATED_LESSONS_FIELD_NUMBER: _ClassVar[int]
    GAPS_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SCORE_FIELD_NUMBER: _ClassVar[int]
    TEACHER_METRICS_JSON_FIELD_NUMBER: _ClassVar[int]
    conflicts: _containers.RepeatedCompositeFieldContainer[Conflict]
    total_lessons: int
    preference_violations: int
    isolated_lessons: int
    gaps_count: int
    total_score: int
    teacher_metrics_json: _containers.ScalarMap[int, str]
    def __init__(self, conflicts: _Optional[_Iterable[_Union[Conflict, _Mapping]]] = ..., total_lessons: _Optional[int] = ..., preference_violations: _Optional[int] = ..., isolated_lessons: _Optional[int] = ..., gaps_count: _Optional[int] = ..., total_score: _Optional[int] = ..., teacher_metrics_json: _Optional[_Mapping[int, str]] = ...) -> None: ...

class Conflict(_message.Message):
    __slots__ = ("conflict_type", "day_of_week", "time_slot", "schedule_ids", "description")
    CONFLICT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DAY_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    TIME_SLOT_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_IDS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    conflict_type: str
    day_of_week: int
    time_slot: int
    schedule_ids: _containers.RepeatedScalarFieldContainer[int]
    description: str
    def __init__(self, conflict_type: _Optional[str] = ..., day_of_week: _Optional[int] = ..., time_slot: _Optional[int] = ..., schedule_ids: _Optional[_Iterable[int]] = ..., description: _Optional[str] = ...) -> None: ...

class MetricsRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class MetricsResponse(_message.Message):
    __slots__ = ("score_history", "top_actions")
    SCORE_HISTORY_FIELD_NUMBER: _ClassVar[int]
    TOP_ACTIONS_FIELD_NUMBER: _ClassVar[int]
    score_history: _containers.RepeatedCompositeFieldContainer[ScorePoint]
    top_actions: _containers.RepeatedCompositeFieldContainer[ActionSummary]
    def __init__(self, score_history: _Optional[_Iterable[_Union[ScorePoint, _Mapping]]] = ..., top_actions: _Optional[_Iterable[_Union[ActionSummary, _Mapping]]] = ...) -> None: ...

class ScorePoint(_message.Message):
    __slots__ = ("iteration", "score")
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    iteration: int
    score: int
    def __init__(self, iteration: _Optional[int] = ..., score: _Optional[int] = ...) -> None: ...

class ActionSummary(_message.Message):
    __slots__ = ("action_type", "count", "avg_score_delta")
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    AVG_SCORE_DELTA_FIELD_NUMBER: _ClassVar[int]
    action_type: str
    count: int
    avg_score_delta: int
    def __init__(self, action_type: _Optional[str] = ..., count: _Optional[int] = ..., avg_score_delta: _Optional[int] = ...) -> None: ...

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
