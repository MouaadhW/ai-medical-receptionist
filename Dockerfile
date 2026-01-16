FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# ffmpeg, libsndfile1 for audio
# curl for ollama install
# zstd for ollama install (sometimes needed)
# build-essential for compiling some python extensions
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    ffmpeg \
    libsndfile1 \
    zstd \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

# Copy requirement first for caching
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Copy only necessary directories (avoids frontend/ and other garbage)
WORKDIR /app
COPY backend /app/backend
COPY start.sh /app/start.sh

# Ensure start script is executable and has LF endings
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

CMD ["bash", "start.sh"]
