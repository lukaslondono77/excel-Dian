"""
Shared constants for DIAN Compliance Platform microservices.
"""

import os
from enum import Enum
from typing import List

# Service Names
class ServiceName(str, Enum):
    API_GATEWAY = "api_gateway"
    AUTH_SERVICE = "auth_service"
    DIAN_PROCESSING = "dian_processing_service"
    EXCEL_SERVICE = "excel_service"
    PDF_SERVICE = "pdf_service"


# Service Ports
class ServicePort(int, Enum):
    API_GATEWAY = 8000
    AUTH_SERVICE = 8001
    DIAN_PROCESSING = 8002
    EXCEL_SERVICE = 8003
    PDF_SERVICE = 8004


# HTTP Status Codes
class HTTPStatus(int, Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# File Types
class FileType(str, Enum):
    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"
    JSON = "json"


# Supported File Extensions
SUPPORTED_EXCEL_EXTENSIONS: List[str] = [".xlsx", ".xls", ".xlsm"]
SUPPORTED_CSV_EXTENSIONS: List[str] = [".csv"]
SUPPORTED_PDF_EXTENSIONS: List[str] = [".pdf"]


# DIAN Constants
class DIANConstants:
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_MIME_TYPES = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
        "application/pdf",
    ]

    # DIAN Document Types
    FORMATO_1001 = "1001"
    FORMATO_1002 = "1002"
    FORMATO_1003 = "1003"
    FORMATO_1004 = "1004"
    FORMATO_1005 = "1005"
    FORMATO_1006 = "1006"
    FORMATO_1007 = "1007"
    FORMATO_1008 = "1008"
    FORMATO_1009 = "1009"
    FORMATO_1010 = "1010"


# Security Constants
class SecurityConstants:
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 24
    JWT_REFRESH_EXPIRY_DAYS = 30
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    MFA_ISSUER = "DIAN Compliance Platform"
    MFA_DIGITS = 6
    MFA_PERIOD = 30


# Rate Limiting
class RateLimitConstants:
    DEFAULT_REQUESTS_PER_MINUTE = 60
    AUTH_REQUESTS_PER_MINUTE = 10
    FILE_UPLOAD_REQUESTS_PER_MINUTE = 20


# Database Constants
class DatabaseConstants:
    DEFAULT_POOL_SIZE = 10
    MAX_POOL_SIZE = 20
    POOL_TIMEOUT = 30
    CONNECTION_TIMEOUT = 10


# Logging Constants
class LoggingConstants:
    DEFAULT_LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    JSON_LOG_FORMAT = {
        "timestamp": "%(asctime)s",
        "level": "%(levelname)s",
        "logger": "%(name)s",
        "message": "%(message)s",
        "service": "%(service)s",
        "correlation_id": "%(correlation_id)s",
    }


# Environment Variables
class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


# API Response Messages
class APIMessages:
    # Success Messages
    SUCCESS = "Operation completed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"

    # Error Messages
    INVALID_CREDENTIALS = "Invalid username or password"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "Access forbidden"
    NOT_FOUND = "Resource not found"
    VALIDATION_ERROR = "Validation error"
    INTERNAL_ERROR = "Internal server error"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"

    # File Processing Messages
    FILE_UPLOADED = "File uploaded successfully"
    FILE_PROCESSED = "File processed successfully"
    FILE_TOO_LARGE = "File size exceeds maximum limit"
    INVALID_FILE_TYPE = "Invalid file type"
    FILE_NOT_FOUND = "File not found"

    # DIAN Specific Messages
    DIAN_VALIDATION_SUCCESS = "DIAN validation completed successfully"
    DIAN_VALIDATION_ERROR = "DIAN validation failed"
    DIAN_FORMAT_ERROR = "File does not conform to DIAN format requirements"


# Correlation ID Header
CORRELATION_ID_HEADER = "X-Correlation-ID"

# Health Check Constants
class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


# Metrics Constants
class MetricsConstants:
    REQUEST_COUNT = "http_requests_total"
    REQUEST_DURATION = "http_request_duration_seconds"
    ACTIVE_CONNECTIONS = "http_active_connections"
    ERROR_COUNT = "http_errors_total"
