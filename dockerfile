FROM python:3.10

# Install system dependencies required for building C extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    libev-dev \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application files
COPY . .

# Specify the command to run your application
CMD ["python", "app.py"]
