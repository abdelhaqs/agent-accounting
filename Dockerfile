FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and agent config.
COPY main.py zerion_client.py storage.py ./
COPY agents.yaml ./

# Cloud Run Jobs run the default command.
CMD ["python", "main.py", "--output-dir", "/output"]
