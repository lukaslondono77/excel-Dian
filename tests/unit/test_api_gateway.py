"""
Unit tests for API Gateway service.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from api_gateway.main import app

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check_success(self):
        """Test successful health check."""
        with patch("api_gateway.main.redis_client") as mock_redis, patch(
            "api_gateway.main.http_client"
        ) as mock_http:

            # Mock Redis methods for rate limiting
            mock_redis.get.return_value = "10"  # Normal rate limit count
            mock_pipeline = Mock()
            mock_redis.pipeline.return_value = mock_pipeline
            mock_pipeline.incr.return_value = mock_pipeline
            mock_pipeline.expire.return_value = mock_pipeline
            mock_pipeline.execute.return_value = [11]  # Incremented count
            
            # Mock Redis ping for health check
            mock_redis.ping.return_value = True

            # Mock HTTP responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_http.get.return_value.__aenter__.return_value = mock_response

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "api_gateway"
            assert "dependencies" in data

    def test_health_check_redis_failure(self):
        """Test health check with Redis failure."""
        with patch("api_gateway.main.redis_client") as mock_redis, patch(
            "api_gateway.main.http_client"
        ) as mock_http:

            # Mock Redis methods for rate limiting
            mock_redis.get.return_value = "10"  # Normal rate limit count
            mock_pipeline = Mock()
            mock_redis.pipeline.return_value = mock_pipeline
            mock_pipeline.incr.return_value = mock_pipeline
            mock_pipeline.expire.return_value = mock_pipeline
            mock_pipeline.execute.return_value = [11]  # Incremented count
            
            # Mock Redis failure for health check
            mock_redis.ping.side_effect = Exception("Redis connection failed")

            # Mock HTTP responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_http.get.return_value.__aenter__.return_value = mock_response

            response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["dependencies"]["redis"] == "unhealthy"


class TestMetrics:
    """Test metrics endpoint."""

    @patch("api_gateway.main.redis_client")
    def test_metrics_endpoint(self, mock_redis):
        """Test metrics endpoint returns Prometheus format."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        response = client.get("/metrics")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "http_requests_total" in response.text


class TestRoot:
    """Test root endpoint."""

    @patch("api_gateway.main.redis_client")
    def test_root_endpoint(self, mock_redis):
        """Test root endpoint returns service information."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "DIAN Compliance Platform - API Gateway"
        assert "version" in data
        assert "environment" in data
        assert "docs" in data


class TestCorrelationId:
    """Test correlation ID functionality."""

    @patch("api_gateway.main.redis_client")
    def test_correlation_id_header(self, mock_redis):
        """Test that correlation ID is added to response headers."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        response = client.get("/health")

        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] is not None

    @patch("api_gateway.main.redis_client")
    def test_correlation_id_preserved(self, mock_redis):
        """Test that provided correlation ID is preserved."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        test_correlation_id = "test-correlation-id-123"
        response = client.get(
            "/health", headers={"X-Correlation-ID": test_correlation_id}
        )

        assert response.headers["X-Correlation-ID"] == test_correlation_id


class TestRateLimiting:
    """Test rate limiting functionality."""

    @patch("api_gateway.main.redis_client")
    def test_rate_limit_exceeded(self, mock_redis):
        """Test rate limit exceeded response."""
        # Mock Redis to return rate limit exceeded
        mock_redis.get.return_value = "60"  # Already at limit

        response = client.get("/health")

        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    @patch("api_gateway.main.redis_client")
    def test_rate_limit_normal(self, mock_redis):
        """Test normal rate limiting."""
        # Mock Redis to return normal count
        mock_redis.get.return_value = "10"

        response = client.get("/health")

        # Should not be rate limited
        assert response.status_code != 429


class TestCORS:
    """Test CORS functionality."""

    @patch("api_gateway.main.redis_client")
    def test_cors_headers(self, mock_redis):
        """Test that CORS headers are present."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        response = client.options("/health")

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers


class TestServiceRouting:
    """Test service routing functionality."""

    @patch("api_gateway.main.redis_client")
    @patch("api_gateway.main.http_client")
    def test_auth_service_proxy(self, mock_http, mock_redis):
        """Test auth service proxy routing."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        # Mock successful response
        mock_response = Mock()
        mock_response.content = b'{"message": "success"}'
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_http.request.return_value.__aenter__.return_value = mock_response

        response = client.get("/auth/test-endpoint")

        # Should proxy to auth service
        assert response.status_code == 200

    @patch("api_gateway.main.redis_client")
    @patch("api_gateway.main.http_client")
    def test_dian_service_proxy(self, mock_http, mock_redis):
        """Test DIAN service proxy routing."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        # Mock successful response
        mock_response = Mock()
        mock_response.content = b'{"message": "success"}'
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_http.request.return_value.__aenter__.return_value = mock_response

        response = client.get("/dian/test-endpoint")

        # Should proxy to DIAN service
        assert response.status_code == 200

    @patch("api_gateway.main.redis_client")
    @patch("api_gateway.main.http_client")
    def test_excel_service_proxy(self, mock_http, mock_redis):
        """Test Excel service proxy routing."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        # Mock successful response
        mock_response = Mock()
        mock_response.content = b'{"message": "success"}'
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_http.request.return_value.__aenter__.return_value = mock_response

        response = client.get("/excel/test-endpoint")

        # Should proxy to Excel service
        assert response.status_code == 200

    @patch("api_gateway.main.redis_client")
    @patch("api_gateway.main.http_client")
    def test_pdf_service_proxy(self, mock_http, mock_redis):
        """Test PDF service proxy routing."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        # Mock successful response
        mock_response = Mock()
        mock_response.content = b'{"message": "success"}'
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_http.request.return_value.__aenter__.return_value = mock_response

        response = client.get("/pdf/test-endpoint")

        # Should proxy to PDF service
        assert response.status_code == 200

    @patch("api_gateway.main.redis_client")
    @patch("api_gateway.main.http_client")
    def test_service_unavailable(self, mock_http, mock_redis):
        """Test service unavailable handling."""
        # Mock Redis methods for rate limiting
        mock_redis.get.return_value = "10"  # Normal rate limit count
        mock_pipeline = Mock()
        mock_redis.pipeline.return_value = mock_pipeline
        mock_pipeline.incr.return_value = mock_pipeline
        mock_pipeline.expire.return_value = mock_pipeline
        mock_pipeline.execute.return_value = [11]  # Incremented count

        # Mock service failure
        mock_http.request.side_effect = Exception("Service unavailable")

        response = client.get("/auth/test-endpoint")

        # Should return service unavailable error
        assert response.status_code == 503
        assert "Service temporarily unavailable" in response.json()["detail"]
