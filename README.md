# DIAN Compliance Platform - Microservices Architecture

A production-grade, secure microservices platform for DIAN (Dirección de Impuestos y Aduanas Nacionales) compliance processing in Colombia.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Excel Service  │    │ DIAN Processing │    │   PDF Service   │
│   (FastAPI)     │    │   Service       │    │   (FastAPI)     │
│                 │    │   (FastAPI)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)

### Development Setup

1. **Clone and setup environment:**
```bash
git clone <your-repo>
cd excel-to-dian
cp .env.example .env
# Edit .env with your configuration
```

2. **Start all services:**
```bash
make dev
# or
docker-compose up -d
```

3. **Access the application:**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Auth Service: http://localhost:8001
- DIAN Processing: http://localhost:8002
- Excel Service: http://localhost:8003
- PDF Service: http://localhost:8004

## 📁 Project Structure

```
├── api_gateway/           # API Gateway service
├── auth_service/          # Authentication & authorization
├── dian_processing_service/ # DIAN compliance processing
├── excel_service/         # Excel/CSV processing
├── pdf_service/           # PDF generation
├── common/               # Shared utilities
├── tests/                # Test suites
├── infra/                # Infrastructure as Code
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Development orchestration
├── Makefile             # Development commands
└── README.md            # This file
```

## 🔧 Services

### API Gateway (`api_gateway/`)
- **Port:** 8000
- **Purpose:** Central routing, CORS, rate limiting, request/response transformation
- **Features:** JWT validation, request logging, service discovery

### Auth Service (`auth_service/`)
- **Port:** 8001
- **Purpose:** User authentication, authorization, MFA
- **Features:** JWT tokens, Argon2 password hashing, TOTP MFA, role-based access

### DIAN Processing Service (`dian_processing_service/`)
- **Port:** 8002
- **Purpose:** DIAN compliance validation and processing
- **Features:** File encryption, DIAN format validation, secure file handling

### Excel Service (`excel_service/`)
- **Port:** 8003
- **Purpose:** Excel/CSV file processing and validation
- **Features:** Multi-format support, data validation, JSON transformation

### PDF Service (`pdf_service/`)
- **Port:** 8004
- **Purpose:** PDF report generation
- **Features:** Template-based generation, secure storage, download endpoints

## 🔒 Security Features

- **Authentication:** JWT with refresh tokens
- **Password Security:** Argon2 hashing with salt
- **MFA:** TOTP-based two-factor authentication
- **File Security:** Fernet encryption for sensitive files
- **API Security:** Rate limiting, CORS, input validation
- **Infrastructure:** Non-root containers, secrets management

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific service tests
make test-auth
make test-gateway
make test-dian
make test-excel
make test-pdf

# Run integration tests
make test-integration

# Run with coverage
make test-coverage
```

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
make build-prod

# Deploy with Terraform
cd infra/terraform
terraform init
terraform plan
terraform apply
```

### Docker Compose Production
```bash
# Start production stack
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

- **Health Checks:** `/health` endpoint on all services
- **Metrics:** Prometheus metrics on `/metrics` (when enabled)
- **Logging:** Structured JSON logging with correlation IDs
- **API Documentation:** Auto-generated Swagger/OpenAPI docs

## 🔧 Development

### Adding a New Service

1. Create service directory with standard structure
2. Add Dockerfile and requirements.txt
3. Update docker-compose.yml
4. Add service to API Gateway routing
5. Create tests
6. Update CI/CD pipelines

### Code Standards

- **Python:** Black, isort, flake8, mypy
- **TypeScript:** ESLint, Prettier
- **Testing:** pytest with 90%+ coverage
- **Documentation:** Docstrings, README per service

## 📝 API Documentation

Each service provides auto-generated API documentation:
- **Swagger UI:** `http://service:port/docs`
- **ReDoc:** `http://service:port/redoc`
- **OpenAPI JSON:** `http://service:port/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [documentation](docs/)
- Review the [troubleshooting guide](docs/troubleshooting.md)
