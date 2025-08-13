#!/bin/bash
set -e

echo "🏗️ Building SPY TA Tracker for deployment..."

# Install frontend dependencies and build
echo "📦 Installing frontend dependencies..."
yarn install --frozen-lockfile

echo "🔨 Building frontend..."
yarn build

# Copy built files to backend static directory
echo "📁 Copying frontend build to backend..."
mkdir -p backend/static
cp -r dist/* backend/static/

# Navigate to backend and install Python dependencies
echo "🐍 Installing backend dependencies..."
cd backend
uv pip install --system -r pyproject.toml

# Create data directory
mkdir -p data

echo "✅ Build complete! Ready for deployment."