FROM python:3.9-slim

WORKDIR /app

# Если нужен git для клонирования
RUN apt update && apt install -y git

# Сначала ставим зависимости
COPY ingest/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса и общий пакет
COPY ingest/ingest_service.py ./ingest_service.py
COPY common ./common

# Запускаем FastAPI
CMD ["uvicorn", "ingest_service:app", "--host", "0.0.0.0", "--port", "8000"]
