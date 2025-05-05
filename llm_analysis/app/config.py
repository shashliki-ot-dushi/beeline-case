import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# API-ключ Яндекс Generative API
YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
# Идентификатор папки (Folder ID) в Яндекс Облаке
YANDEX_FOLDER_ID: str = os.getenv("YANDEX_FOLDER_ID", "")

print(YANDEX_API_KEY, YANDEX_FOLDER_ID)
