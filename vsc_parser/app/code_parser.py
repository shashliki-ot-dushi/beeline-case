import ast
import dis
import git
import yaml
import dotenv
from pathlib import Path
from tqdm import tqdm
import networkx as nx
from neo4j import GraphDatabase

from app.graph_utils import add_node, add_edge, neo4j_query
from app.adapters.base import LanguageAdapter
from app.adapters.python_adapter import PythonAdapter
from app.adapters.cpp_adapter import CppAdapter
from common.neo4j.base import get_neo4j_connection

driver = get_neo4j_connection()
G = nx.MultiDiGraph()

# --- 1. Код, классы, функции, переменные и байткод/IR ---
def ingest_code(base_path: Path, adapter: LanguageAdapter, project_uuid: str):
    files = list(adapter.find_source_files(base_path))
    for path in tqdm(files, desc=f"{adapter.__class__.__name__} files", unit="file"):
        rel = path.relative_to(base_path)
        mid = adapter.module_id(rel)
        add_node(G, "Module", mid, project_uuid, path=str(rel))

        src = path.read_text(encoding="utf-8")
        tree = adapter.parse_ast(path)
        adapter.attach_parents(tree)

        # --- 1.1 Ингест классов ---
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cid = f"class:{node.name}@{mid}"
                add_node(G, "Class", cid, project_uuid, name=node.name, lineno=node.lineno)
                add_edge(G, mid, cid, "defines_class", project_uuid)

        # --- 1.2 Ингест функций и методов ---
        for node in adapter.walk(tree):
            if adapter.node_kind(node) == "function":
                fid = adapter.function_id(node, mid)
                add_node(G, "Function", fid, project_uuid,
                         name=adapter.function_name(node), lineno=adapter.node_lineno(node))

                # определяем область: метод класса или свободная функция
                parent = getattr(node, "parent", None)
                while parent and not isinstance(parent, ast.ClassDef):
                    parent = getattr(parent, "parent", None)

                if isinstance(parent, ast.ClassDef):
                    cid = f"class:{parent.name}@{mid}"
                    add_edge(G, cid, fid, "defines_method", project_uuid)
                else:
                    add_edge(G, mid, fid, "defines", project_uuid)

                # PythonAdapter: извлечение байткода
                if isinstance(adapter, PythonAdapter):
                    try:
                        mets = adapter.extract_metrics(path, node, fid)
                        bytecode_sample = mets.get('bytecode_sample')
                        cyclo = mets.get('cyclomatic_complexity')
                        if bytecode_sample is not None:
                            print(f"[BYTECODE SAMPLE] {fid}: {bytecode_sample}")
                            neo4j_query(
                                "MATCH (n {id: $id}) SET n.bytecode_sample = $bc, n.cyclomatic_complexity = $cc",
                                id=fid, bc=bytecode_sample, cc=cyclo
                            )
                            G.nodes[fid]['bytecode_sample'] = bytecode_sample
                            G.nodes[fid]['cyclomatic_complexity'] = cyclo
                    except Exception as e:
                        print(f"[BYTECODE ERROR] {fid}: {e}")

                # CppAdapter: извлечение метрик IR
                elif isinstance(adapter, CppAdapter):
                    try:
                        mets = adapter.extract_metrics(path, node, fid)
                        if mets.get('ir_instructions'):
                            print(f"[IR METRICS] {fid}: blocks={mets['num_basic_blocks']}, instr={len(mets['ir_instructions'])}")
                            neo4j_query(
                                "MATCH (n {id: $id}) SET n.ir_instructions = $ins, n.num_basic_blocks = $bb",
                                id=fid, ins=mets['ir_instructions'], bb=mets['num_basic_blocks']
                            )
                            G.nodes[fid]['ir_instructions'] = mets['ir_instructions']
                            G.nodes[fid]['num_basic_blocks'] = mets['num_basic_blocks']
                    except Exception as e:
                        print(f"[IR METRICS ERROR] {fid}: {e}")

        # --- 1.3 Ингест переменных ---
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        var_name = t.id
                        vid = f"variable:{var_name}@{mid}:{node.lineno}"
                        add_node(G, "Variable", vid, project_uuid, name=var_name, lineno=node.lineno)

                        # определяем область видимости переменной
                        owner = mid
                        parent = getattr(node, "parent", None)
                        while parent:
                            if isinstance(parent, ast.FunctionDef):
                                owner = adapter.function_id(parent, mid)
                                break
                            if isinstance(parent, ast.ClassDef):
                                owner = f"class:{parent.name}@{mid}"
                                break
                            parent = getattr(parent, "parent", None)

                        add_edge(G, owner, vid, "defines_variable", project_uuid)

# --- 2. Тесты ---
def ingest_tests(base_path: Path, project_uuid: str):
    for path in tqdm(base_path.rglob("test_*.py"), desc="Test files", unit="file"):
        rel = path.relative_to(base_path)
        mod_id = f"module:{rel}"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        add_node(G, "Module", mod_id, project_uuid, path=str(rel))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tst_id = f"test:{node.name}@{mod_id}"
                add_node(G, "TestCase", tst_id, project_uuid, name=node.name, lineno=node.lineno)
                add_edge(G, mod_id, tst_id, "defines", project_uuid)
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assert):
                        step_id = f"teststep:{node.name}:{sub.lineno}@{mod_id}"
                        add_node(G, "TestStep", step_id, project_uuid, lineno=sub.lineno)
                        add_edge(G, tst_id, step_id, "has_step", project_uuid)
            if isinstance(node, ast.ClassDef):
                for m in node.body:
                    if isinstance(m, ast.FunctionDef) and m.name == "setUp":
                        fix_id = f"fixture:{node.name}.setUp@{mod_id}"
                        add_node(G, "Fixture", fix_id, project_uuid)
                        add_edge(G, fix_id, f"test:{m.name}@{mod_id}", "defines_fixture", project_uuid)

# --- 3. Документация ---
def ingest_docs(base_path: Path, project_uuid: str):
    for py in tqdm(base_path.rglob("*.py"), desc="Docstrings", unit="file"):
        if any(p in ("__pycache__", ".ipynb_checkpoints") for p in py.parts):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except Exception:
            continue
        module_id = f"module:{py.relative_to(base_path)}"
        doc = ast.get_docstring(tree)
        if doc:
            nid = f"doc:module:{py.relative_to(base_path)}"
            add_node(G, "DocString", nid, project_uuid, text=doc)
            add_edge(G, nid, module_id, "docs", project_uuid)
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                if doc:
                    kind = "Class" if isinstance(node, ast.ClassDef) else "Function"
                    nid = f"doc:{kind.lower()}:{node.name}@{py.relative_to(base_path)}"
                    tgt = f"{kind.lower()}:{node.name}@{module_id}"
                    add_node(G, "DocString", nid, project_uuid, text=doc)
                    add_edge(G, nid, tgt, "docs", project_uuid)
    
    readme = base_path / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        nid = f"doc:README@{readme.name}"
        add_node(G, "DocFile", nid, project_uuid, text=text)
        add_edge(G, f"doc:README@{readme.name}", f"module:.@{readme.name}", "docs", project_uuid)

    for y in tqdm(base_path.rglob("*.yaml"), desc="OpenAPI specs", unit="file"):
        try:
            conf = yaml.safe_load(y.read_text(encoding="utf-8"))
        except Exception:
            continue
        nid = f"openapi:{y.relative_to(base_path)}"
        conf_text = yaml.safe_dump(conf, default_flow_style=False)
        add_node(G, "OpenAPI", nid, project_uuid, text=conf_text)
        for pi in conf.get("paths", {}).values():
            for det in pi.values():
                op_id = det.get("operationId")
                if op_id:
                    for n, d in G.nodes(data=True):
                        if d.get("type") == "Function" and d.get("name") == op_id:
                            add_edge(G, nid, n, "api_implements", project_uuid)
                            break

# --- 4. Конфиг ---
def ingest_config(base_path: Path, project_uuid: str):
    env_file = base_path / ".env"
    if env_file.exists():
        cfg = dotenv.dotenv_values(str(env_file))
        for k, v in cfg.items():
            add_node(G, "EnvVar", f"env:{k}", project_uuid, value=v)

    for y in tqdm(base_path.rglob("*.yml"), desc="Config files", unit="file"):
        try:
            data = yaml.safe_load(y.read_text(encoding="utf-8"))
        except Exception:
            continue
        conf_text = yaml.safe_dump(data, default_flow_style=False)
        add_node(G, "ConfigFile", f"cfg:{y.relative_to(base_path)}", project_uuid, text=conf_text)

# --- 5. VCS ingest ---
def ingest_vcs(base_path: Path, project_uuid: str):
    repo = git.Repo(str(base_path))
    for commit in tqdm(repo.iter_commits(), desc="Commits", unit="commit"):
        user_email = commit.author.email or "unknown@example.com"
        user_id = f"user:{user_email}"
        add_node(G, "User", user_id, project_uuid, email=user_email, name=commit.author.name or user_email)
        cid = f"commit:{commit.hexsha}"
        add_node(G, "Commit", cid, project_uuid,
                 hexsha=commit.hexsha, author=user_email,
                 date=commit.committed_datetime.isoformat(), message=commit.message.strip())
        add_edge(G, user_id, cid, "authored", project_uuid)

        parent = commit.parents[0] if commit.parents else None
        diffs = commit.diff(parent, create_patch=True)
        for diff in diffs:
            fpath = diff.b_path or diff.a_path
            mod_id = f"module:{fpath}"
            if not G.has_node(mod_id):
                continue
            patch_text = diff.diff.decode('utf-8', errors='ignore')
            lines = patch_text.splitlines()
            insertions = sum(1 for l in lines if l.startswith('+') and not l.startswith('+++'))
            deletions = sum(1 for l in lines if l.startswith('-') and not l.startswith('---'))
            neo4j_query(
                "MATCH (c {id: $cid}), (m {id: $mod_id}) CREATE (c)-[r:MODIFIES {insertions: $insertions, deletions: $deletions, patch: $patch}]->(m)",
                cid=cid, mod_id=mod_id, insertions=insertions,
                        deletions=deletions, patch=patch_text
            )