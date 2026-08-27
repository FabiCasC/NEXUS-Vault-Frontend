"""
graph_view.py — LU-3

Pinta el grafo de un "team_data" (nodos + aristas) usando streamlit-agraph.
- Colorea cada nodo según su tipo (NEED, THESIS, PROJECT, RESEARCHER, ...).
- Los nodos tipo PROP (propuesta generada, todavía no existe en Data V1.0)
  se dibujan con borde punteado para distinguirlos de lo institucional.
- Devuelve el id del nodo que el usuario clickeó (o None si no clickeó nada).

Formato esperado de team_data (lo que debería devolver form_team / el fixture):
{
  "nodes": [
    {"id": "NEED-001", "type": "NEED", "label": "...", "generado": false, ...},
    {"id": "PROP-001", "type": "PROP", "label": "...", "generado": true, ...}
  ],
  "edges": [
    {"source": "NEED-001", "target": "PROP-001", "weight": 0.83}
  ]
}
"""

from __future__ import annotations

from streamlit_agraph import agraph, Node, Edge, Config

# Color por tipo de entidad — ajustar a gusto, esto es solo punto de partida.
TYPE_COLORS = {
    "NEED": "#E63946",
    "THESIS": "#457B9D",
    "PROJECT": "#1D3557",
    "RESEARCHER": "#2A9D8F",
    "CAPABILITY": "#E9C46A",
    "SUBJECT": "#8D5A97",
    "LAB": "#F4A261",
    "PROP": "#6C757D",  # propuesta generada — se distingue por el borde punteado
}

TYPE_SHAPES = {
    "NEED": "diamond",
    "PROP": "star",
}

DEFAULT_COLOR = "#B0B0B0"
DEFAULT_SHAPE = "dot"


def render_graph(team_data: dict) -> str | None:
    nodes = []
    for n in team_data.get("nodes", []):
        node_type = n.get("type", "UNKNOWN")
        is_proposal = node_type == "PROP" or n.get("generado", False)

        extra = {}
        if is_proposal:
            # borde punteado para notas-propuesta (todavía no existen en el ZIP)
            extra["shapeProperties"] = {"borderDashes": [5, 5]}
            extra["borderWidth"] = 2

        nodes.append(
            Node(
                id=n["id"],
                label=n.get("label", n["id"]),
                size=24 if node_type == "NEED" else 16,
                color=TYPE_COLORS.get(node_type, DEFAULT_COLOR),
                shape=TYPE_SHAPES.get(node_type, DEFAULT_SHAPE),
                **extra,
            )
        )

    node_lookup = {n["id"]: n for n in team_data.get("nodes", [])}

    edges = []
    for e in team_data.get("edges", []):
        weight = e.get("weight")
        label = f"{weight:.2f}" if isinstance(weight, (int, float)) else ""

        target_node = node_lookup.get(e.get("target"), {})
        is_dashed = e.get("dashed", False) or target_node.get("type") == "PROP" or target_node.get("generado", False)

        edges.append(
            Edge(
                source=e["source"],
                target=e["target"],
                label=label,
                dashes=is_dashed,
            )
        )

    config = Config(
        width=900,
        height=600,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#F7F7F7",
        collapsible=False,
    )

    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)
    return clicked_node_id
