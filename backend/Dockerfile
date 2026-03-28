# Use the official Python slim image for a smaller footprint
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080

# Set the working directory
WORKDIR /app

# Install system dependencies required for psycopg2 and other tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port (Cloud Run uses the PORT env var, but we expose 8080 by default)
EXPOSE $PORT

# Start the application using uvicorn
# We use 0.0.0.0 to listen on all network interfaces
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
