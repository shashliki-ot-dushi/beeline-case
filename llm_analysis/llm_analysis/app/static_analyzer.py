import os
import shutil
import tempfile
import ast
from git import Repo
import networkx as nx

class StaticRepoParser:
    """
    Универсальный статический парсер репозитория:
    - строит граф пакетов, модулей, классов, функций
    - связи: contains, import, call
    """
    def __init__(self, repo_url: str, clone_dir: str = None):
        self.repo_url = repo_url
        self.clone_dir = clone_dir or tempfile.mkdtemp()
        self.graph = nx.DiGraph()

    def clone_repo(self):
        """Клонируем репозиторий в временную папку"""
        Repo.clone_from(self.repo_url, self.clone_dir)

    def cleanup(self):
        """Удаляем временную папку"""
        shutil.rmtree(self.clone_dir, ignore_errors=True)

    def _collect_py_files(self):
        """Находит все .py файлы, исключая tests, docs и .git"""
        for root, _, files in os.walk(self.clone_dir):
            # пропускаем тесты, документацию и папку .git
            if any(skip in root for skip in ('/tests', '/docs', '/.git')):
                continue
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                yield os.path.join(root, fname)

    def build_graph(self):
        """
        Строим граф:
        - пакеты (папки) → модули (файлы) → классы/функции
        - связи: contains, import, call
        """
        # собираем все файлы
        py_files = list(self._collect_py_files())

        # 1) Узлы-пакеты и модули
        for path in py_files:
            rel = os.path.relpath(path, self.clone_dir)
            parts = rel.split(os.sep)
            pkg = parts[0] if len(parts) > 1 else 'root'
            pkg_id = f"pkg:{pkg}"
            if not self.graph.has_node(pkg_id):
                self.graph.add_node(pkg_id, type='package', name=pkg)

            mod_id = f"m:{rel}"
            self.graph.add_node(mod_id,
                                type='module',
                                name=rel,
                                package=pkg_id)
            self.graph.add_edge(pkg_id, mod_id, type='contains')

        # 2) Парсинг AST: классы, функции, импорты и вызовы
        for path in py_files:
            rel = os.path.relpath(path, self.clone_dir)
            mod_id = f"m:{rel}"
            src = open(path, encoding='utf-8').read()
            tree = ast.parse(src)

            # a) классы и функции
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    name = node.name
                    if name.startswith('_'):
                        continue
                    ntype = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    prefix = 'c' if ntype == 'class' else 'f'
                    comp_id = f"{prefix}:{rel}:{name}"
                    pkg_id = self.graph.nodes[mod_id]['package']
                    self.graph.add_node(comp_id,
                                        type=ntype,
                                        name=name,
                                        module=mod_id,
                                        package=pkg_id)
                    self.graph.add_edge(comp_id, mod_id, type='contains')

            # b) импорты
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

            # c) вызовы функций
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

    def graph_to_c4(self, graph):
        """
        Преобразуем граф в формат C4: контейнеры, компоненты и связи
        """
        containers = []
        components = []
        relationships = []

        # контейнеры = модули
        for nid, data in graph.nodes(data=True):
            if data.get('type') == 'module':
                containers.append({
                    'id': nid,
                    'name': data.get('name', nid),
                    'description': ''
                })
            else:
                components.append({
                    'id': nid,
                    'name': data.get('name', nid),
                    'description': '',
                    'containerId': data.get('module', '')
                })

        # связи
        for u, v, data in graph.edges(data=True):
            rel_type = data.get('type', '')
            desc = {'import': 'модуль импортирует', 'call': 'вызывает', 'contains': 'содержит'}.get(rel_type, rel_type)
            relationships.append({
                'source': u,
                'destination': v,
                'description': desc
            })

        return {
            'containers': containers,
            'components': components,
            'relationships': relationships
        }
