# Deploy Frontend to Render

## Method 1: Using Render Dashboard (Recommended)

### Step 1: Go to Render Dashboard
1. Visit [dashboard.render.com](https://dashboard.render.com)
2. Sign in with your GitHub account

### Step 2: Create New Static Site
1. Click "New" button
2. Select "Static Site"
3. Connect your GitHub repository: `lukaslondono77/excel-Dian`

### Step 3: Configure the Static Site
- **Name**: `excel-dian-frontend`
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/build`
- **Environment**: Static Site
- **Plan**: Free

### Step 4: Environment Variables
Add these environment variables:
- `NODE_VERSION`: `18`

### Step 5: Deploy
Click "Create Static Site" and wait for the build to complete.

## Method 2: Using render.yaml (Blueprint)

### Step 1: Push to GitHub
Make sure your repository is up to date:
```bash
git add .
git commit -m "Add frontend configuration for Render"
git push
```

### Step 2: Use Blueprint
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file
5. Deploy both services at once

## Method 3: Manual Deployment

### Step 1: Create Static Site
1. Go to Render Dashboard
2. Click "New" → "Static Site"
3. Connect your repository

### Step 2: Configure Build Settings
- **Repository**: `lukaslondono77/excel-Dian`
- **Branch**: `main`
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/build`

### Step 3: Environment Variables
- `NODE_VERSION`: `18`

### Step 4: Deploy
Click "Create Static Site"

## After Deployment

### Test Your Application
1. **Frontend URL**: Your frontend will be available at `https://excel-dian-frontend.onrender.com`
2. **Backend URL**: Your backend is at `https://excel-dian.onrender.com`

### Verify Configuration
The frontend is configured to automatically use the correct backend URL:
- **Development**: Uses `localhost:8003`
- **Production**: Uses `https://excel-dian.onrender.com`

### Test Features
1. **DIAN Processing**: Upload Excel/CSV files and process them
2. **Excel to PDF**: Upload Excel files and generate PDFs
3. **Date Filtering**: Set date ranges for processing
4. **Consolidation**: Test monthly, account, NIT, and document type breakdowns

## Troubleshooting

### Build Failures
If the build fails:
1. Check the build logs in Render dashboard
2. Verify all dependencies are in `frontend/package.json`
3. Make sure the build command is correct

### CORS Issues
If you get CORS errors:
1. Check that your backend CORS configuration includes your frontend URL
2. Verify the API endpoints are correct in `frontend/src/config.js`

### API Connection Issues
If the frontend can't connect to the backend:
1. Verify the backend URL in `frontend/src/config.js`
2. Check that the backend service is running
3. Test the backend endpoints directly

## Custom Domain (Optional)

You can add a custom domain to your frontend:
1. Go to your static site settings in Render
2. Click "Custom Domains"
3. Add your domain and configure DNS

## Monitoring

- **Logs**: View build and runtime logs in the Render dashboard
- **Analytics**: Enable analytics in your static site settings
- **Performance**: Monitor load times and performance metrics 