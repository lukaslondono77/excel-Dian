# Frontend Deployment Guide

## Option 1: Deploy to Netlify (Recommended)

### Step 1: Install Netlify CLI
```bash
npm install -g netlify-cli
```

### Step 2: Login to Netlify
```bash
netlify login
```

### Step 3: Deploy
```bash
netlify deploy --prod --dir=frontend/build
```

## Option 2: Deploy to Vercel

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy
```bash
vercel --prod
```

## Option 3: Deploy to GitHub Pages

### Step 1: Add homepage to package.json
Add this to `frontend/package.json`:
```json
{
  "homepage": "https://yourusername.github.io/excel-to-dian"
}
```

### Step 2: Install gh-pages
```bash
cd frontend
npm install --save-dev gh-pages
```

### Step 3: Add deploy script to package.json
```json
{
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d build"
  }
}
```

### Step 4: Deploy
```bash
npm run deploy
```

## Option 4: Deploy to Render (Static Site)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Static Site"
3. Connect your GitHub repository
4. Set build command: `cd frontend && npm install && npm run build`
5. Set publish directory: `frontend/build`
6. Deploy!

## Environment Configuration

The frontend is configured to automatically use the correct API endpoints:
- **Development**: Uses `localhost:8003` for DIAN service and `localhost:8000` for gateway
- **Production**: Uses `https://excel-dian.onrender.com` for both services

## Testing the Deployment

After deployment, test these features:
1. **DIAN Processing Tab**: Upload Excel/CSV files and process them
2. **Excel to PDF Tab**: Upload Excel files and generate PDFs
3. **Date filtering**: Set date ranges for DIAN processing
4. **Consolidation options**: Test monthly, account, NIT, and document type breakdowns

## Troubleshooting

### CORS Issues
If you encounter CORS errors, make sure your backend (Render deployment) has the correct CORS configuration.

### API Connection Issues
Verify that the deployed backend URL is correct in `frontend/src/config.js`.

### Build Issues
Make sure all dependencies are installed:
```bash
cd frontend
npm install
npm run build
``` 