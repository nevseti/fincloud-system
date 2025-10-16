FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install DejaVu fonts for Cyrillic support (used by reportlab)
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY run.py ./run.py

EXPOSE 8002

# Create non-root user and take ownership of the workdir
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck against /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import http.client as h; c=h.HTTPConnection('127.0.0.1',8002,timeout=2); c.request('GET','/health'); r=c.getresponse(); exit(0 if r.status==200 else 1)"

CMD ["python", "run.py"]


