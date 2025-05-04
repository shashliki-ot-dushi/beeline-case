import os
import requests
from .config import YANDEX_API_KEY, YANDEX_MODEL_ID

class YandexGPTClient:
    def __init__(self):
        if not YANDEX_API_KEY:
            raise RuntimeError("Не задан YANDEX_API_KEY")
        self.url = (
            f"https://api.generative.yandexcloud.net/models/"
            f"{YANDEX_MODEL_ID}/generate"
        )
        self.headers = {
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "Content-Type": "application/json"
        }

    def summarize(self, prompt: str, max_tokens: int = 300) -> str:
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.2
        }
        resp = requests.post(self.url, headers=self.headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # В ответе Yandex GPT текст обычно в ['result']['text'] или ['choices'][0]['text']
        return data.get("result", {}).get("text") or data["choices"][0]["text"]
