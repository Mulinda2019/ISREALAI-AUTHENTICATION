# Use official Python image with specific Debian variant
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (for builds and healthcheck)
RUN apt-get update && apt-get install -y \
    build-essential gcc curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add app code
COPY . .

# Cleanup (optional)
RUN find . -type d -name __pycache__ -exec rm -r {} + || true

# Add non-root user and switch
RUN addgroup --system isrealai && adduser --system --ingroup isrealai isrealai
USER isrealai

# Expose port
EXPOSE 5000

# Healthcheck (optional)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Run
ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]