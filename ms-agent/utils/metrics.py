"""
Prometheus Metrics
"""

from prometheus_client import Counter, Histogram, Gauge

# Generation metrics
generations_total = Counter(
    'generations_total',
    'Total generations',
    ['status']
)

generation_duration_seconds = Histogram(
    'generation_duration_seconds',
    'Generation duration',
    ['stage']
)

# RPC metrics
rpc_requests_total = Counter(
    'rpc_requests_total',
    'Total RPC requests',
    ['method', 'status']
)

rpc_duration_seconds = Histogram(
    'rpc_duration_seconds',
    'RPC request duration',
    ['method']
)

# Agent metrics
agent_actions_total = Counter(
    'agent_actions_total',
    'Total agent actions',
    ['action_type', 'success']
)

fitness_score = Gauge(
    'fitness_score',
    'Current fitness score',
    ['generation_id']
)

# LLM metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

llm_duration_seconds = Histogram(
    'llm_duration_seconds',
    'LLM request duration',
    ['model']
)

