# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy the rest of the application
COPY . .

# Expose port (default for many PaaS is 8000 or defined by env)
EXPOSE 8000

# Run the application (interpolating PORT for cloud providers)
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
