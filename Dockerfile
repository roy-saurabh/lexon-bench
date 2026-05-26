FROM python:3.11-slim

LABEL maintainer="roy@affectlog.com"
LABEL description="LEXON-Bench: Executable AI Regulatory Obligation Reasoning"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /workspace

# Install uv
RUN pip install --no-cache-dir uv==0.4.29

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY scripts/ scripts/
COPY rules/ rules/
COPY configs/ configs/
COPY data/raw/ data/raw/
COPY tests/ tests/

# Install dependencies
RUN uv sync --no-dev

# Create output directories
RUN mkdir -p data/processed data/splits data/examples \
    outputs/results outputs/tables outputs/figures outputs/reports outputs/audit

# Default: run reproduction pipeline
CMD ["uv", "run", "python", "scripts/reproduce_paper_results.py"]
