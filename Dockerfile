# Multi-stage build for SPY TA Tracker
FROM node:20-alpine AS frontend-builder

# Build frontend
WORKDIR /app
ARG VITE_API_URL="/"
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile
COPY . .
ENV VITE_API_URL=${VITE_API_URL}
RUN yarn build

# Python backend stage
FROM python:3.11-slim

# Install uv for faster Python package management
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/ ./backend/
WORKDIR /app/backend

# Clean any local virtualenv that may have been copied and install Python deps into system
RUN rm -rf .venv && uv pip install --system -r pyproject.toml

# Copy built frontend files
COPY --from=frontend-builder /app/dist ./static

# Create data directory for SQLite
RUN mkdir -p ./data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

# Start command (bind to $PORT if provided by platform, else 8000)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]