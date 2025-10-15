FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY run.py ./run.py

ENV FINANCE_DATABASE_URL=postgresql://postgres:postgres@db:5432/finance_db

EXPOSE 8001

CMD ["python", "run.py"]


