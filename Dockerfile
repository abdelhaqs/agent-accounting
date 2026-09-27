FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and agent config.
COPY dag/ ./dag/
COPY config/ ./config/

ENV PYTHONPATH=/app/dag:/app

# Workflow: pull from Uniblock/DeBank & Base RPC -> save timestamped JSONs in RECV (staging)
# -> write run log in logs/ -> move JSONs into Archive/.
CMD ["python", "dag/main.py", "--agents-config", "config/agents.yaml", "--output-dir", "/output/RECV", "--archive-dir", "/output/Archive", "--logs-dir", "/output/logs", "--report-dir", "/output/reports"]
