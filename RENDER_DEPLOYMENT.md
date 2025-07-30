# 🚀 Render Deployment Guide

## 📋 Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **PostgreSQL Database**: You'll need a database (Render provides this)

## 🔧 Step-by-Step Deployment

### Step 1: Create a PostgreSQL Database on Render

1. Go to your Render dashboard
2. Click "New" → "PostgreSQL"
3. Configure:
   - **Name**: `dian-database`
   - **Database**: `dian_saas`
   - **User**: `dian_user`
   - **Plan**: Free (for testing)
4. Copy the connection details

### Step 2: Deploy the DIAN Processing Service

1. Go to your Render dashboard
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

#### Basic Settings:
- **Name**: `dian-processing-service`
- **Environment**: `Docker`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty (root)
- **Dockerfile Path**: `./Dockerfile`

#### Environment Variables:
```
JWT_SECRET=your-super-secret-jwt-key-here
DB_HOST=your-postgres-host-from-step-1
DB_NAME=dian_saas
DB_USER=your-postgres-user
DB_PASSWORD=your-postgres-password
DB_PORT=5432
PORT=8003
```

### Step 3: Deploy the Frontend (Optional)

1. Create another Web Service
2. Configure:
   - **Name**: `dian-frontend`
   - **Environment**: `Static Site`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`

## 🔍 Troubleshooting Common Issues

### Issue 1: Build Fails
**Error**: `ModuleNotFoundError: No module named 'pandas'`
**Solution**: Make sure `requirements.txt` is in the correct location

### Issue 2: Port Issues
**Error**: `Port already in use`
**Solution**: The Dockerfile uses `$PORT` environment variable from Render

### Issue 3: Database Connection
**Error**: `Connection refused`
**Solution**: 
1. Check database credentials
2. Ensure database is in the same region
3. Verify network access

### Issue 4: JWT Issues
**Error**: `Invalid token`
**Solution**: Set a strong `JWT_SECRET` environment variable

## 📊 Monitoring

- **Logs**: View real-time logs in Render dashboard
- **Health Check**: Service responds to `/health` endpoint
- **Metrics**: Monitor CPU, memory usage

## 🔗 API Endpoints

Once deployed, your service will be available at:
- **Base URL**: `https://your-service-name.onrender.com`
- **Health Check**: `https://your-service-name.onrender.com/health`
- **API Docs**: `https://your-service-name.onrender.com/docs`
- **Root**: `https://your-service-name.onrender.com/`

## 🛠️ Local Testing

Before deploying, test locally:

```bash
# Build the Docker image
docker build -t dian-service .

# Run locally
docker run -p 8003:8003 -e PORT=8003 dian-service
```

## 📝 Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET` | Secret key for JWT tokens | Yes | - |
| `DB_HOST` | PostgreSQL host | Yes | - |
| `DB_NAME` | Database name | Yes | `dian_saas` |
| `DB_USER` | Database user | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `DB_PORT` | Database port | No | `5432` |
| `PORT` | Service port | No | `8003` |

## 🚀 Next Steps

1. Deploy the service
2. Test all endpoints
3. Configure custom domain (optional)
4. Set up monitoring
5. Deploy frontend (if needed) 