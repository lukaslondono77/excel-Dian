#!/bin/bash

# Build script for frontend deployment
set -e

echo "Starting frontend build process..."

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building the application..."
npm run build

echo "Frontend build completed successfully!"
echo "Build output is in: frontend/build/" 