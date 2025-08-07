"""
Basic integration tests for DIAN Compliance Platform.
"""

import pytest
from fastapi.testclient import TestClient

from api_gateway.main import app

client = TestClient(app)


class TestBasicIntegration:
    """Basic integration tests that don't require external services."""

    def test_health_check_integration(self):
        """Test health check endpoint in integration environment."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "api_gateway"
        assert "status" in data

    def test_root_endpoint_integration(self):
        """Test root endpoint in integration environment."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "DIAN Compliance Platform - API Gateway"
        assert "version" in data

    def test_metrics_endpoint_integration(self):
        """Test metrics endpoint in integration environment."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "http_requests_total" in response.text

    def test_cors_headers_integration(self):
        """Test CORS headers in integration environment."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-credentials" in response.headers

    def test_correlation_id_integration(self):
        """Test correlation ID functionality in integration environment."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] is not None
