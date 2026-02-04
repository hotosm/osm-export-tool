# OSM Export Tool - Development Dockerfile
# Django + React application for exporting OSM data

# Force linux/amd64 for Mac M1/M2/M3 compatibility (GDAL image lacks ARM64 support)
FROM --platform=linux/amd64 ghcr.io/osgeo/gdal:ubuntu-small-3.8.4 AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and Yarn
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Development stage
FROM base AS development

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip3 install --no-cache-dir -r requirements-dev.txt || pip3 install --no-cache-dir -r requirements.txt
# Force numpy<2.0 for deepdiff compatibility (must be after requirements)
RUN pip3 install --no-cache-dir --force-reinstall "numpy<2.0"

# Install frontend dependencies (cached independently from source code)
COPY ui/package.json ui/yarn.lock* ./ui/
WORKDIR /app/ui
RUN yarn install --frozen-lockfile || yarn install

# Copy application code
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/ui
RUN yarn run dist || yarn run build || echo "Frontend build skipped"

WORKDIR /app

# Create directories for exports
RUN mkdir -p /app/export_staging /app/export_downloads

# Expose port
EXPOSE 8000

# Default command for development
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
