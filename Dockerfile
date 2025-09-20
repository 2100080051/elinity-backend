# Use the official Python image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system deps (optional if needed for psycopg2, etc.)
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Render’s dynamic port
EXPOSE 8000

# Start app (Render injects $PORT automatically)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
