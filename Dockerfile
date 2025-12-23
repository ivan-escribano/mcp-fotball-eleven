# Dockerfile for Azure App Service
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSPORT=http
ENV HOST=0.0.0.0
ENV PORT=8000

# Install dependencies (using Docker-specific requirements without Windows packages)
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check for Azure
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the server
CMD ["python", "-m", "main"]
