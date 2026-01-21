# Use official Python image as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up apt cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application code into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV FLASK_ENV=production

# Expose application port
EXPOSE 8402

# Run migration then start Gunicorn
CMD python migrate_db.py && gunicorn main:app --workers=5 --threads=2 --bind=0.0.0.0:8402 --timeout=30 --access-logfile -
