"""
Prometheus metrics for ms-schedule
Метрики производительности и мониторинга
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable
import logging

from config import config

logger = logging.getLogger(__name__)

# ============ SERVICE INFO ============

service_info = Info('ms_schedule_info', 'MS-Schedule service information')
service_info.info({
    'version': config.SERVICE_VERSION,
    'environment': config.ENVIRONMENT
})

# ============ SCHEDULE VIEWS ============

schedule_views_total = Counter(
    'schedule_views_total',
    'Total number of schedule views',
    ['entity_type', 'status']  # 'group', 'teacher', 'classroom' + 'success'/'error'
)

schedule_view_duration = Histogram(
    'schedule_view_duration_seconds',
    'Schedule view duration',
    ['entity_type']
)

# ============ EXPORTS ============

schedule_exports_total = Counter(
    'schedule_exports_total',
    'Total number of schedule exports',
    ['format', 'status']  # 'excel', 'pdf', 'ical' + 'success'/'error'
)

schedule_export_duration = Histogram(
    'schedule_export_duration_seconds',
    'Schedule export duration',
    ['format']
)

export_file_size_bytes = Histogram(
    'schedule_export_file_size_bytes',
    'Exported file size in bytes',
    ['format'],
    buckets=[1024, 10240, 102400, 1024000, 10240000]  # 1KB to 10MB
)

# ============ SCHEDULE OPERATIONS ============

schedule_operations_total = Counter(
    'schedule_operations_total',
    'Total schedule operations',
    ['operation', 'status']  # 'create', 'update', 'delete', 'activate'
)

schedule_active_total = Gauge(
    'schedule_active_total',
    'Number of active schedules'
)

schedule_lessons_total = Gauge(
    'schedule_lessons_total',
    'Total number of lessons',
    ['lesson_type']
)

# ============ CONFLICTS ============

schedule_conflicts_detected = Counter(
    'schedule_conflicts_detected_total',
    'Total conflicts detected',
    ['conflict_type']  # 'teacher', 'group', 'classroom'
)

schedule_conflicts_active = Gauge(
    'schedule_conflicts_active',
    'Number of active conflicts',
    ['conflict_type', 'severity']
)

# ============ HISTORY ============

schedule_changes_total = Counter(
    'schedule_changes_total',
    'Total schedule changes logged',
    ['change_type']  # 'created', 'updated', 'deleted'
)

# ============ SNAPSHOTS ============

schedule_snapshots_total = Counter(
    'schedule_snapshots_total',
    'Total snapshots created',
    ['snapshot_type']  # 'manual', 'auto', 'generation', 'backup'
)

snapshot_size_bytes = Histogram(
    'schedule_snapshot_size_bytes',
    'Snapshot data size',
    buckets=[10240, 102400, 1024000, 10240000, 102400000]  # 10KB to 100MB
)

# ============ CACHE ============

cache_operations_total = Counter(
    'schedule_cache_operations_total',
    'Total cache operations',
    ['operation', 'status']  # 'get', 'set', 'delete' + 'hit'/'miss'/'error'
)

# ============ DATABASE ============

database_query_duration = Histogram(
    'schedule_database_query_duration_seconds',
    'Database query duration',
    ['query_type']  # 'select', 'insert', 'update', 'delete'
)

database_errors_total = Counter(
    'schedule_database_errors_total',
    'Total database errors',
    ['error_type']
)

# ============ DECORATORS ============

def track_view(entity_type: str):
    """Decorator to track schedule views"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'error'
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                logger.error(f"View error: {e}")
                raise
            finally:
                duration = time.time() - start_time
                schedule_views_total.labels(entity_type=entity_type, status=status).inc()
                schedule_view_duration.labels(entity_type=entity_type).observe(duration)
        
        return wrapper
    return decorator


def track_export(format_type: str):
    """Decorator to track exports"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'error'
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
                
                # Track file size
                if isinstance(result, bytes):
                    export_file_size_bytes.labels(format=format_type).observe(len(result))
                
                return result
            except Exception as e:
                logger.error(f"Export error: {e}")
                raise
            finally:
                duration = time.time() - start_time
                schedule_exports_total.labels(format=format_type, status=status).inc()
                schedule_export_duration.labels(format=format_type).observe(duration)
        
        return wrapper
    return decorator


def track_db_query(query_type: str):
    """Decorator to track database queries"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                database_query_duration.labels(query_type=query_type).observe(duration)
        
        return wrapper
    return decorator

