# Force linux/amd64 for Mac M1/M2/M3 compatibility (GDAL image lacks ARM64 support)
FROM --platform=linux/amd64 ghcr.io/osgeo/gdal:ubuntu-small-3.8.4 AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
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
RUN pip3 install --no-cache-dir -r requirements-dev.txt || pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir "numpy<2.0"

# Install frontend dependencies (cached independently from source code)
COPY ui/package.json ui/yarn.lock* ./ui/
RUN cd /app/ui && yarn install

# Copy application code
COPY . .

# Build frontend
RUN cd /app/ui && (yarn run dist || yarn run build)

# Create directories for exports
RUN mkdir -p /app/export_staging /app/export_downloads

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
