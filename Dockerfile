# Multi-stage build for SPY TA Tracker
FROM node:20-alpine AS frontend-builder

# Build frontend
WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn build

# Python backend stage
FROM python:3.11-slim

# Install uv for faster Python package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/ ./backend/
WORKDIR /app/backend

# Install Python dependencies
RUN uv pip install --system -r pyproject.toml

# Copy built frontend files
COPY --from=frontend-builder /app/dist ./static

# Create data directory for SQLite
RUN mkdir -p ./data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/healthz')"

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]