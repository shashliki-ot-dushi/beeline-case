import ast
import dis
import inspect
from pathlib import Path
from radon.visitors import ComplexityVisitor

from adapters.base import LanguageAdapter

class PythonAdapter(LanguageAdapter):
    """
    Быстрый парсинг Python: AST → Module, Class, Function,
    Variable, Attribute, Exception, Import.
    Сбор метрик: байткод и цикломатическая сложность.
    """
    ext = '.py'

    def find_source_files(self, base_path: Path):
        return base_path.rglob(f"*{self.ext}")

    def module_id(self, rel_path: Path):
        return f"module:{rel_path}"

    def parse_ast(self, path: Path):
        return ast.parse(path.read_text(encoding="utf-8"))

    def attach_parents(self, tree):
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    def walk(self, tree):
        return ast.walk(tree)

    def node_kind(self, node):
        if isinstance(node, ast.ClassDef):
            return "class"
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return "function"
        if isinstance(node, ast.Assign):
            return "assign"
        if isinstance(node, ast.Raise):
            return "raise"
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "import"
        return None

    def class_id(self, node, mod_id: str):
        return f"class:{node.name}@{mod_id}"

    def class_name(self, node):
        return node.name

    def class_bases(self, node):
        return [b for b in node.bases if isinstance(b, ast.Name)]

    def class_base_id(self, base):
        return f"class:{base.id}"

    def function_id(self, node, mod_id: str):
        return f"func:{node.name}@{mod_id}"

    def function_name(self, node):
        return node.name

    def node_lineno(self, node):
        return getattr(node, 'lineno', None)

    def extract_metrics(self, path: Path, node, fn_id: str):
        """
        Сбор метрик Python-функции:
         - пример: первые 5 инструкций байткода
         - цикломатическая сложность
        """
        try:
            src = path.read_text(encoding="utf-8")
            # Компилируем весь модуль
            code_obj = compile(src, filename=str(path), mode="exec")
            # Находим функцию объект по co_name
            target_consts = [const for const in code_obj.co_consts
                             if hasattr(const, 'co_name') and const.co_name == node.name]
            if not target_consts:
                return {}
            fn_obj = target_consts[0]
            # Байткод: первые 5 инструкций
            bc = list(dis.Bytecode(fn_obj))[:5]
            bytecode_sample = [(ins.opname, ins.argrepr) for ins in bc]
            # Цикломатическая сложность
            cc = ComplexityVisitor.from_code(inspect.getsource(fn_obj))[0].complexity
            return {
                "bytecode_sample": bytecode_sample,
                "cyclomatic_complexity": cc
            }
        except Exception:
            return {}

    def assign_targets(self, node):
        return node.targets

    def variable_info(self, tgt, mod_id: str):
        if isinstance(tgt, ast.Name):
            return f"var:{tgt.id}@{mod_id}", "Variable", tgt.id
        if isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == 'self':
            return f"attr:{tgt.attr}@{mod_id}", "Attribute", tgt.attr
        return None, None, None

    def raise_exception(self, node):
        if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
            return node.exc.func.id
        return None

    def exception_id(self, ex_name: str):
        return f"exception:{ex_name}"

    def enclosing_function(self, node):
        fn = getattr(node, 'parent', None)
        while fn and not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = getattr(fn, 'parent', None)
        return fn

    def imports(self, node, base_path: Path, rel_path: Path):
        modules = []
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(f"module:{alias.name.split('.')[0]}.py")
        else:  # ImportFrom
            for alias in node.names:
                pkg = (node.module or alias.name).split('.')[0]
                modules.append(f"module:{pkg}.py")
        return modules
