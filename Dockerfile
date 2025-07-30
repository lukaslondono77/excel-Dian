# Dockerfile for Render deployment - DIAN Processing Service
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY dian_processing_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY dian_processing_service/ .

# Create output directory
RUN mkdir -p dian_reports

# Expose port (Render will set PORT environment variable)
EXPOSE 8003

# Use environment variable for port
CMD ["python", "-c", "import os; import uvicorn; from main import app; port = int(os.environ.get('PORT', 8003)); uvicorn.run(app, host='0.0.0.0', port=port)"] 