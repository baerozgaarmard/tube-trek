# Tube Trek — Autonomous Agentic Shorts Studio
FROM python:3.11-slim

# Install FFmpeg and base fonts for video compositing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cache dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Ensure output mount directory exists
RUN mkdir -p /app/output

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "make_short.py"]
CMD ["--help"]
