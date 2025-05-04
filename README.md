<img src="https://static.beeline.ru/upload/dpcupload/contents/342/avatarbee_2704.svg" align="right" width="130"/>

# Code Insight

Интеллектуальная система статического анализа кода для автоматического восстановления архитектуры, выявления зависимостей и генерации подробной документации. Проект помогает инженерам быстро понять сложные кодовые базы и снизить риски при миграции и модернизации систем.

## 🎯 Основные возможности

* **Автоматический статический анализ**

  * Клонирование Git-репозиториев и обход исходников
  * Построение графа зависимостей (модули, классы, функции, импорт, вызовы)
* **Генерация архитектурных диаграмм (C4/Mermaid)**
  Конвертация графа в структуру C4 и в удобочитаемый синтаксис Mermaid
* **RAG-поиск по коду**
  Индексация фрагментов кода в MinIO + Qdrant, поиск по семантическим запросам
* **Интеграция с LLM (Yandex GPT)**
  Суммирование и обобщение кода на уровне блоков, файлов и всего репозитория
* **Управление пользователями и проектами** через REST API

## 🛠️ Установка и запуск

### Предварительные требования

* Python ≥ 3.12
* PostgreSQL
* MinIO (или любое S3-совместимое хранилище)
* Qdrant
* Docker & Docker Compose (рекомендуется)
* API-ключ Yandex Cloud для GPT

### Настройка окружения

1. **.env для llm\_analysis/**
   В `llm_analysis/.env` добавьте:

   ```dotenv
   YANDEX_API_KEY=<ваш API-ключ>
   YANDEX_MODEL_ID=gpt-3.5-large
   ```
2. **Основной .env**
   В корне проекта или экспортируйте:

   ```dotenv
   DATABASE_URL=postgresql://user:pass@host:5432/db
   AWS_ENDPOINT_URL=http://minio:9000
   AWS_ACCESS_KEY_ID=<ключ>
   AWS_SECRET_ACCESS_KEY=<секрет>
   AWS_S3_BUCKET=<имя бакета>
   QDRANT_URL=<http://qdrant-host:6333>
   ```

### Запуск сервисов

*(пример с Docker Compose — создайте свой `docker-compose.yml` или запускайте вручную)*

```bash
# Запустить все сервисы в фоне
docker-compose up -d
```

Или вручную:

```bash
# User Service
cd user_service
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# RAG Service
cd ../rag
pip install -r requirements.txt
uvicorn rag_service:app --host 0.0.0.0 --port 8001

# LLM Analysis Service
cd ../llm_analysis
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

При первом запуске **создайте таблицы** в базе данных:

```bash
python - << 'EOF'
from common.database.base import Base, engine
Base.metadata.create_all(bind=engine)
EOF
```

## 💡 Использование

### 1. Аутентификация

Получите токен сессии:

```bash
curl -X POST http://localhost:8000/sessions
```

Ответ:

```json
{"session_token":"<UUID4_TOKEN>"}
```

Используйте заголовок:

```
Authorization: Bearer <UUID4_TOKEN>
```

### 2. Управление проектами

* **Создать проект** (Git-репозиторий):

  ```bash
  curl -X POST http://localhost:8000/projects \
    -H "Authorization: Bearer <TOKEN>" \
    -H "Content-Type: application/json" \
    -d '{"repo_url":"https://github.com/..."}'
  ```
* **Список проектов**:

  ```bash
  curl http://localhost:8000/projects \
    -H "Authorization: Bearer <TOKEN>"
  ```
* **Удалить проект**:

  ```bash
  curl -X DELETE http://localhost:8000/projects/<project_id> \
    -H "Authorization: Bearer <TOKEN>"
  ```

### 3. Поиск по коду (RAG)

```bash
curl -X POST http://localhost:8001/rag-query/<project_id> \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"query":"Как вызвать обновление пользователя?"}'
```

### 4. Генерация диаграммы C4

```bash
curl -X POST http://localhost:8002/generate-diagram \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/..."}'
```

Ответ — JSON с массивами `containers`, `components`, `relationships`.
Для конвертации в Mermaid:

```bash
python to_mermaid.py > diagram.mmd
```

## 🤝 Вклад

PR и issue приветствуются! Пожалуйста, создавайте форки и предлагайте улучшения.

## 📄 Лицензия

MIT License
