"""
Prometheus Metrics
Метрики для мониторинга микросервиса аутентификации
"""

from prometheus_client import Counter, Histogram, Gauge


# ============ COUNTERS ============

# Регистрации
registrations_total = Counter(
    'registrations_total',
    'Total registrations',
    ['status']
)

# Логины
logins_total = Counter(
    'logins_total',
    'Total login attempts',
    ['status']
)

# RPC requests
rpc_requests_total = Counter(
    'rpc_requests_total',
    'Total number of RPC requests',
    ['method', 'status']
)

# Token validations
token_validations_total = Counter(
    'token_validations_total',
    'Total token validations',
    ['result']
)

# ============ HISTOGRAMS ============

# RPC request duration
rpc_duration_seconds = Histogram(
    'rpc_duration_seconds',
    'Duration of RPC requests in seconds',
    ['method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# Auth operation duration
auth_duration_seconds = Histogram(
    'auth_duration_seconds',
    'Auth operation duration',
    ['operation'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)
)

# ============ GAUGES ============

# Active users
active_users_total = Gauge(
    'active_users_total',
    'Number of active users'
)

# Valid tokens
valid_tokens_total = Gauge(
    'valid_tokens_total',
    'Number of valid refresh tokens'
)

# Locked accounts
locked_accounts_total = Gauge(
    'locked_accounts_total',
    'Number of locked accounts'
)

