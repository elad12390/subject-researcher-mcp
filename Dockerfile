# Enhanced Subject Researcher MCP - Production Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY src/ ./src/
COPY LICENSE ./
COPY ENHANCEMENTS_SUMMARY.md ./
COPY FINAL_PRODUCTION_STATUS.md ./

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash researcher && \
    chown -R researcher:researcher /app
USER researcher

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.subject_researcher_mcp.research_engine import ResearchEngine; print('✅ Health check passed')" || exit 1

# Expose MCP port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "src.subject_researcher_mcp.server"]