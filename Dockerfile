# Base image with Python and Tesseract
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean

# Set work directory
WORKDIR /app

# Copy your app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Flask
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
