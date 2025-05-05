import ast
import dis
import inspect
import yaml
import git
import dotenv
from pathlib import Path
import networkx as nx
from radon.visitors import ComplexityVisitor
from neo4j import GraphDatabase

# Neo4j connection
driver = GraphDatabase.driver(
    "bolt://84.54.56.225:7687",
    auth=("neo4j", "12345678")
)

def neo4j_query(query: str, **kwargs):
    with driver.session() as session:
        session.run(query, **kwargs)

# --- Graph initialization ---
G = nx.MultiDiGraph()

def add_node(node_type: str, identifier: str, **attrs):
    if not G.has_node(identifier):
        G.add_node(identifier, type=node_type, **attrs)
        attrs_cleaned = {k: v for k, v in attrs.items() if isinstance(v, (str, int, float, bool))}
        attrs_query = ', '.join(f'{key}: ${key}' for key in attrs_cleaned)
        query = f"CREATE (n:{node_type} {{ id: $id{', ' + attrs_query if attrs_query else ''} }})"
        neo4j_query(query, id=identifier, **attrs_cleaned)


def add_edge(src: str, dst: str, edge_type: str = "RELATED_TO"):
    G.add_edge(src, dst, type=edge_type)
    query = f"""
    MATCH (a {{id: $src}}), (b {{id: $dst}})
    CREATE (a)-[:{edge_type.upper()}]->(b)
    """
    neo4j_query(query, src=src, dst=dst)

# --- 1. AST/BC/CFG & Symbol (+ Variable, Type, Exception) ---
def ingest_code(base_path: Path):
    for path in base_path.rglob("*.py"):
        src = path.read_text(encoding="utf-8")
        # Module ID and store path relative to the library root
        rel = path.relative_to(base_path)
        mod_id = f"module:{rel}"
        add_node("Module", mod_id, path=str(rel))

        tree = ast.parse(src)
        for n in ast.walk(tree):
            for c in ast.iter_child_nodes(n):
                c.parent = n

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls_id = f"class:{node.name}@{mod_id}"
                add_node("Class", cls_id, name=node.name, lineno=node.lineno)
                add_edge(mod_id, cls_id, "defines")
                for b in node.bases:
                    if isinstance(b, ast.Name):
                        add_edge(cls_id, f"class:{b.id}", "inherits")

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn_id = f"func:{node.name}@{mod_id}"
                add_node("Function", fn_id, name=node.name, lineno=node.lineno)
                add_edge(mod_id, fn_id, "defines")
                if node.returns:
                    tp = ast.unparse(node.returns)
                    tp_id = f"type:{tp}"
                    add_node("Type", tp_id, name=tp)
                    add_edge(fn_id, tp_id, "returns_type")
                for arg in list(node.args.args) + list(node.args.kwonlyargs):
                    if arg.annotation:
                        tp = ast.unparse(arg.annotation)
                        tp_id = f"type:{tp}"
                        add_node("Type", tp_id, name=tp)
                        add_edge(fn_id, tp_id, "param_type")

            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        var_id = f"var:{tgt.id}@{mod_id}"
                        add_node("Variable", var_id, name=tgt.id, lineno=node.lineno)
                        add_edge(mod_id, var_id, "defines")
                    elif isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == "self":
                        var_id = f"attr:{tgt.attr}@{mod_id}"
                        add_node("Attribute", var_id, name=tgt.attr, lineno=node.lineno)
                        add_edge(mod_id, var_id, "defines")

            elif isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                    ex = node.exc.func.id
                    ex_id = f"exception:{ex}"
                    add_node("Exception", ex_id, name=ex)
                    fn = node
                    while fn and not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fn = fn.parent
                    if fn:
                        add_edge(f"func:{fn.name}@{mod_id}", ex_id, "throws")

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    pkg = alias.name.split('.')[0]
                    imp_id = f"module:{pkg}.py"
                    add_node("Module", imp_id)
                    add_edge(mod_id, imp_id, "imports")

            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if node.level == 0 and node.module:
                        pkg = node.module.split('.')[0]
                        imp_id = f"module:{pkg}.py"
                    else:
                        parent_dir = path.parent
                        for _ in range(max(0, node.level-1)):
                            parent_dir = parent_dir.parent
                        rel_mod = (parent_dir / f"{alias.name}.py").relative_to(base_path)
                        imp_id = f"module:{rel_mod}"
                    add_node("Module", imp_id)
                    add_edge(mod_id, imp_id, "imports")

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                fn_id = f"func:{node.name}@{mod_id}"
                try:
                    module_obj = __import__(path.stem)
                    fn_obj = getattr(module_obj, node.name)
                    bc = list(dis.Bytecode(fn_obj))[:5]
                    G.nodes[fn_id]["bytecode"] = [(ins.opname, ins.argrepr) for ins in bc]
                    src_fn = inspect.getsource(fn_obj)
                    cc = ComplexityVisitor.from_code(src_fn)[0].complexity
                    G.nodes[fn_id]["cyclomatic_complexity"] = cc
                except Exception:
                    pass

# --- 2. Test-Coverage: TestStep and Fixture ---
def ingest_tests(base_path: Path):
    for path in base_path.rglob("test_*.py"):
        rel = path.relative_to(base_path)
        mod_id = f"module:{rel}"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tst_id = f"test:{node.name}@{mod_id}"
                add_node("TestCase", tst_id, name=node.name, lineno=node.lineno)
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assert):
                        step_id = f"teststep:{node.name}:{sub.lineno}@{mod_id}"
                        add_node("TestStep", step_id, lineno=sub.lineno)
                        add_edge(tst_id, step_id, "has_step")
            if isinstance(node, ast.ClassDef):
                for m in node.body:
                    if isinstance(m, ast.FunctionDef) and m.name == "setUp":
                        fix_id = f"fixture:{node.name}.setUp@{mod_id}"
                        add_node("Fixture", fix_id)
                        add_edge(fix_id, f"test:{node.name}.setUp@{mod_id}", "defines_fixture")

# --- 3. Runtime-Metrics (stub) ---
def ingest_runtime_metrics():
    pass

# --- 4. Docs: docstrings, README, OpenAPI spec ---
def ingest_docs(base_path: Path):
    for py in base_path.rglob("*.py"):
        if any(p in ("__pycache__", ".ipynb_checkpoints") for p in py.parts):
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except Exception:
            continue
        module_id = f"module:{py.relative_to(base_path)}"
        try:
            doc = ast.get_docstring(tree)
        except TypeError:
            doc = None
        if doc:
            nid = f"doc:module:{py.relative_to(base_path)}"
            add_node("DocString", nid, text=doc)
            add_edge(nid, module_id, "docs")
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                try:
                    doc = ast.get_docstring(node)
                except TypeError:
                    continue
                if doc:
                    kind = "Class" if isinstance(node, ast.ClassDef) else "Function"
                    nid = f"doc:{kind.lower()}:{node.name}@{py.relative_to(base_path)}"
                    add_node("DocString", nid, text=doc)
                    tgt = f"{kind.lower()}:{node.name}@module:{py.relative_to(base_path)}"
                    add_edge(nid, tgt, "docs")
    readme = base_path / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        nid = f"doc:README@{readme.name}"
        add_node("DocFile", nid, text=text)
        add_edge(nid, f"module:.@{readme.name}", "docs")
    for y in base_path.rglob("*.yaml"):
        try:
            conf = yaml.safe_load(y.read_text(encoding="utf-8"))
        except Exception:
            continue
        nid = f"openapi:{y.relative_to(base_path)}"
        add_node("OpenAPI", nid, data=conf)
        for pi in conf.get("paths", {}).values():
            for det in pi.values():
                op_id = det.get("operationId")
                if op_id:
                    for n, d in G.nodes(data=True):
                        if d.get("type") == "Function" and d.get("name") == op_id:
                            add_edge(nid, n, "api_implements")
                            break

# --- 5. External & Config ---
def ingest_config(base_path: Path):
    env_file = base_path / ".env"
    if env_file.exists():
        cfg = dotenv.dotenv_values(str(env_file))
        for k, v in cfg.items():
            add_node("EnvVar", f"env:{k}", value=v)
    for y in base_path.rglob("*.yml"):
        try:
            data = yaml.safe_load(y.read_text(encoding="utf-8"))
        except Exception:
            continue
        add_node("ConfigFile", f"cfg:{y.relative_to(base_path)}", data=data)

# --- 6. VCS ingest ---
def ingest_vcs(base_path: Path):
    repo = git.Repo(str(base_path))
    for commit in repo.iter_commits():
        user_email = commit.author.email or "unknown@example.com"
        user_id = f"user:{user_email}"
        add_node("User", user_id, email=user_email, name=commit.author.name or user_email)
        cid = f"commit:{commit.hexsha}"
        add_node("Commit", cid, hexsha=commit.hexsha, author=user_email,
                 date=commit.committed_datetime.isoformat(), message=commit.message.strip())
        add_edge(user_id, cid, "authored")
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
            query = """
            MATCH (c {id: $cid}), (m {id: $mod_id})
            CREATE (c)-[r:MODIFIES {insertions: $insertions, deletions: $deletions, patch: $patch}]->(m)
            """
            neo4j_query(query, cid=cid, mod_id=mod_id, insertions=insertions,
                        deletions=deletions, patch=patch_text)

# --- Main execution ---
if __name__ == "__main__":
    neo4j_query("MATCH (n) DETACH DELETE n")
    BASE = Path("./requests")
    ingest_code(BASE)
    ingest_tests(BASE)
    ingest_runtime_metrics()
    ingest_docs(BASE)
    ingest_config(BASE)
    ingest_vcs(BASE)
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
    print("Граф сформирован и отправлен в Neo4j инкрементально.")