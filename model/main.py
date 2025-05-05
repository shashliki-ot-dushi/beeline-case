import os
import json
import httpx
from typing import Any, Dict, List, Optional
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# === OpenAI v1 SDK setup ===
from openai import OpenAI

# Minio client setup (assumed imported and configured elsewhere)
from minio import Minio

# Minio configuration
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "mybucket")
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", ""),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", ""),
    secure=False
)

# Загрузка API-ключа из окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Environment variable OPENAI_API_KEY is not set or empty")

# SOCKS5-прокси (если нужно)
socks_proxy = httpx.Client(proxy="socks5://mathmod:whatever123@62.60.231.70:1080")
openai_client = OpenAI(api_key=OPENAI_API_KEY, http_client=socks_proxy)

MODEL_NAME = "gpt-4.1"
NEO4J_API_URL = "http://84.54.56.225:8000"

app = FastAPI(title="OpenAI o4-mini + Neo4j + Minio Self-Chat Service")

# === Pydantic-модели запросов и ответов ===
class ChatRequest(BaseModel):
    seed_prompt: str
    temperature: float = 0.7
    max_tokens: int = 512

class ChatResponse(BaseModel):
    thoughts: List[Dict[str, Any]]
    answer: str

# === Функция для получения кода из Minio ===
def get_code_from_minio(file_path: str) -> str:
    """Получаем код из Minio по пути файла"""
    try:
        key = f"repository_code/{file_path}"
        response = minio_client.get_object(MINIO_BUCKET, key)
        code = response.read().decode('utf-8')
        print(code)
        return code
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла из Minio: {e}")
        return ""

# === Описание функций для LLM ===
functions = [
    {
        "name": "execute_cypher",
        "description": "Выполнить Cypher-запрос через Neo4j API",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "params": {"type": "object"}}, "required": ["query"]}
    },
    {
        "name": "get_code_from_minio",
        "description": "Получить содержимое файла из Minio по пути",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Путь к файлу внутри bucket 'repository_code'"}
            },
            "required": ["file_path"]
        }
    }
]

# === Helpers для вызова Neo4j API ===
def call_execute_cypher(query: str, params: Dict[str, Any]) -> Dict[str, Any]:
    logs: List[str] = [f"→ POST {NEO4J_API_URL}/cypher", f"  query: {query}", f"  params: {params}"]
    try:
        resp = httpx.post(f"{NEO4J_API_URL}/cypher", json={"query": query, "params": params}, timeout=10)
        data = resp.json()
    except Exception as e:
        logs.append(f"HTTP error: {e}")
        return {"records": [], "logs": logs, "error": str(e)}
    if resp.status_code != 200:
        logs.extend(data.get("logs", []))
        err = data.get("error") or data.get("detail") or f"HTTP {resp.status_code}"
        logs.append(f"API error: {err}")
        return {"records": [], "logs": logs, "error": err}
    logs.extend(data.get("logs", []))
    return {"records": data.get("records", []), "logs": logs}

# === Основная self-chat логика ===
def openai_self_chat_with_db(seed_prompt: str, temperature: float, max_tokens: int) -> ChatResponse:
    history = [
        {
            "role": "system",
            "content": 
                """
                Ты — ассистент с доступом к Neo4j ≥4.x через функции list_labels, list_properties, execute_cypher и к объектному хранилищу MinIO через get_code_from_minio.

                Твоя задача помогать людям анализировать репозиторий GitHub и отвечать на вопросы о нём. Вся информация находится в подключенных к тебе сервисах.

                Если вопрос не касается репозитория, скажи, что отвечаешь только по вопросам, связанным с репозиторием.

                Если пользователь задаёт вопрос об элементе без указания, это класс, функция или переменная и т. д., начинай поиск в таком порядке:

                Сначала среди классов

                Затем среди функций

                Затем среди переменных

                Затем среди атрибутов
                Вот структура графа:

                Узлы (Labels) и их свойства:

                Module(id, path)

                Class(id, name, lineno)

                Function(id, name, lineno)

                Type(id, name)

                Variable(id, name, lineno)

                Attribute(id, name, lineno)

                Exception(id, name)

                TestCase(id, name, lineno)

                TestStep(id, lineno)

                Fixture(id)

                DocString(id, text)

                DocFile(id, text)

                OpenAPI(id, data)

                EnvVar(id, value)

                ConfigFile(id, data)

                User(id, email, name)

                Commit(id, hexsha, author, date, message)

                Рёбра (Relationships) и их свойства:

                DEFINES: (Module)->(Class|Function|Variable|Attribute)

                INHERITS: (Class)->(Class)

                RETURNS_TYPE: (Function)->(Type)

                PARAM_TYPE: (Function)->(Type)

                THROWS: (Function)->(Exception)

                IMPORTS: (Module)->(Module)

                HAS_STEP: (TestCase)->(TestStep)

                DEFINES_FIXTURE: (Fixture)->(TestCase)

                DOCS: (DocString|DocFile)->(Module|Class|Function)

                API_IMPLEMENTS: (OpenAPI)->(Function)

                AUTHORED: (User)->(Commit)

                MODIFIES: (Commit)->(Module) с {insertions, deletions, patch}

                Процесс работы:

                При старте любого поиска пути к файлу для заданного класса (Class):
                a) Сначала получай список всех возможных свойств, где может лежать путь:

                list_properties('Class')

                list_properties('File')
                b) Проверяй, что найденное свойство действительно содержит непустое значение:

                всегда добавляй в WHERE условие IS NOT NULL или <> ''
                c) Если среди свойств класса нет подходящего пути или все значения пустые/NULL, сразу переключайся на связанный узел File:
                MATCH (c:Class {name: $className})-[:AUTHORED|MODIFIES*1..2]->(f:File)
                WHERE f.path IS NOT NULL AND f.path <> ''
                RETURN f.path AS file_path
                LIMIT 1
                d) Если и такой запрос не дал результата, модель должна:

                зафиксировать факт отсутствия данных (например, «Узел File с непустым f.path не найден»)

                объяснить, почему именно дальше нельзя искать (нет меток, свойств или связей)

                предложить возможные альтернативы (поиск по другим связям: IMPORTS, альтернативным именам свойств) и попытаться снова

                Во всех запросах:

                всегда использовать LIMIT 1, чтобы быстро получить один результат, но не терять информацию о том, что в БД может быть и больше

                если возникает ошибка синтаксиса или выполнения, ловить её и:
                • логировать текст ошибки,
                • пробовать скорректировать запрос (например, убрать WHERE, проверить имена меток/свойств),
                • если после трёх попыток запрос не удаётся, сообщить: «Не удалось выполнить запрос из-за ошибки: <текст>. Дальнейшие попытки не дали результата.»

                Подтверждение отсутствия данных:

                когда после всех путей поиска (свойства класса → связанные файлы → альт. связи) нет результата, явно вывести:
                «Данных для класса <имя> не найдено. Проверил:
                • свойства Class: …
                • связи AUTHORED/MODIFIES*1..2 к File: …
                • связи IMPORTS: …
                Возможных путей больше нет.»

                Подгрузка содержимого файлов:

                если требуется посмотреть внутренности файла, используй get_code_from_minio(f.path)

                заранее проверяй, что f.path — корректный ключ в MinIO

                если get_code_from_minio возвращает ошибку или пустое содержимое, зафиксировать причину и сообщить:
                «Не удалось получить код из MinIO по пути <путь>: <текст ошибки или “пустое содержимое”>»

                Свобода исследования:

                можешь дополнять цепочку связей IMPORTS, MODIFIES, AUTHORED в произвольном порядке и глубине до 2, чтобы найти файл

                всегда проверяй новый путь на наличие корректного непустого пути

                при любом «сливе» (NULL, ошибка, отсутствие узлов) — фиксируй и переходи к следующему сценарию

                Формат ответов:

                по каждому действию кратко указывай, какой запрос был выполнен и почему (успех/провал)

                в конце — окончательный результат: путь к файлу или доказательство отсутствия данных

                Добавленная логика поиска по типу сущности без явного указания:
                Если пользователь не указывает, к какому типу относится элемент (класс, функция и т.д.), модель последовательно ищет сначала среди классов, затем функций, затем переменных, затем атрибутов. Файлы при этом не трогаются напрямую, если они не были явно запрошены пользователем.

                """
        },
        {"role": "user", "content": seed_prompt},
    ]

    final_answer = ""
    while True:
        resp = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=history,
            temperature=temperature,
            max_tokens=max_tokens,
            functions=functions,
            function_call="auto"
        )
        msg = resp.choices[0].message
        # Если модель вызывает функцию
        if getattr(msg, "function_call", None):
            fn = msg.function_call.name
            args = json.loads(msg.function_call.arguments or "{}")
            history.append({"role": "assistant", "name": fn, "content": None, "function_call": {"name": fn, "arguments": msg.function_call.arguments}})

            if fn == "list_labels":
                result = call_execute_cypher("CALL db.labels() YIELD label RETURN label", {})
            elif fn == "list_properties":
                label = args.get("label")
                query = f"MATCH (n:`{label}`) UNWIND keys(n) AS k RETURN DISTINCT k"
                result = call_execute_cypher(query, {})
            elif fn == "execute_cypher":
                result = call_execute_cypher(args["query"], args.get("params", {}))
            elif fn == "get_code_from_minio":
                code = get_code_from_minio(args.get("file_path", ""))
                result = {"code": code}
            else:
                result = {"error": f"Unknown function {fn}"}

            history.append({"role": "function", "name": fn, "content": json.dumps(result)})
            continue

        # Финальный ответ
        final_answer = msg.content.strip() if msg.content else ""
        history.append({"role": "assistant", "content": final_answer})
        break

    return ChatResponse(thoughts=history, answer=final_answer)

@app.post("/self_chat", response_model=ChatResponse)
async def self_chat(req: ChatRequest) -> ChatResponse:
    if not req.seed_prompt:
        raise HTTPException(status_code=400, detail="Empty seed_prompt")
    return openai_self_chat_with_db(req.seed_prompt, req.temperature, req.max_tokens)
