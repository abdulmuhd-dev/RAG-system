FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runtime

# Fix OS base vulnerabilties
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/list7s/*

RUN useradd --create-home --shell /bin/bash appuser

ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

# ✅ Remove build tooling — not needed at runtime
# Eliminates entire class of pip/ensurepip CVEs
RUN rm -rf /usr/local/lib/python3.12/ensurepip \
           /usr/local/lib/python3.12/site-packages/* \
           /usr/local/bin/pip* /usr/local/bin/wheel \
 && rm -rf /opt/venv/lib/python3.12/site-packages/pip \
           /opt/venv/lib/python3.12/site-packages/pip-*.dist-info \
           /opt/venv/bin/pip*

WORKDIR /app

COPY --chown=appuser:appuser app/ ./app/

RUN mkdir -p /app/chroma_db && \
    chown -R appuser:appuser /app/chroma_db

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=30s \
            --retries=3 \
            CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "1", \
     "--timeout", "300", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.main:create_app()"]
