# Multi-stage build: Stage 1 - Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY omnicore/dashboard/frontend/package*.json ./
RUN npm ci
COPY omnicore/dashboard/frontend/ ./
RUN npm run build

# Stage 2 - Backend Python Runtime
FROM python:3.12-slim
WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir hatchling fastapi uvicorn pydantic networkx pydantic-settings

# Copy project source code and built frontend assets
COPY . .
COPY --from=frontend-builder /app/omnicore/dashboard/dist /app/omnicore/dashboard/dist

# Install omnicore package
RUN pip install --no-cache-dir -e .

EXPOSE 8001
ENV PORT=8001
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "omnicore.cli.main", "dashboard", "--host", "0.0.0.0", "--port", "8001"]
