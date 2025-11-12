FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir matplotlib numpy Pillow

# Copy all project files
COPY . /app

# Default command
CMD ["python", "benchmark.py"]
