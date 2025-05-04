# autodoc/generator.py
"""Автогенератор Markdown‑документации.

* Собирает структуру проектов на Python.
* Если docstring отсутствует, формирует краткое описание через OpenAI Chat GPT‑4o.
* Обрабатывает файлы параллельно для скорости.
* Чтобы работало, выстави переменную окружения **OPENAI_API_KEY**.
  Опционально — **OPENAI_MODEL** (по‑умолчанию ``gpt-4o-mini``).
"""
from __future__ import annotations

import ast
import os
import textwrap
import concurrent.futures as _fut
from pathlib import Path
from typing import Iterable, List

import openai

# ──────────────────────────  конфигурация  ───────────────────────────
openai.api_key = os.getenv("OPENAI_API_KEY")
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_MAX_SRC_CHARS = int(os.getenv("SRC_SNIPPET_CHARS", "2000"))  # сколько символов кода слать LLM
_CONCURRENCY = int(os.getenv("DOC_THREADS", "8"))             # потоков при генерации

GITHUB_BASE = os.getenv("REPO_WEB_BASE", "").rstrip("/")
MD_HEADER = "# Сгенерированная документация\n"

# ──────────────────────────  утилиты  ────────────────────────────────

def _rel_link(repo_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(repo_root)
    return f"[`{rel}`]({GITHUB_BASE}/{rel})" if GITHUB_BASE else f"`{rel}`"


def _sig(node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    args = [a.arg for a in node.args.args]
    if node.args.vararg:
        args.append("*" + node.args.vararg.arg)
    if node.args.kwarg:
        args.append("**" + node.args.kwarg.arg)
    return f"{node.name}({', '.join(args)})"

client = openai.OpenAI() 


def _llm_summary(kind: str, name: str, src: str) -> str:
    if not openai.api_key:
        return "_Докстрока отсутствует._"
    try:
        rsp = client.chat.completions.create(
            model=_MODEL,
            messages=[{"role": "user",
                       "content": f"Сжато опиши назначение {kind} '{name}'.\\n\\n{src[:_MAX_SRC_CHARS]}"}],
            temperature=0.2,
        )
        return rsp.choices[0].message.content.strip()
    except Exception as exc:
        return f"_Автогенерация не удалась: {exc}_"

# ──────────────────────────  главный сборщик  ─────────────────────────

def _process_file(repo_root: Path, path: Path) -> str:
    """Возвращает Markdown‑блок для одного .py файла."""
    with path.open(encoding="utf-8") as fh:
        src = fh.read()
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return f"## Модуль {_rel_link(repo_root, path)} — синтаксическая ошибка: {exc}\n"

    parts: List[str] = [f"## Модуль {_rel_link(repo_root, path)}\n"]
    mod_doc = ast.get_docstring(tree) or _llm_summary("модуля", path.stem, src)
    parts.append(textwrap.dedent(mod_doc) + "\n")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            cls_doc = ast.get_docstring(node) or _llm_summary("класса", node.name, ast.get_source_segment(src, node))
            parts.append(f"### Класс `{node.name}`\n\n{textwrap.dedent(cls_doc)}\n")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = _sig(node)
            fn_doc = ast.get_docstring(node) or _llm_summary("функции", sig, ast.get_source_segment(src, node))
            parts.append(f"### Функция `{sig}`\n\n{textwrap.dedent(fn_doc)}\n")
    return "".join(parts)


def collect_docs(repo_root: str | Path, out_path: str | Path) -> None:
    repo_root = Path(repo_root).resolve()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    py_files: List[Path] = sorted(repo_root.rglob("*.py"))

    md_chunks: List[str] = [MD_HEADER]
    with _fut.ThreadPoolExecutor(max_workers=_CONCURRENCY) as pool:
        for chunk in pool.map(lambda p: _process_file(repo_root, p), py_files):
            md_chunks.append(chunk)

    out_path.write_text("\n".join(md_chunks), encoding="utf-8")
