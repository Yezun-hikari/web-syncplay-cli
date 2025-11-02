# Stage 1: Build stage
FROM python:3.11-slim-bookworm AS builder

# Install Syncplay from PyPI
RUN pip install --no-cache-dir syncplay

# Stage 2: Final stage
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/syncplay /usr/local/bin/syncplay


# Copy application code
COPY ./app /app

# Install Python dependencies
RUN pip install --no-cache-dir Flask Flask-SocketIO gunicorn eventlet

# Change ownership to non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "--workers", "1", "--threads", "100", "--bind", "0.0.0.0:8000", "--worker-class", "eventlet", "main:app"]
