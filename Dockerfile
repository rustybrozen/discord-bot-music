# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and clean up
RUN apt update && apt install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first (to leverage Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot script
COPY bot.py .

# Run the bot
CMD ["python", "bot.py"]
