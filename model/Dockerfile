FROM python:3.10-slim

WORKDIR /app

COPY model/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY model/main.py ./main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
