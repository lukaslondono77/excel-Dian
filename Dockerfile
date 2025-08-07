# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY api_gateway/requirements.txt ./api_gateway/
COPY setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r api_gateway/requirements.txt
RUN pip install --no-cache-dir -e .

# Copy application code
COPY api_gateway/ ./api_gateway/
COPY common/ ./common/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
