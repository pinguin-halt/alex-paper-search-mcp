# Dockerfile for OpenAlex MCP Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and README (needed for package metadata)
COPY alex-paper-search-mcp/pyproject.toml alex-paper-search-mcp/README.md ./
RUN pip install -e .

# Copy the application code
COPY alex-paper-search-mcp/openalex_mcp/ ./openalex_mcp/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp_user && \
    chown -R mcp_user:mcp_user /app
USER mcp_user

# Default command to run the OpenAlex MCP server
CMD ["python", "-m", "openalex_mcp.server"]