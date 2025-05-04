FROM python:3.12-slim

# 1) Устанавливаем git и создаём каталог /data
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /data

WORKDIR /app

# 2) Копируем пакет с генератором
COPY autoDoc ./autodoc

# 3) Устанавливаем зависимости
RUN pip install --no-cache-dir fastapi uvicorn gitpython openai

# 4) Чтобы Python мог найти пакет autodoc
ENV PYTHONPATH=/app

EXPOSE 8000

# 5) Запуск FastAPI
CMD ["uvicorn", "autodoc.main:app", "--host", "0.0.0.0", "--port", "8000"]
