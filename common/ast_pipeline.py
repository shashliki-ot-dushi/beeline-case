import os
import json
import pickle
import ast
import git
from pathlib import Path
import networkx as nx
from sentence_transformers import SentenceTransformer
import faiss

class CacheManager:
    """
    Управление кэшированными AST и метаданными (Git-хеши файлов).
    Если репозиторий недоступен из-за прав, кэширование отключается.
    """
    def __init__(self, repo_path: str, cache_dir: str = ".cache"):
        self.repo_path = Path(repo_path)
        self.cache_dir = self.repo_path / cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            self.repo = git.Repo(repo_path)
        except Exception:
            print(f"[CacheManager] Warning: Не удалось открыть git-репозиторий в {repo_path}, кэш отключен.")
            self.repo = None

    def _cache_path(self, file_path: str) -> Path:
        rel = os.path.relpath(file_path, self.repo_path)
        safe = rel.replace(os.sep, "_") + ".pkl"
        return self.cache_dir / safe

    def is_cached(self, file_path: str) -> bool:
        return self._cache_path(file_path).exists()

    def is_modified(self, file_path: str) -> bool:
        if not self.repo:
            return True
        rel = os.path.relpath(file_path, self.repo_path)
        try:
            commit = self.repo.head.commit
            blob = commit.tree / rel
            git_hash = blob.hexsha
        except Exception:
            return True
        meta_path = self._cache_path(file_path).with_suffix('.hash')
        if not meta_path.exists():
            return True
        return meta_path.read_text() != git_hash

    def load_ast(self, file_path: str):
        with open(self._cache_path(file_path), 'rb') as f:
            return pickle.load(f)

    def save_ast(self, file_path: str, ast_node):
        pkl_path = self._cache_path(file_path)
        with open(pkl_path, 'wb') as f:
            pickle.dump(ast_node, f)
        if not self.repo:
            return
        rel = os.path.relpath(file_path, self.repo_path)
        try:
            commit = self.repo.head.commit
            blob = commit.tree / rel
            hash_path = pkl_path.with_suffix('.hash')
            hash_path.write_text(blob.hexsha)
        except Exception:
            print(f"[CacheManager] Warning: Не удалось получить git-хеш для {file_path}.")

class CodeParser:
    """
    Парсинг Python-файлов в AST с поддержкой кэша.
    """
    def __init__(self, repo_path: str, cache_manager: CacheManager = None):
        self.repo_path = Path(repo_path)
        self.cache = cache_manager

    def find_py_files(self):
        return list(self.repo_path.rglob("*.py"))

    def parse_file(self, file_path: Path):
        source = file_path.read_text(encoding="utf-8")
        return ast.parse(source)

    def parse_repo(self):
        ast_map = {}
        for file in self.find_py_files():
            path_str = str(file)
            if self.cache and self.cache.is_cached(path_str) and not self.cache.is_modified(path_str):
                ast_map[path_str] = self.cache.load_ast(path_str)
            else:
                node = self.parse_file(file)
                ast_map[path_str] = node
                if self.cache:
                    self.cache.save_ast(path_str, node)
        return ast_map

    def ast_to_text(self, node: ast.AST) -> str:
        return ast.unparse(node)

    def extract_calls(self, node: ast.AST):
        """Извлечение пар (caller, callee) из AST-функций."""
        calls = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                # нахождение родительской функции
                parent = n
                while parent and not isinstance(parent, ast.FunctionDef):
                    parent = getattr(parent, 'parent', None)
                if isinstance(parent, ast.FunctionDef):
                    calls.append((parent.name, n.func.id))
        return calls

class Indexer:
    """Построение FAISS-индекса эмбеддингов AST-фрагментов и узлов графа."""
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []

    def build_index(self, texts):
        embeddings = self.model.encode(texts, batch_size=32, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

    def add_metadata(self, meta: dict):
        self.metadata.append(meta)

    def save_index(self, index_path: str, meta_path: str):
        import json
        faiss.write_index(self.index, index_path)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load_index(self, index_path: str, meta_path: str):
        import json
        self.index = faiss.read_index(index_path)
        with open(meta_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)