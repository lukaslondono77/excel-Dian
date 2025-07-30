#!/bin/bash

# Excel to DIAN - Quick Start Script
# This script helps you start the application quickly

set -e

echo "🚀 Excel to DIAN - Quick Start"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ .env file created. Please review and update the configuration if needed."
    else
        echo "⚠️  No env.example found. Creating basic .env file..."
        cat > .env << EOF
# Excel to DIAN - Environment Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1
EOF
    fi
fi

# Function to check if services are ready
check_services() {
    echo "⏳ Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    echo "   - Waiting for PostgreSQL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T postgres pg_isready -U admin -d dian_saas > /dev/null 2>&1; then
            echo "   ✅ PostgreSQL is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        echo "   ❌ PostgreSQL failed to start within 60 seconds"
        return 1
    fi
    
    # Wait for services
    echo "   - Waiting for microservices..."
    services=("gateway_service:8000" "excel_service:8001" "pdf_service:8002")
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        echo "   - Waiting for $service_name..."
        
        timeout=30
        while [ $timeout -gt 0 ]; do
            if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
                echo "   ✅ $service_name is ready"
                break
            fi
            sleep 2
            timeout=$((timeout - 2))
        done
        
        if [ $timeout -le 0 ]; then
            echo "   ❌ $service_name failed to start within 30 seconds"
            return 1
        fi
    done
    
    return 0
}

# Start services
echo "🔧 Starting services..."
docker-compose up --build -d

# Wait for services to be ready
if check_services; then
    echo ""
    echo "🎉 All services are ready!"
    echo ""
    echo "📱 Access the application:"
    echo "   Frontend:     http://localhost:3000"
    echo "   API Gateway:  http://localhost:8000"
    echo "   Excel Service: http://localhost:8001"
    echo "   PDF Service:  http://localhost:8002"
    echo ""
    echo "🔍 Health checks:"
    echo "   Gateway:      http://localhost:8000/health"
    echo "   Excel:        http://localhost:8001/health"
    echo "   PDF:          http://localhost:8002/health"
    echo ""
    echo "📊 Database:"
    echo "   PostgreSQL:   localhost:5432"
    echo "   Database:     dian_saas"
    echo "   User:         admin"
    echo "   Password:     admin123"
    echo ""
    echo "🧪 Run tests:"
    echo "   python test_services.py"
    echo ""
    echo "🛑 To stop services:"
    echo "   docker-compose down"
    echo ""
    echo "📖 For more information, see README.md"
else
    echo ""
    echo "❌ Some services failed to start properly."
    echo "Check the logs with: docker-compose logs"
    echo ""
    echo "🛑 Stopping services..."
    docker-compose down
    exit 1
fi 