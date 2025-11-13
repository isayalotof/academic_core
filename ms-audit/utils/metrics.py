"""
Prometheus Metrics
Метрики для мониторинга микросервиса
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# ============ COUNTERS ============

# RPC requests counter
rpc_requests_total = Counter(
    'rpc_requests_total',
    'Total number of RPC requests',
    ['method', 'status']
)

# Database queries counter
db_queries_total = Counter(
    'db_queries_total',
    'Total number of database queries',
    ['operation', 'table']
)

# Cache operations counter
cache_operations_total = Counter(
    'cache_operations_total',
    'Total number of cache operations',
    ['operation', 'result']
)

# ============ HISTOGRAMS ============

# RPC request duration
rpc_duration_seconds = Histogram(
    'rpc_duration_seconds',
    'Duration of RPC requests in seconds',
    ['method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Database query duration
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Duration of database queries in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# ============ GAUGES ============

# Active classrooms
classrooms_total = Gauge(
    'classrooms_total',
    'Total number of active classrooms'
)

# Available classrooms
available_classrooms = Gauge(
    'available_classrooms',
    'Number of available classrooms',
    ['day', 'time_slot']
)

# Database connections
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

# Cache hit rate
cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)

# ============ SUMMARY ============

# Response size
response_size_bytes = Summary(
    'response_size_bytes',
    'Size of RPC responses in bytes',
    ['method']
)

# ============ DECORATORS ============

def track_rpc_duration(method_name: str):
    """
    Декоратор для отслеживания длительности RPC вызовов
    
    Args:
        method_name: Имя RPC метода
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                rpc_duration_seconds.labels(method=method_name).observe(duration)
                rpc_requests_total.labels(method=method_name, status=status).inc()
                
        return wrapper
    return decorator


def track_db_query(operation: str, table: str = 'unknown'):
    """
    Декоратор для отслеживания запросов к БД
    
    Args:
        operation: Тип операции (select, insert, update, delete)
        table: Имя таблицы
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(operation=operation).observe(duration)
                db_queries_total.labels(operation=operation, table=table).inc()
                
        return wrapper
    return decorator


def track_cache_operation(operation: str):
    """
    Декоратор для отслеживания операций с кэшем
    
    Args:
        operation: Тип операции (get, set, delete)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Determine result
            if operation == 'get':
                cache_result = 'hit' if result is not None else 'miss'
            else:
                cache_result = 'success' if result else 'failure'
            
            cache_operations_total.labels(
                operation=operation, 
                result=cache_result
            ).inc()
            
            return result
            
        return wrapper
    return decorator


# ============ HELPERS ============

def update_classrooms_gauge(count: int) -> None:
    """Обновить счетчик аудиторий"""
    classrooms_total.set(count)


def update_available_classrooms_gauge(day: int, time_slot: int, count: int) -> None:
    """Обновить счетчик доступных аудиторий"""
    available_classrooms.labels(day=str(day), time_slot=str(time_slot)).set(count)


def update_db_connections_gauge(count: int) -> None:
    """Обновить счетчик активных соединений с БД"""
    db_connections_active.set(count)


def update_cache_hit_rate(hits: int, total: int) -> None:
    """Обновить процент попаданий в кэш"""
    if total > 0:
        rate = (hits / total) * 100
        cache_hit_rate.set(rate)

