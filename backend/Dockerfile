FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building wheels (needed for numpy, torch, etc.)
RUN apt-get update && apt-get install -y build-essential wget curl && rm -rf /var/lib/apt/lists/*

# Copy only requirements first
COPY requirements.txt .

# Install dependencies (cached unless requirements.txt changes)
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
