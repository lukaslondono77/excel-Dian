# DIAN Compliance Platform - Makefile
# Production-grade microservices development and deployment

.PHONY: help dev build test clean deploy-prod deploy-staging

# Default target
help:
	@echo "DIAN Compliance Platform - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  dev              - Start development environment"
	@echo "  dev-build        - Build and start development environment"
	@echo "  dev-logs         - Show development logs"
	@echo "  dev-stop         - Stop development environment"
	@echo ""
	@echo "Building:"
	@echo "  build            - Build all services"
	@echo "  build-prod       - Build production images"
	@echo "  build-service    - Build specific service (SERVICE=name)"
	@echo ""
	@echo "Testing:"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-coverage    - Run tests with coverage"
	@echo "  test-auth        - Test auth service"
	@echo "  test-gateway     - Test API gateway"
	@echo "  test-dian        - Test DIAN processing service"
	@echo "  test-excel       - Test Excel service"
	@echo "  test-pdf         - Test PDF service"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint             - Run linting"
	@echo "  format           - Format code"
	@echo "  security-scan    - Run security scans"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-prod      - Deploy to production"
	@echo "  deploy-staging   - Deploy to staging"
	@echo "  deploy-local     - Deploy locally"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean            - Clean up containers and images"
	@echo "  logs             - Show all logs"
	@echo "  health           - Check service health"
	@echo "  backup           - Create backup"
	@echo "  restore          - Restore from backup"

# Development
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "API Gateway: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev-build:
	@echo "Building and starting development environment..."
	docker-compose up --build -d
	@echo "Development environment built and started!"

dev-logs:
	docker-compose logs -f

dev-stop:
	@echo "Stopping development environment..."
	docker-compose down
	@echo "Development environment stopped!"

# Building
build:
	@echo "Building all services..."
	docker-compose build
	@echo "All services built successfully!"

build-prod:
	@echo "Building production images..."
	docker-compose -f docker-compose.prod.yml build
	@echo "Production images built successfully!"

build-service:
ifndef SERVICE
	@echo "Error: SERVICE variable not set. Usage: make build-service SERVICE=service_name"
	@exit 1
endif
	@echo "Building $(SERVICE)..."
	docker-compose build $(SERVICE)
	@echo "$(SERVICE) built successfully!"

# Testing
test:
	@echo "Running all tests..."
	docker-compose exec api_gateway pytest /app/tests/ || true
	docker-compose exec auth_service pytest /app/tests/ || true
	docker-compose exec dian_processing_service pytest /app/tests/ || true
	docker-compose exec excel_service pytest /app/tests/ || true
	docker-compose exec pdf_service pytest /app/tests/ || true
	@echo "All tests completed!"

test-unit:
	@echo "Running unit tests..."
	docker-compose exec api_gateway pytest /app/tests/unit/ || true
	docker-compose exec auth_service pytest /app/tests/unit/ || true
	docker-compose exec dian_processing_service pytest /app/tests/unit/ || true
	docker-compose exec excel_service pytest /app/tests/unit/ || true
	docker-compose exec pdf_service pytest /app/tests/unit/ || true

test-integration:
	@echo "Running integration tests..."
	docker-compose exec api_gateway pytest /app/tests/integration/ || true

test-coverage:
	@echo "Running tests with coverage..."
	docker-compose exec api_gateway pytest --cov=/app --cov-report=html /app/tests/ || true
	docker-compose exec auth_service pytest --cov=/app --cov-report=html /app/tests/ || true
	docker-compose exec dian_processing_service pytest --cov=/app --cov-report=html /app/tests/ || true
	docker-compose exec excel_service pytest --cov=/app --cov-report=html /app/tests/ || true
	docker-compose exec pdf_service pytest --cov=/app --cov-report=html /app/tests/ || true

test-auth:
	@echo "Testing auth service..."
	docker-compose exec auth_service pytest /app/tests/ || true

test-gateway:
	@echo "Testing API gateway..."
	docker-compose exec api_gateway pytest /app/tests/ || true

test-dian:
	@echo "Testing DIAN processing service..."
	docker-compose exec dian_processing_service pytest /app/tests/ || true

test-excel:
	@echo "Testing Excel service..."
	docker-compose exec excel_service pytest /app/tests/ || true

test-pdf:
	@echo "Testing PDF service..."
	docker-compose exec pdf_service pytest /app/tests/ || true

# Code Quality
lint:
	@echo "Running linting..."
	docker-compose exec api_gateway flake8 /app || true
	docker-compose exec auth_service flake8 /app || true
	docker-compose exec dian_processing_service flake8 /app || true
	docker-compose exec excel_service flake8 /app || true
	docker-compose exec pdf_service flake8 /app || true

format:
	@echo "Formatting code..."
	docker-compose exec api_gateway black /app || true
	docker-compose exec auth_service black /app || true
	docker-compose exec dian_processing_service black /app || true
	docker-compose exec excel_service black /app || true
	docker-compose exec pdf_service black /app || true

security-scan:
	@echo "Running security scans..."
	docker-compose exec api_gateway bandit -r /app || true
	docker-compose exec auth_service bandit -r /app || true
	docker-compose exec dian_processing_service bandit -r /app || true
	docker-compose exec excel_service bandit -r /app || true
	docker-compose exec pdf_service bandit -r /app || true

# Deployment
deploy-prod:
	@echo "Deploying to production..."
	@echo "This will deploy to production environment"
	@echo "Are you sure? (y/N)"
	@read -p "" confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production deployment completed!"

deploy-staging:
	@echo "Deploying to staging..."
	docker-compose -f docker-compose.staging.yml up -d
	@echo "Staging deployment completed!"

deploy-local:
	@echo "Deploying locally..."
	docker-compose up -d
	@echo "Local deployment completed!"

# Maintenance
clean:
	@echo "Cleaning up containers and images..."
	docker-compose down -v
	docker system prune -f
	@echo "Cleanup completed!"

logs:
	docker-compose logs -f

health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "API Gateway: UNHEALTHY"
	@curl -f http://localhost:8001/health || echo "Auth Service: UNHEALTHY"
	@curl -f http://localhost:8002/health || echo "DIAN Processing: UNHEALTHY"
	@curl -f http://localhost:8003/health || echo "Excel Service: UNHEALTHY"
	@curl -f http://localhost:8004/health || echo "PDF Service: UNHEALTHY"

backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@tar -czf backups/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude='.git' \
		--exclude='node_modules' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='backups' \
		.
	@echo "Backup created successfully!"

restore:
ifndef BACKUP_FILE
	@echo "Error: BACKUP_FILE variable not set. Usage: make restore BACKUP_FILE=backup-file.tar.gz"
	@exit 1
endif
	@echo "Restoring from backup $(BACKUP_FILE)..."
	@tar -xzf backups/$(BACKUP_FILE)
	@echo "Restore completed!"

# Database operations
db-migrate:
	@echo "Running database migrations..."
	docker-compose exec postgres psql -U admin -d dian_saas -f /docker-entrypoint-initdb.d/migrate.sql

db-backup:
	@echo "Creating database backup..."
	docker-compose exec postgres pg_dump -U admin dian_saas > backups/db-backup-$(shell date +%Y%m%d-%H%M%S).sql

db-restore:
ifndef DB_BACKUP_FILE
	@echo "Error: DB_BACKUP_FILE variable not set. Usage: make db-restore DB_BACKUP_FILE=backup-file.sql"
	@exit 1
endif
	@echo "Restoring database from $(DB_BACKUP_FILE)..."
	docker-compose exec -T postgres psql -U admin -d dian_saas < backups/$(DB_BACKUP_FILE)

# Monitoring
monitor:
	@echo "Starting monitoring stack..."
	docker-compose -f docker-compose.monitoring.yml up -d
	@echo "Monitoring stack started!"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001"

# Development helpers
shell:
ifndef SERVICE
	@echo "Error: SERVICE variable not set. Usage: make shell SERVICE=service_name"
	@exit 1
endif
	docker-compose exec $(SERVICE) /bin/bash

logs-service:
ifndef SERVICE
	@echo "Error: SERVICE variable not set. Usage: make logs-service SERVICE=service_name"
	@exit 1
endif
	docker-compose logs -f $(SERVICE)

restart-service:
ifndef SERVICE
	@echo "Error: SERVICE variable not set. Usage: make restart-service SERVICE=service_name"
	@exit 1
endif
	docker-compose restart $(SERVICE)
