from typing import Dict, Any, List
import networkx as nx
from app.yandex_gpt import YandexGPTClient

class DiagramBuilder:
    """
    Принимает summary от RepoParser (включая уровни функций, классов, модулей, сервисов)
    и строит C4-диаграмму с готовыми описаниями.
    """
    def __init__(self, summary: Dict[str, Any]):
        self.summary = summary
        self.graph: nx.DiGraph = summary.get("graph")
        self.client = YandexGPTClient()

    def build_c4(self) -> Dict[str, Any]:
        containers: List[Dict[str, Any]] = []
        components: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []

        # 1. Сервисы как верхнеуровневые контейнеры
        # summary["service_summaries"]: {svc_id: text}
        # summary["service_clusters"]: {svc_id: [module_ids]}
        service_clusters = self.summary.get("service_clusters", {})
        if not service_clusters:
            # модули выступают отдельными «сервисами» (контейнерами)
            service_clusters = {f"srv:{mid}": [mid] for mid in self.summary.get("module_summaries", {})}
            # добавляем эти «сервисы» в список контейнеров с пустым описанием
            for svc_id in service_clusters:
                containers.append({"id": svc_id, "name": svc_id, "description": ""})
        for svc_id, desc in self.summary["service_summaries"].items():
            containers.append({
                "id": svc_id,
                "name": svc_id,
                "description": desc
            })

        # 2. Модули как вложенные контейнеры (components уровня контейнера)
        for mod_id, desc in self.summary["module_summaries"].items():
            # находим, в каком сервисе находится модуль
            parent_svc = None
            for svc_id, modules in service_clusters.items():
                if mod_id in modules:
                    parent_svc = svc_id
                    break
            # если не попал ни в один, в "root"
            parent_svc = parent_svc or service_clusters.keys().__iter__().__next__()
            components.append({
                "id": mod_id,
                "name": mod_id,
                "description": desc,
                "containerId": parent_svc
            })
            relationships.append({
                "source": parent_svc,
                "destination": mod_id,
                "description": "содержит"
            })

        # 3. Классы и функции как sub-components
        # class_summaries и function_summaries
        for cls_id, desc in self.summary.get("class_summaries", {}).items():
            comp_module = self.graph.nodes[cls_id]["module"]
            components.append({
                "id": cls_id,
                "name": self.summary["graph"].nodes[cls_id].get("name", cls_id),
                "description": desc,
                "containerId": comp_module
            })
            relationships.append({
                "source": comp_module,
                "destination": cls_id,
                "description": "содержит"
            })
        for fn_id, desc in self.summary.get("function_summaries", {}).items():
            comp_module = self.graph.nodes[fn_id]["module"]
            components.append({
                "id": fn_id,
                "name": self.summary["graph"].nodes[fn_id].get("name", fn_id),
                "description": desc,
                "containerId": comp_module
            })
            relationships.append({
                "source": comp_module,
                "destination": fn_id,
                "description": "содержит"
            })

        # 4. Добавляем связи из графа (import, call)
        for u, v, data in self.graph.edges(data=True):
            rel_type = data.get("type")
            if rel_type in ("import", "call"):
                desc = "импортирует" if rel_type == "import" else "вызывает"
                relationships.append({
                    "source": u,
                    "destination": v,
                    "description": desc
                })

        return {
            "containers": containers,
            "components": components,
            "relationships": relationships
        }
