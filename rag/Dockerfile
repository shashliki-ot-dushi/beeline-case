FROM python:3.9-slim

WORKDIR /app

# Добавляем Git, чтобы gitpython мог работать
RUN apt update && apt install -y git

# Ставим зависимости
COPY rag/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY rag/rag_service.py ./rag_service.py
COPY common ./common

CMD ["uvicorn", "rag_service:app", "--host", "0.0.0.0", "--port", "8000"]
