# ── Base ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Metadata
LABEL maintainer="Umair Kashif <kashifumair125@gmail.com>"
LABEL description="Indian Stock Price Prediction — scikit-learn · Streamlit"
LABEL version="1.0.0"

# ── System deps ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────
WORKDIR /app

# ── Python deps (cached layer) ────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── App source ────────────────────────────────────────────────────────
COPY app.py .

# ── Streamlit config ──────────────────────────────────────────────────
RUN mkdir -p /root/.streamlit
COPY .streamlit/config.toml /root/.streamlit/config.toml

# ── Port (Cloud Run uses 8080 by default) ────────────────────────────
ENV PORT=8080
EXPOSE 8080

# ── Health check ──────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/_stcore/health || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8080", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]
