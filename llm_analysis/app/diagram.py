from typing import Dict, Any
from app.yandex_gpt import YandexGPTClient

class DiagramBuilder:
    """
    Принимает summary от RepoParser и строит C4-диаграмму с обогащенными описаниями через Yandex GPT.
    """
    def __init__(self, summary: Dict[str, Any]):
        self.summary = summary
        self.client = YandexGPTClient()

    def build_c4(self) -> Dict[str, Any]:
        containers = []
        components = []
        relationships = []

        # 1) Контейнеры: файлы репозитория
        for file_path, file_desc in self.summary.get("file_summaries", {}).items():
            containers.append({
                "id": file_path,
                "name": file_path,
                "description": ""
            })

        # 2) Компоненты: функции и классы
        for block_key, block_desc in self.summary.get("block_summaries", {}).items():
            file_path, name = block_key.split(":", 1)
            components.append({
                "id": block_key,
                "name": name,
                "description": "",
                "containerId": file_path
            })
            # связь "содержит"
            relationships.append({
                "source": block_key,
                "destination": file_path,
                "description": "содержит"
            })

        # 3) Обогащение описаний контейнеров (файлов)
        for c in containers:
            prompt = (
                f"Дай краткое описание на русском, для чего файл `{c['name']}`. "
                "Отметь ключевые функции и классы, которые в нём находятся."
            )
            c["description"] = self.client.summarize(prompt).strip()

        # 4) Обогащение описаний компонентов (функций/классов)
        for comp in components:
            prompt = (
                f"Что делает { 'класс' if ':' in comp['id'].split(':')[0] else 'функция' } "
                f"`{comp['name']}` в файле `{comp['containerId']}`?"
            )
            comp["description"] = self.client.summarize(prompt).strip()

        return {
            "containers": containers,
            "components": components,
            "relationships": relationships
        }
