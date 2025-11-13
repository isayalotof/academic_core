#!/usr/bin/env python3
"""
Gateway Main Entry Point
Главная точка входа для API Gateway
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse, PlainTextResponse  # noqa: E402
import uvicorn  # noqa: E402
import time  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402

from config import config  # noqa: E402
from routes import (  # noqa: E402
    classrooms, auth, agent, schedule, preferences,
    teachers, groups, students, loads, buildings,
    lms, tickets, events, library, documents, cafeteria
)
from middleware.logging_middleware import LoggingMiddleware  # noqa: E402

# Metrics storage (simple in-memory counter)
request_count = 0
request_duration_sum = 0
start_time = time.time()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============ LIFESPAN ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    import asyncio

    # Startup
    logger.info("=" * 60)
    logger.info("Gateway - API Gateway")
    logger.info(f"Version: {config.SERVICE_VERSION}")
    logger.info(f"Environment: {config.ENVIRONMENT}")
    logger.info(f"API Docs: {config.DOCS_URL}")
    logger.info("=" * 60)

    # Import clients
    from rpc_clients.classroom_client import classroom_client
    from rpc_clients.auth_client import auth_client
    from rpc_clients.agent_client import agent_client
    from rpc_clients.schedule_client import (
        get_schedule_client,
        close_schedule_client
    )
    from rpc_clients.core_client import get_core_client

    # Wait a bit for microservices to start
    logger.info("⏳ Waiting for microservices to start...")
    await asyncio.sleep(5)

    # Check microservices connections with retry
    max_retries = 3
    retry_delay = 2

    def check_schedule():
        return (
            get_schedule_client().health_check().get('status')
            == 'healthy'
        )

    def check_core():
        return (
            get_core_client().health_check().get('status')
            == 'healthy'
        )

    services = {
        'ms-auth': lambda: auth_client.health_check(),
        'ms-audit': lambda: classroom_client.health_check(),
        'ms-agent': lambda: agent_client.health_check(),
        'ms-schedule': check_schedule,
        'ms-core': check_core
    }

    for service_name, health_check_fn in services.items():
        connected = False
        for attempt in range(1, max_retries + 1):
            try:
                if health_check_fn():
                    logger.info(f"✓ Connected to {service_name}")
                    connected = True
                    break
            except Exception:
                if attempt < max_retries:
                    logger.debug(
                        f"⏳ {service_name} not ready yet "
                        f"(attempt {attempt}/{max_retries}), "
                        f"retrying in {retry_delay}s..."
                    )
                    await asyncio.sleep(retry_delay)

        if not connected:
            logger.warning(
                f"⚠️  Failed to connect to {service_name} "
                f"(will continue without it)"
            )

    logger.info("🚀 Gateway is ready to accept requests")

    yield

    # Shutdown
    logger.info("Shutting down Gateway...")

    # Close gRPC connections
    try:
        auth_client.close()
        classroom_client.close()
        agent_client.close()
        close_schedule_client()
    except Exception as e:
        logger.error(f"Error closing connections: {e}")

    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="University Schedule Gateway",
    description="API Gateway для системы составления расписания университета",
    version=config.SERVICE_VERSION,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    openapi_url=config.OPENAPI_URL,
    lifespan=lifespan
)


# ============ MIDDLEWARE ============

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
app.add_middleware(LoggingMiddleware)


# ============ EXCEPTION HANDLERS ============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if config.ENVIRONMENT == 'development' else None
        }
    )


# ============ ROUTES ============

# Include routers
app.include_router(
    auth.router,
    prefix=config.API_PREFIX
)

app.include_router(
    classrooms.router,
    prefix=config.API_PREFIX
)

app.include_router(
    buildings.router,
    prefix=config.API_PREFIX
)

app.include_router(
    agent.router,
    prefix=config.API_PREFIX
)

app.include_router(
    schedule.router,
    prefix=config.API_PREFIX
)

app.include_router(
    preferences.router,
    prefix=config.API_PREFIX
)

app.include_router(
    teachers.router,
    prefix=config.API_PREFIX
)

app.include_router(
    groups.router,
    prefix=config.API_PREFIX
)

app.include_router(
    students.router,
    prefix=config.API_PREFIX
)

app.include_router(
    loads.router,
    prefix=config.API_PREFIX
)

app.include_router(
    lms.router,
    prefix=config.API_PREFIX
)

app.include_router(
    tickets.router,
    prefix=config.API_PREFIX
)

app.include_router(
    events.router,
    prefix=config.API_PREFIX
)

app.include_router(
    library.router,
    prefix=config.API_PREFIX
)

app.include_router(
    documents.router,
    prefix=config.API_PREFIX
)

app.include_router(
    cafeteria.router,
    prefix=config.API_PREFIX
)


# ============ HEALTH CHECK ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from rpc_clients.classroom_client import classroom_client
    from rpc_clients.auth_client import auth_client
    from rpc_clients.agent_client import agent_client
    from rpc_clients.schedule_client import get_schedule_client
    from rpc_clients.core_client import get_core_client

    ms_audit_healthy = classroom_client.health_check()
    ms_auth_healthy = auth_client.health_check()
    ms_agent_healthy = agent_client.health_check()

    ms_schedule_healthy = False
    try:
        schedule_client = get_schedule_client()
        health_result = schedule_client.health_check()
        ms_schedule_healthy = health_result.get('status') == 'healthy'
    except Exception:
        pass

    ms_core_healthy = False
    try:
        core_client = get_core_client()
        health_result = core_client.health_check()
        ms_core_healthy = health_result.get('status') == 'healthy'
    except Exception:
        pass

    all_healthy = (
        ms_audit_healthy and ms_auth_healthy and ms_agent_healthy
        and ms_schedule_healthy and ms_core_healthy
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": config.SERVICE_VERSION,
        "environment": config.ENVIRONMENT,
        "services": {
            "ms-auth": "healthy" if ms_auth_healthy else "unhealthy",
            "ms-audit": "healthy" if ms_audit_healthy else "unhealthy",
            "ms-agent": "healthy" if ms_agent_healthy else "unhealthy",
            "ms-core": "healthy" if ms_core_healthy else "unhealthy",
            "ms-schedule": (
                "healthy" if ms_schedule_healthy else "unhealthy"
            )
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "University Schedule Gateway",
        "version": config.SERVICE_VERSION,
        "docs": config.DOCS_URL,
        "health": "/health"
    }


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    global request_count, request_duration_sum, start_time

    uptime = time.time() - start_time
    version = config.SERVICE_VERSION
    env = config.ENVIRONMENT

    metrics_text = f"""# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total {request_count}

# HELP gateway_uptime_seconds Gateway uptime in seconds
# TYPE gateway_uptime_seconds gauge
gateway_uptime_seconds {uptime:.2f}

# HELP gateway_info Gateway information
# TYPE gateway_info gauge
gateway_info{{version="{version}",environment="{env}"}} 1
"""

    return metrics_text


# ============ MAIN ============


def main():
    """Run application"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.ENVIRONMENT == 'development',
        log_level=config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
