# ---- Builder stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
COPY pyproject.toml ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir .

# Install the app itself (editable not needed in container)
COPY retschat/ ./retschat/
COPY app.py ./
RUN /opt/venv/bin/pip install --no-cache-dir .

# ---- Runtime stage ----
FROM python:3.12-slim

LABEL maintainer="anderskeis"
LABEL description="DK-Law-AI – Chat interface for Danish law"

# Create non-root user
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --create-home app

WORKDIR /app

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY app.py ./
COPY retschat/ ./retschat/
COPY .streamlit/ ./.streamlit/
COPY .env.example ./

# Streamlit config: headless, disable CORS for LAN, disable gather usage stats
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Healthcheck against the Streamlit health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

USER app

CMD ["streamlit", "run", "app.py"]
