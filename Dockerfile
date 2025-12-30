# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set an environment variable for Python
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Default command to run your bot
# Replace app.py with the main script of your project
CMD ["python", "main.py"]
