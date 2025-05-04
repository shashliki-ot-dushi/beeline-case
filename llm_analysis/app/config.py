import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_MODEL_ID = os.getenv("YANDEX_MODEL_ID", "gpt-3.5-large")
