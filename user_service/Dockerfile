FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

COPY user_service/pyproject.toml ./pyproject.toml
RUN uv sync

COPY user_service/main.py ./main.py
COPY common ./common

EXPOSE 8000
CMD ["uv", "run", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]