FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv
RUN uv venv

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install project and dependencies
RUN uv pip install -e . --system --no-cache-dir

# Run the bot
CMD ["discord-comfyui"]