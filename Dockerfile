FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and agent config.
COPY main.py zerion_client.py storage.py bigquery_loader.py uniblock_client.py rpc_client.py ./
COPY agents.yaml ./

# Workflow: pull from Zerion -> save timestamped JSONs in RECV (staging)
# -> write run log in logs/ -> move JSONs into Archive/.
CMD ["python", "main.py", "--output-dir", "/output/RECV", "--archive-dir", "/output/Archive", "--logs-dir", "/output/logs"]
