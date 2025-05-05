import os
import shutil
import ast
import tempfile
from git import Repo
import networkx as nx
from networkx.algorithms import community
from app.yandex_gpt import YandexGPTClient


class RepoParser:
    """
    Клонирует репозиторий, строит AST-граф и поэтапно собирает summary:
    - функции → классы → модули → сервисы
    """
    def __init__(self, repo_url: str, clone_dir: str = None):
        self.repo_url = repo_url
        self.clone_dir = clone_dir or tempfile.mkdtemp()
        self.graph = nx.DiGraph()
        self.client = YandexGPTClient()

    def clone_repo(self):
        """Клонируем репозиторий в temp-директорию"""
        Repo.clone_from(self.repo_url, self.clone_dir)

    def cleanup(self):
        """Удаляем временную папку"""
        shutil.rmtree(self.clone_dir, ignore_errors=True)

    def _collect_py_files(self):
        """Ищем релевантные Python-файлы (без тестов и доков)"""
        for root, _, files in os.walk(self.clone_dir):
            rel_root = os.path.relpath(root, self.clone_dir)
            if rel_root.startswith(("tests", "docs")):
                continue
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                yield os.path.join(root, fname)

    def build_graph(self):
        """
        Строим граф пакетов, модулей, классов и функций с импортами и вызовами.
        Также сохраняем код каждого узла.
        """
        py_files = list(self._collect_py_files())

        # Добавляем узлы-пакеты и узлы-модулей
        for path in py_files:
            rel = os.path.relpath(path, self.clone_dir)
            parts = rel.split(os.sep)
            pkg = parts[0] if parts else ''
            pkg_id = f"pkg:{pkg}" if pkg else "pkg:root"
            if not self.graph.has_node(pkg_id):
                self.graph.add_node(pkg_id, type='package', name=pkg or 'root')

            mod_id = f"m:{rel}"
            self.graph.add_node(mod_id, type='module', name=rel, package=pkg_id)
            self.graph.add_edge(pkg_id, mod_id, type='contains')

        # Парсим AST каждого модуля
        for path in py_files:
            rel = os.path.relpath(path, self.clone_dir)
            mod_id = f"m:{rel}"
            src = open(path, encoding='utf-8').read()
            tree = ast.parse(src)

            # классы и функции
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = node.name
                    if name.startswith('_'):
                        continue
                    ntype = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    prefix = 'c' if ntype == 'class' else 'f'
                    comp_id = f"{prefix}:{rel}:{name}"
                    pkg_id = self.graph.nodes[mod_id]['package']
                    # извлекаем код узла
                    code = self._extract_source(node, path)
                    self.graph.add_node(comp_id,
                                        type=ntype,
                                        name=name,
                                        module=mod_id,
                                        package=pkg_id,
                                        code=code)
                    self.graph.add_edge(comp_id, mod_id, type='contains')

            # импорты
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        tgt = alias.name.replace('.', os.sep) + '.py'
                        tgt_path = os.path.normpath(os.path.join(self.clone_dir, tgt))
                        if os.path.exists(tgt_path):
                            tgt_rel = os.path.relpath(tgt_path, self.clone_dir)
                            self.graph.add_edge(mod_id, f"m:{tgt_rel}", type='import')
                elif isinstance(node, ast.ImportFrom) and node.module:
                    base = node.module.replace('.', os.sep) + '.py'
                    tgt_path = os.path.normpath(os.path.join(self.clone_dir, base))
                    if os.path.exists(tgt_path):
                        tgt_rel = os.path.relpath(tgt_path, self.clone_dir)
                        self.graph.add_edge(mod_id, f"m:{tgt_rel}", type='import')

            # вызовы функций
            class CallVisitor(ast.NodeVisitor):
                def __init__(self, graph, current):
                    self.graph = graph
                    self.current = current
                def visit_Call(self, call):
                    if isinstance(call.func, ast.Name):
                        tgt = f"f:{rel}:{call.func.id}"
                        if self.graph.has_node(tgt):
                            self.graph.add_edge(self.current, tgt, type='call')
                    self.generic_visit(call)

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    CallVisitor(self.graph, f"f:{rel}:{node.name}").visit(node)
                elif isinstance(node, ast.ClassDef):
                    for child in node.body:
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            CallVisitor(self.graph, f"f:{rel}:{child.name}").visit(child)

        return self.graph

    def _extract_source(self, node, filepath):
        """Извлекаем исходный код узла AST по номерам строк"""
        lines = open(filepath, encoding='utf-8').read().splitlines()
        return '\n'.join(lines[node.lineno-1: node.end_lineno])

    def summarize_functions(self):
        self.function_summaries = {}
        for nid, data in self.graph.nodes(data=True):
            if data.get('type') == 'function':
                prompt = (
                    "Опиши коротко, что делает эта функция на русском языке,"
                    " используя следующий код:\n```python\n{code}\n```".format(code=data['code'])
                )
                self.function_summaries[nid] = self.client.summarize(prompt).strip()


    def summarize_classes(self):
        self.class_summaries = {}
        for nid, data in self.graph.nodes(data=True):
            if data.get('type') == 'class':
                # находим методы класса через ребра contains
                methods = []
                for u, v, d in self.graph.edges(data=True):
                    if d.get('type') == 'contains' and v == nid and u.startswith('f:'):
                        methods.append(u)
                # формируем bullets из summary функций
                bullets = '\n'.join(
                    f"- {self.function_summaries.get(m, '')}" for m in methods
                )
                prompt = (
                    "Собери короткое summary класса на русском языке на основе его методов:\n"
                    + bullets
                )
                self.class_summaries[nid] = self.client.summarize(prompt).strip()

    def summarize_modules(self):
        self.module_summaries = {}
        for nid, data in self.graph.nodes(data=True):
            if data.get('type') == 'module':
                # находим компоненты модуля
                comps = [n for n, d in self.graph.nodes(data=True)
                         if d.get('module') == nid and d.get('type') in ('function', 'class')]
                bullets = '\n'.join(
                    f"- {self.function_summaries.get(n, self.class_summaries.get(n, ''))}" for n in comps
                )
                prompt = (
                    "Собери короткое summary модуля на русском языке на основе его функций и классов:\n" + bullets
                )
                self.module_summaries[nid] = self.client.summarize(prompt).strip()

    def summarize_services(self):
        # кластеризация модулей в подсистемы
        mod_nodes = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'module']
        subgraph = self.graph.subgraph(mod_nodes).to_undirected()
        communities = community.louvain_communities(subgraph)
        self.service_summaries = {}
        for idx, cluster in enumerate(communities):
            bullets = '\n'.join(f"- {self.module_summaries.get(m)}" for m in cluster if m in self.module_summaries)
            prompt = (
                f"Опиши подсистему #{idx} на русском языке на основе следующих модулей:\n" + bullets
            )
            svc_id = f"svc:{idx}"
            self.service_summaries[svc_id] = self.client.summarize(prompt).strip()

    def summarize_all(self):
        """
        Выполняет весь pipeline summarization: граф→функции→классы→модули→сервисы
        """
        self.build_graph()
        self.summarize_functions()
        self.summarize_classes()
        self.summarize_modules()
        self.summarize_services()
        return {
            "function_summaries": self.function_summaries,
            "class_summaries": self.class_summaries,
            "module_summaries": self.module_summaries,
            "service_summaries": self.service_summaries,
            "graph": self.graph,
        }