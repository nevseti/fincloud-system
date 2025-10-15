FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY run.py ./run.py

ENV FINANCE_SERVICE_URL=http://finance-service:8001

EXPOSE 8002

CMD ["python", "run.py"]


