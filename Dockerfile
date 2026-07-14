
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS runtime

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages \
                    /usr/local/lib/python3.12/site-packages

COPY --from=builder /usr/local/bin /usr/local/bin

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
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.main:create_app()"]
