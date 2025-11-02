# Mport - TCP Tunnel Server
# Multi-stage Docker build optimized for Fly.io (256MB RAM)
# Uses Python 3.13 and minimal Alpine Linux

# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirements first (for layer caching)
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage (minimal)
FROM python:3.13-slim

# Create non-root user for security
RUN useradd -m -u 1000 mport

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/mport/.local

# Copy application code
COPY server/ ./server/
COPY client/ ./client/

# Set ownership
RUN chown -R mport:mport /app

# Switch to non-root user
USER mport

# Add local Python packages to PATH
ENV PATH=/home/mport/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Expose ports (Fly.io will handle external mapping)
# 8080: Public port (ADB access)
# 8081: Control port (tunnel management)
# 8082: Tunnel port (data transfer)
EXPOSE 8080 8081 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 8081)); s.close()" || exit 1

# Run the server
CMD ["python", "server/tunnel_server.py", "--host", "0.0.0.0"]
