FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/

# Install dependencies and build wheel
RUN pip install --no-cache-dir build && \
    python -m build --wheel

# Start fresh with a clean image
FROM python:3.12-slim

WORKDIR /app

# Copy built wheel from builder
COPY --from=builder /app/dist/*.whl .
COPY config.yaml.template config.yaml

# Install the wheel
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Create volume for config
VOLUME /app/config

# Run the bot
CMD ["discord-comfyui"]
