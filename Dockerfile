FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system deps
# Added python-is-python3 to ensure 'python' command works
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    python-is-python3 \
    zstd \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Ensure 'pip' command exists (aliased to pip3)
RUN ln -sf /usr/bin/pip3 /usr/bin/pip

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app
COPY . .

RUN chmod +x start.sh

CMD ["bash", "start.sh"]
