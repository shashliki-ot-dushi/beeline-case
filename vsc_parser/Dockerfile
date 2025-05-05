FROM python:3.9-slim

WORKDIR /app

# Добавляем Git, чтобы gitpython мог работать
RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      build-essential \
      libclang-dev \
&& rm -rf /var/lib/apt/lists/*

# Ставим зависимости
COPY vsc_parser/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY vsc_parser/app ./app
COPY common ./common

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
