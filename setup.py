"""
Setup script for DIAN Compliance Platform common package.
"""

from setuptools import find_packages, setup

setup(
    name="dian-compliance-common",
    version="1.0.0",
    description="Common utilities for DIAN Compliance Platform microservices",
    author="DIAN Compliance Platform Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.2",
        "redis>=5.0.1",
        "python-jose[cryptography]>=3.3.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "prometheus-client>=0.19.0",
        "structlog>=23.2.0",
        "python-json-logger>=2.0.7",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4.1",
            "pytest-cov>=6.2.1",
            "pytest-asyncio>=1.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "bandit>=1.7.0",
        ],
    },
)
