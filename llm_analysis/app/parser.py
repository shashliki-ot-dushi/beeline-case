import os
import shutil
import ast
import tempfile
from git import Repo
from app.yandex_gpt import YandexGPTClient

class RepoParser:
    """
    Клонирует репозиторий, поуровнево суммирует код (функции → файлы → репозиторий)
    с помощью Yandex GPT и возвращает структурированные summary.
    """
    def __init__(self, repo_url: str, clone_dir: str = None):
        self.repo_url = repo_url
        self.clone_dir = clone_dir or tempfile.mkdtemp()
        self.client = YandexGPTClient()
        self.block_summaries = {}
        self.file_summaries = {}

    def clone_repo(self):
        """Клонирует Git-репозиторий в временную папку"""
        Repo.clone_from(self.repo_url, self.clone_dir)

    def cleanup(self):
        """Удаляет временную папку с репозиторием"""
        shutil.rmtree(self.clone_dir, ignore_errors=True)

    def extract_code_blocks(self):
        """
        Ищет в .py-файлах репозитория определения функций, async-функций и классов,
        возвращает список кортежей (key, code), где key = "path:Name".
        """
        blocks = []
        for root, _, files in os.walk(self.clone_dir):
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, self.clone_dir)
                src = open(full, encoding='utf-8').read()
                tree = ast.parse(src)
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        start = node.lineno - 1
                        end = getattr(node, 'end_lineno', None)
                        code_lines = src.splitlines()[start:end]
                        code = '\n'.join(code_lines)
                        key = f"{rel}:{node.name}"
                        blocks.append((key, code))
        return blocks

    def summarize_all(self):
        """
        1) Суммирует каждый кодовый блок (функция/класс)
        2) Группирует их по файлам и суммирует файлы
        3) Дает общий обзор репозитория
        Возвращает dict с keys: block_summaries, file_summaries, repo_summary.
        """
        # 1. Суммирование функций и классов
        for key, code in self.extract_code_blocks():
            prompt = (
                "Дай краткое описание на русском, что делает этот Python-код:\n"
                "```python\n" + code + "\n```"
            )
            summary = self.client.summarize(prompt)
            self.block_summaries[key] = summary.strip()

        # 2. Суммирование на уровне файлов
        grouped = {}
        for key, summ in self.block_summaries.items():
            file_path = key.split(':')[0]
            grouped.setdefault(file_path, []).append((key, summ))
        for file_path, items in grouped.items():
            combined = '\n'.join(f"- {n}: {s}" for n, s in items)
            prompt = (
                f"На основании описаний функций и классов в файле `{file_path}`, "
                "сформулируй краткий обзор содержания файла:\n" + combined
            )
            self.file_summaries[file_path] = self.client.summarize(prompt).strip()

        # 3. Общий обзор всего репозитория
        combined_files = '\n'.join(f"- {f}: {s}" for f, s in self.file_summaries.items())
        prompt = (
            "На основании следующих обзоров файлов, дай общее представление "
            "о структуре и предназначении всего репозитория:\n" + combined_files
        )
        repo_overview = self.client.summarize(prompt).strip()

        return {
            "block_summaries": self.block_summaries,
            "file_summaries": self.file_summaries,
            "repo_summary": repo_overview
        }
