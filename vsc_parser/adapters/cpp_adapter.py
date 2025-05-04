import os
import subprocess
from pathlib import Path

from clang.cindex import Index, CursorKind, Config

import llvmlite

llvmlite.opaque_pointers_enabled = True

from llvmlite       import binding as llvm


from adapters.base    import LanguageAdapter
from graph_utils      import add_node, add_edge

import re

# Указываем путь к libclang (можно задать через переменную окружения LIBCLANG_PATH)
Config.set_library_file(os.getenv('LIBCLANG_PATH', '/usr/lib/llvm-18/lib/libclang.so'))

class CppAdapter(LanguageAdapter):
    ext = ['.c', '.cc', '.cxx', '.cpp', '.h', '.hpp']

    def __init__(self, clang_args=None):
        # Аргументы для фронтенда Clang (например, стандарт C++17)
        self.clang_args = clang_args or ['-std=c++17']
        # Инициализируем llvmlite
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmparser()

    def find_source_files(self, base_path: Path):
        # Ищем файлы с любым из расширений C/C++
        for ext in self.ext:
            yield from base_path.rglob(f"*{ext}")

    def module_id(self, rel_path: Path) -> str:
        return f"module:{rel_path}"

    def parse_ast(self, path: Path):
        # Создаём индекс и парсим AST
        idx = Index.create()
        return idx.parse(str(path), args=self.clang_args)

    def attach_parents(self, tu):
        # У clang.cindex курсоры уже связаны через semantic_parent
        pass

    def walk(self, tu):
        # Обход AST в preorder
        return tu.cursor.walk_preorder()

    def node_kind(self, node):
        k = node.kind
        if k in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL):
            return 'class'
        if k in (CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD,
                 CursorKind.CONSTRUCTOR, CursorKind.DESTRUCTOR):
            return 'function'
        if k == CursorKind.VAR_DECL:
            return 'assign'
        if k == CursorKind.CXX_THROW_EXPR:
            return 'raise'
        if k == CursorKind.INCLUSION_DIRECTIVE:
            return 'import'
        return None

    def class_id(self, node, mod_id: str) -> str:
        return f"class:{node.spelling}@{mod_id}"

    def class_name(self, node) -> str:
        return node.spelling

    def class_bases(self, node):
        return [c for c in node.get_children() if c.kind == CursorKind.CXX_BASE_SPECIFIER]

    def class_base_id(self, base) -> str:
        d = base.get_definition()
        return f"class:{d.spelling}" if d else None

    def function_id(self, node, mod_id: str) -> str:
        return f"func:{node.spelling}@{mod_id}"

    def function_name(self, node) -> str:
        return node.spelling

    def node_lineno(self, node) -> int:
        return node.location.line if node.location else None

    class TypeInfo:
        def __init__(self, name, edge_label):
            self.name = name
            self.edge_label = edge_label

    def function_return_and_param_types(self, node):
        ts = [self.TypeInfo(node.result_type.spelling, 'returns_type')]
        for arg in node.get_arguments():
            ts.append(self.TypeInfo(arg.type.spelling, 'param_type'))
        return ts

    def assign_targets(self, node):
        return [node]

    def variable_info(self, node, mod_id: str):
        name = node.spelling
        return f"var:{name}@{mod_id}", 'Variable', name

    def raise_exception(self, node):
        children = list(node.get_children())
        return children[0].type.spelling if children else None

    def exception_id(self, ex: str) -> str:
        return f"exception:{ex}"

    def enclosing_function(self, node):
        p = node.semantic_parent
        while p and p.kind not in (CursorKind.FUNCTION_DECL, CursorKind.CXX_METHOD):
            p = p.semantic_parent
        return p

    def imports(self, node, base_path: Path, rel_path: Path):
        return [f"module:{node.include}"]

    def extract_metrics(self, path: Path, node, fn_id: str) -> dict:
        """
        Stubbed out: no IR metrics collected. Always returns NaN.
        """
        # IR extraction disabled — returning NaN for metrics
        return {
            'ir_instructions': [],
            'num_basic_blocks': float('nan')
        }
