"""
API Gateway for DIAN Compliance Platform
Handles routing, CORS, rate limiting, and request/response transformation.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Callable, AsyncGenerator, Union

import httpx
import redis
import structlog
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic_settings import BaseSettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from common.constants import (
    CORRELATION_ID_HEADER,
    APIMessages,
    HealthStatus,
    HTTPStatus,
    ServiceName,
    ServicePort,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"]
)


class Settings(BaseSettings):
    """Application settings."""

    # Service configuration
    service_name: str = "api_gateway"
    service_version: str = "1.0.0"
    environment: str = "development"

    # JWT configuration
    jwt_secret: str = "your-secret-key-change-in-production"

    # Redis configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = "your-redis-password"

    # Service URLs
    auth_service_url: str = "http://auth_service:8001"
    dian_processing_service_url: str = "http://dian_processing_service:8002"
    excel_service_url: str = "http://excel_service:8003"
    pdf_service_url: str = "http://pdf_service:8004"

    # CORS configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"

    # Rate limiting
    default_requests_per_minute: int = 60

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Redis client
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    decode_responses=True,
)

# HTTP client
http_client = httpx.AsyncClient(timeout=30.0)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting API Gateway", service_name=settings.service_name)

    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))

    yield

    logger.info("Shutting down API Gateway")
    await http_client.aclose()


# Create FastAPI application
app = FastAPI(
    title="DIAN Compliance Platform - API Gateway",
    description="Central API Gateway for DIAN Compliance Platform microservices",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts.split(",")
)


@app.middleware("http")
async def add_correlation_id(
    request: Request, call_next: Callable
) -> Union[Response, Any]:
    """Add correlation ID to requests."""
    correlation_id = request.headers.get(CORRELATION_ID_HEADER, str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Add correlation ID to response headers
    response = await call_next(request)
    response.headers[CORRELATION_ID_HEADER] = correlation_id

    return response


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable) -> Union[Response, Any]:
    """Log all requests and responses."""
    start_time = time.time()
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    # Log request
    logger.info(
        "Incoming request",
        method=request.method,
        url=str(request.url),
        correlation_id=correlation_id,
        user_agent=request.headers.get("user-agent"),
        client_ip=request.client.host if request.client else None,
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=duration,
        correlation_id=correlation_id,
    )

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(method=request.method, endpoint=request.url.path).observe(
        duration
    )

    return response


@app.middleware("http")
async def rate_limit_middleware(
    request: Request, call_next: Callable
) -> Union[Response, Any]:
    """Rate limiting middleware."""
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}"

    try:
        # Check rate limit
        current_requests = redis_client.get(key)
        if (
            current_requests
            and int(str(current_requests)) >= settings.default_requests_per_minute
        ):
            logger.warning(
                "Rate limit exceeded",
                client_ip=client_ip,
                correlation_id=getattr(request.state, "correlation_id", "unknown"),
            )
            return JSONResponse(
                status_code=429, content={"detail": "Rate limit exceeded"}
            )

        # Increment request count
        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # 1 minute window
        pipe.execute()

    except Exception as e:
        # Only log error if not in testing environment
        if settings.environment != "testing":
            logger.error("Rate limiting error", error=str(e))
        # Continue without rate limiting if Redis is unavailable

    return await call_next(request)


async def get_correlation_id(request: Request) -> str:
    """Get correlation ID from request."""
    return getattr(request.state, "correlation_id", str(uuid.uuid4()))


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis_client.ping()
        redis_status = HealthStatus.HEALTHY
    except Exception:
        redis_status = HealthStatus.UNHEALTHY

    # Check downstream services
    services_status = {}

    for service_name, service_url in [
        ("auth_service", settings.auth_service_url),
        ("dian_processing_service", settings.dian_processing_service_url),
        ("excel_service", settings.excel_service_url),
        ("pdf_service", settings.pdf_service_url),
    ]:
        try:
            response = await http_client.get(f"{service_url}/health")
            services_status[service_name] = (
                HealthStatus.HEALTHY
                if response.status_code == 200
                else HealthStatus.UNHEALTHY
            )
        except Exception:
            services_status[service_name] = HealthStatus.UNHEALTHY

    overall_status = HealthStatus.HEALTHY
    if (
        any(status == HealthStatus.UNHEALTHY for status in services_status.values())
        or redis_status == HealthStatus.UNHEALTHY
    ):
        overall_status = HealthStatus.DEGRADED

    return {
        "status": overall_status,
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "dependencies": {"redis": redis_status, **services_status},
        "timestamp": time.time(),
    }


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Service routing
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_service_proxy(
    request: Request, path: str, correlation_id: str = Depends(get_correlation_id)
) -> Response:
    """Proxy requests to Auth Service."""
    return await proxy_request(request, settings.auth_service_url, path, correlation_id)


@app.api_route("/dian/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def dian_service_proxy(
    request: Request, path: str, correlation_id: str = Depends(get_correlation_id)
) -> Response:
    """Proxy requests to DIAN Processing Service."""
    return await proxy_request(
        request, settings.dian_processing_service_url, path, correlation_id
    )


@app.api_route("/excel/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def excel_service_proxy(
    request: Request, path: str, correlation_id: str = Depends(get_correlation_id)
) -> Response:
    """Proxy requests to Excel Service."""
    return await proxy_request(
        request, settings.excel_service_url, path, correlation_id
    )


@app.api_route("/pdf/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def pdf_service_proxy(
    request: Request, path: str, correlation_id: str = Depends(get_correlation_id)
) -> Response:
    """Proxy requests to PDF Service."""
    return await proxy_request(request, settings.pdf_service_url, path, correlation_id)


async def proxy_request(
    request: Request, service_url: str, path: str, correlation_id: str
) -> Response:
    """Proxy request to downstream service."""
    target_url = f"{service_url}/{path}"

    # Prepare headers
    headers = dict(request.headers)
    headers[CORRELATION_ID_HEADER] = correlation_id

    # Remove host header to avoid conflicts
    headers.pop("host", None)

    try:
        # Forward request
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )

        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except httpx.RequestError as e:
        logger.error(
            "Service request failed",
            service_url=service_url,
            path=path,
            error=str(e),
            correlation_id=correlation_id,
        )
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail=APIMessages.SERVICE_UNAVAILABLE,
        )


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "DIAN Compliance Platform - API Gateway",
        "version": settings.service_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
