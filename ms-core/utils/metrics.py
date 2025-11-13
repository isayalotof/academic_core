"""
Prometheus metrics for ms-core
"""
from prometheus_client import Counter, Histogram, Gauge, Info
import logging

logger = logging.getLogger(__name__)

# ============ ОБЩИЕ МЕТРИКИ ============

service_info = Info('ms_core_service', 'Service information')
service_info.info({
    'version': '1.0.0',
    'service': 'ms-core',
    'description': 'University core entities management'
})

# ============ ПРЕПОДАВАТЕЛИ ============

teachers_total = Gauge(
    'teachers_total',
    'Total number of teachers',
    ['employment_type', 'is_active']
)

teachers_created = Counter(
    'teachers_created_total',
    'Total teachers created'
)

teachers_updated = Counter(
    'teachers_updated_total',
    'Total teachers updated'
)

# ⭐ ПРЕДПОЧТЕНИЯ ПРЕПОДАВАТЕЛЕЙ (KEY METRICS!)

teacher_preferences_set = Counter(
    'teacher_preferences_set_total',
    'Total preferences set operations',
    ['teacher_id']
)

teacher_preferences_coverage = Gauge(
    'teacher_preferences_coverage',
    'Preferences coverage percentage',
    ['teacher_id', 'teacher_priority']
)

teacher_preferences_avg_coverage = Gauge(
    'teacher_preferences_avg_coverage',
    'Average preferences coverage across all teachers'
)

preferred_slots_total = Gauge(
    'teacher_preferred_slots_total',
    'Total preferred slots',
    ['teacher_id', 'priority']
)

# ============ ГРУППЫ И СТУДЕНТЫ ============

groups_total = Gauge(
    'groups_total',
    'Total number of groups',
    ['level', 'is_active']
)

students_total = Gauge(
    'students_total',
    'Total number of students',
    ['status']
)

group_size_avg = Gauge(
    'group_size_avg',
    'Average group size'
)

# ============ УЧЕБНАЯ НАГРУЗКА ============

course_loads_total = Gauge(
    'course_loads_total',
    'Total course loads',
    ['semester', 'academic_year', 'lesson_type']
)

course_loads_created = Counter(
    'course_loads_created_total',
    'Total course loads created'
)

# ============ ИМПОРТ EXCEL ============

course_loads_imported = Counter(
    'course_loads_imported_total',
    'Total course loads imported',
    ['status']  # 'success', 'failed'
)

import_duration = Histogram(
    'course_load_import_duration_seconds',
    'Course load import duration',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

import_rows = Histogram(
    'course_load_import_rows',
    'Number of rows in import',
    buckets=[10, 50, 100, 200, 500, 1000, 2000]
)

import_errors = Counter(
    'course_load_import_errors_total',
    'Total import errors',
    ['error_type']
)

# ============ RPC МЕТРИКИ ============

rpc_requests_total = Counter(
    'ms_core_rpc_requests_total',
    'Total RPC requests',
    ['method', 'status']
)

rpc_request_duration = Histogram(
    'ms_core_rpc_request_duration_seconds',
    'RPC request duration',
    ['method'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# ============ CACHE МЕТРИКИ ============

cache_hits = Counter(
    'ms_core_cache_hits_total',
    'Total cache hits',
    ['cache_key']
)

cache_misses = Counter(
    'ms_core_cache_misses_total',
    'Total cache misses',
    ['cache_key']
)


def update_teachers_metrics(db_pool):
    """Обновить метрики по преподавателям"""
    try:
        result = db_pool.execute_query("""
            SELECT employment_type, is_active, COUNT(*) as count
            FROM teachers
            GROUP BY employment_type, is_active
        """, fetch=True)
        
        for row in result:
            teachers_total.labels(
                employment_type=row['employment_type'],
                is_active=str(row['is_active'])
            ).set(row['count'])
    except Exception as e:
        logger.error(f"Error updating teachers metrics: {e}")


def update_preferences_metrics(db_pool):
    """Обновить метрики по предпочтениям"""
    try:
        # Средний coverage
        result = db_pool.execute_query("""
            SELECT AVG((COUNT(*)::DECIMAL / 36 * 100)) as avg_coverage
            FROM teacher_preferences
            GROUP BY teacher_id
        """, fetch=True)
        
        if result:
            teacher_preferences_avg_coverage.set(result[0]['avg_coverage'] or 0)
    except Exception as e:
        logger.error(f"Error updating preferences metrics: {e}")


def update_all_metrics(db_pool):
    """Обновить все метрики"""
    update_teachers_metrics(db_pool)
    update_preferences_metrics(db_pool)

