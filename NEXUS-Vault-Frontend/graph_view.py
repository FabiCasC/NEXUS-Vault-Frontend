"""
graph_view.py
Pinta el grafo estilo Obsidian a partir de un dict {root, nodes, edges}.
No sabe nada de CSVs ni de algoritmos: solo recibe JSON ya armado
(por el fixture local o por form_team.py) y lo dibuja.

Formato esperado de graph_data:
{
    "root": "NEED-001",
    "nodes": [
        {"id": "...", "type": "NEED|THESIS|PROJECT|RESEARCHER|CAPABILITY|SUBJECT|LAB|PROP",
         "label": "...", "generated": bool, ...},
        ...
    ],
    "edges": [
        {"source": "...", "target": "...", "label": "...", "generated": bool},
        ...
    ]
}
"""

from streamlit_agraph import agraph, Node, Edge, Config

NODE_COLORS = {
    "NEED": "#4C6EF5",
    "THESIS": "#12B886",
    "PROJECT": "#12B886",
    "RESEARCHER": "#F59F00",
    "CAPABILITY": "#868E96",
    "SUBJECT": "#868E96",
    "LAB": "#E64980",
    "PROP": "#ADB5BD",
}

DEFAULT_COLOR = "#CED4DA"


def _is_generated(node_or_edge: dict) -> bool:
    return node_or_edge.get("type") == "PROP" or bool(node_or_edge.get("generated"))


def build_graph(graph_data: dict):
    """Convierte el JSON del grafo en listas de Node/Edge de streamlit-agraph."""
    root_id = graph_data.get("root")
    nodes, edges = [], []

    for n in graph_data.get("nodes", []):
        node_type = n.get("type", "UNKNOWN")
        generated = _is_generated(n)
        nodes.append(
            Node(
                id=n["id"],
                label=n.get("label", n["id"]),
                size=26 if n["id"] == root_id else 18,
                color=NODE_COLORS.get(node_type, DEFAULT_COLOR),
                shape="diamond" if generated else "dot",
                borderWidth=3 if generated else 1,
                # borde punteado para las notas GENERADAS (propuestas)
                shapeProperties={"borderDashes": True} if generated else {},
            )
        )

    for e in graph_data.get("edges", []):
        edges.append(
            Edge(
                source=e["source"],
                target=e["target"],
                label=e.get("label", ""),
                dashes=_is_generated(e),
            )
        )

    return nodes, edges


def render_graph(graph_data: dict, height: int = 550):
    """
    Dibuja el grafo y devuelve el id del nodo en el que el usuario hizo clic
    (o None si no hizo clic en nada todavía).
    """
    nodes, edges = build_graph(graph_data)

    config = Config(
        width="100%",
        height=height,
        directed=True,
        physics=True,
        hierarchical=False,
        collapsible=False,
        node={"labelProperty": "label"},
    )

    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)
    return clicked_node_id
