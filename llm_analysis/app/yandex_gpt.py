from __future__ import annotations

import requests
from app.config import YANDEX_API_KEY, YANDEX_FOLDER_ID
from yandex_cloud_ml_sdk import YCloudML

class YandexGPTClient:
    """
    Клиент для работы с Yandex Generative API.
    Использует региональный endpoint ru-central1 для стабильной работы DNS.
    """
    def __init__(self):
        self.sdk = YCloudML(
            folder_id=YANDEX_FOLDER_ID,
            auth=YANDEX_API_KEY,
        )

    def summarize(self, prompt: str, max_tokens: int = 300, temperature: float = 0.2) -> str:
        """
        Отправляет prompt в модель и возвращает сгенерированный текст.
        """
        messages =  [
            {
                "role": "system",
                "text": "Ты виртуальный помощник программиста. Твоя задача максимально подробно описывать структуру кода и зависимости в нем."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
        
        result = (
                self.sdk.models.completions("yandexgpt-32k").configure(temperature=0.5).run(messages)
            ) 
        for alternative in result:
            return alternative.text
        return ""
