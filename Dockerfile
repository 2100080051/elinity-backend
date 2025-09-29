# Use the official Python image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ARG CACHE_BUSTER=1

# Create a non-root user called appuser
RUN useradd -m -d /home/appuser -s /bin/bash appuser
 
# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --default-timeout=1000 --retries 10 -r requirements.txt



# Copy app code
COPY . /app

# Expose the necessary port
EXPOSE 8081

# Copy code
COPY . /app

# Copy Firebase credentials JSON
# Make sure keys directory exists
RUN mkdir -p /app/keys

# Copy Firebase credentials into container
COPY keys/firebase.json /app/keys/firebase.json