FROM python:3.10-slim

LABEL maintainer="Your Name <your.email@example.com>"
LABEL description="Copilot TUI - Terminal User Interface for multi-turn conversations with Microsoft Copilot"
LABEL version="0.1.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY main.py .
COPY config.py . 2>/dev/null || true

# Create conversations directory
RUN mkdir -p /app/conversations

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV COPILOT_API_KEY=""
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from copilot_tui.models import Message, Conversation; print('OK')" || exit 1

# Run the application
ENTRYPOINT ["python", "-u", "main.py"]
CMD []

# Document volume mount point
VOLUME ["/app/conversations"]

# Default to no port exposure (TUI app), but allow override
# EXPOSE 8000
