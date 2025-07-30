# Excel to DIAN - SaaS Application

A modern microservices-based SaaS application that converts Excel files to DIAN-compliant PDF reports (Libro Mayor - Formato 1007).

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  API Gateway    │    │  PostgreSQL DB  │
│   (Port 3000)   │◄──►│  (Port 8000)    │◄──►│  (Port 5432)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼──────┐    ┌───────▼──────┐
            │Excel Service │    │ PDF Service  │
            │(Port 8001)   │    │(Port 8002)   │
            └──────────────┘    └──────────────┘
```

## 🚀 Features

- **Excel File Processing**: Upload and parse .xlsx/.xls files
- **DIAN Compliance**: Generate Libro Mayor reports in DIAN Format 1007
- **PDF Generation**: Create professional PDF reports with FPDF
- **AWS S3 Integration**: Store generated PDFs in S3
- **Authentication**: JWT-based authentication (Auth0/Firebase ready)
- **Database Storage**: PostgreSQL for metadata and workflow tracking
- **Modern UI**: React + Tailwind CSS with drag-and-drop file upload
- **Microservices**: Scalable architecture with separate services
- **API Gateway**: Centralized orchestration and workflow management

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)
- AWS S3 bucket (optional, for production)

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd excel-to-dian
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```bash
# AWS Configuration (optional for development)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1

# JWT Secret (change in production)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

### 3. Start the Application

```bash
# Start all services
docker-compose up --build

# Or start without S3 mock (recommended for first run)
docker-compose up --build gateway_service excel_service pdf_service postgres frontend
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Excel Service**: http://localhost:8001
- **PDF Service**: http://localhost:8002
- **PostgreSQL**: localhost:5432

## 📁 Project Structure

```
excel-to-dian/
├── docker-compose.yml          # Main orchestration file
├── README.md                   # This file
├── .env                        # Environment variables
├── excel_service/              # Excel parsing microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── pdf_service/                # PDF generation microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── gateway_service/            # API Gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── frontend/                   # React application
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
├── db/                         # Database schema
│   └── init.sql
└── auth/                       # Authentication config (future)
    └── config.json
```

## 🔧 Development

### Local Development Setup

1. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

2. **Backend Services**:
   ```bash
   # Excel Service
   cd excel_service
   pip install -r requirements.txt
   python main.py

   # PDF Service
   cd pdf_service
   pip install -r requirements.txt
   python main.py

   # Gateway Service
   cd gateway_service
   pip install -r requirements.txt
   python main.py
   ```

3. **Database**:
   ```bash
   docker run -d \
     --name postgres \
     -e POSTGRES_DB=dian_saas \
     -e POSTGRES_USER=admin \
     -e POSTGRES_PASSWORD=admin123 \
     -p 5432:5432 \
     postgres:15
   ```

### API Endpoints

#### Excel Service (Port 8001)
- `POST /parse_excel` - Upload and parse Excel file
- `GET /health` - Health check

#### PDF Service (Port 8002)
- `POST /generate_pdf` - Generate PDF from Excel data
- `GET /health` - Health check

#### Gateway Service (Port 8000)
- `POST /process_excel_to_pdf` - Complete workflow
- `GET /workflow-history` - Get user workflow history
- `GET /health` - Health check

## 🔐 Authentication

The application uses JWT tokens for authentication. For development, a mock token is included in the frontend. For production:

1. **Auth0 Setup**:
   - Create an Auth0 application
   - Configure JWT settings
   - Update JWT_SECRET in environment

2. **Firebase Setup**:
   - Create Firebase project
   - Enable Authentication
   - Configure JWT settings

## 🗄️ Database Schema

### Tables
- `users` - User information
- `file_uploads` - Excel file metadata
- `pdf_generations` - PDF generation records
- `workflow_logs` - Workflow execution history

### Views
- `file_pdf_summary` - Combined file and PDF data

## 🚀 Deployment

### Production Deployment

1. **Update Environment Variables**:
   ```bash
   JWT_SECRET=your-production-secret
   AWS_ACCESS_KEY_ID=your-production-aws-key
   AWS_SECRET_ACCESS_KEY=your-production-aws-secret
   S3_BUCKET=your-production-bucket
   ```

2. **Deploy with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Or Deploy to Cloud Platforms**:
   - **AWS ECS**: Use provided ECS task definitions
   - **Google Cloud Run**: Deploy individual services
   - **Azure Container Instances**: Use Azure CLI

### Environment-Specific Configurations

- **Development**: Use local Docker Compose
- **Staging**: Use staging environment variables
- **Production**: Use production environment variables and secrets management

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd excel_service && pytest
cd pdf_service && pytest
cd gateway_service && pytest

# Frontend tests
cd frontend && npm test
```

### Test with Sample Data

1. Create a sample Excel file with the following structure:
   ```
   | Account | Description | Debit | Credit | Balance |
   |---------|-------------|-------|--------|---------|
   | 1100    | Cash        | 1000  |        | 1000    |
   | 1200    | Accounts Rec| 500   |        | 500     |
   ```

2. Upload the file through the frontend
3. Generate PDF and verify DIAN compliance

## 🔍 Monitoring and Logging

### Health Checks
- All services expose `/health` endpoints
- Docker Compose includes health checks for PostgreSQL

### Logging
- Services log to stdout/stderr
- Use Docker logs: `docker-compose logs [service-name]`

### Metrics (Future)
- Prometheus metrics endpoints
- Grafana dashboards
- Application performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks
- Update dependencies regularly
- Monitor security advisories
- Backup database regularly
- Monitor AWS S3 usage and costs

### Version Updates
- Follow semantic versioning
- Update CHANGELOG.md
- Test thoroughly before releases
- Provide migration guides for breaking changes 