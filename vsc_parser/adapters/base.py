# base.py
from abc import ABC, abstractmethod
from pathlib import Path

class LanguageAdapter(ABC):
    @abstractmethod
    def find_source_files(self, base_path: Path):
        pass

    @abstractmethod
    def module_id(self, rel_path: Path) -> str:
        pass

    @abstractmethod
    def parse_ast(self, path: Path):
        pass

    @abstractmethod
    def attach_parents(self, tree):
        pass

    @abstractmethod
    def walk(self, tree):
        pass

    @abstractmethod
    def node_kind(self, node):
        pass

    @abstractmethod
    def class_id(self, node, mod_id: str) -> str:
        pass

    @abstractmethod
    def class_name(self, node) -> str:
        pass

    @abstractmethod
    def class_bases(self, node):
        pass

    @abstractmethod
    def class_base_id(self, base) -> str:
        pass

    @abstractmethod
    def function_id(self, node, mod_id: str) -> str:
        pass

    @abstractmethod
    def function_name(self, node) -> str:
        pass

    @abstractmethod
    def node_lineno(self, node) -> int:
        pass

    @abstractmethod
    def extract_metrics(self, path: Path, node, fn_id: str) -> dict:
        pass

    @abstractmethod
    def assign_targets(self, node):
        pass

    @abstractmethod
    def variable_info(self, node, mod_id: str):
        pass

    @abstractmethod
    def raise_exception(self, node):
        pass

    @abstractmethod
    def exception_id(self, ex_name: str) -> str:
        pass

    @abstractmethod
    def enclosing_function(self, node):
        pass

    @abstractmethod
    def imports(self, node, base_path: Path, rel_path: Path):
        pass
