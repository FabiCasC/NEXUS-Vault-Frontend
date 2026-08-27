"""
graph_view.py — LU-3

Pinta el "camino de pertinencia" de un team_data (nodos + aristas) usando
streamlit-agraph:
- Layout JERÁRQUICO izquierda->derecha (no física libre): así se lee como
  una CADENA (Necesidad -> Antecedente/Propuesta -> Equipo), que es
  literalmente el argumento central del proyecto — no un blob de puntos.
- Leyenda visible arriba del grafo: sin ella nadie adivina qué significa
  cada color.
- Etiquetas cortas en el grafo (el texto largo va en la nota, al clic).

Formato esperado de team_data (lo que devuelve form_team / el fixture):
{
  "nodes": [
    {"id": "NEED-001", "type": "NEED", "label": "...", "generado": false, ...},
    {"id": "PROP-001", "type": "PROP", "label": "...", "generado": true}
  ],
  "edges": [
    {"source": "NEED-001", "target": "PROP-001", "weight": 0.83, "dashed": true}
  ]
}
"""

from __future__ import annotations

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# Color por tipo de entidad — el mismo valor se usa en la leyenda, así que
# si lo cambias acá, la leyenda se actualiza sola.
TYPE_COLORS = {
    "NEED": "#E63946",
    "THESIS": "#457B9D",
    "PROJECT": "#1D3557",
    "RESEARCHER": "#2A9D8F",
    "CAPABILITY": "#E9C46A",
    "SUBJECT": "#8D5A97",
    "LAB": "#F4A261",
    "PROP": "#6C757D",
}

TYPE_LABELS_ES = {
    "NEED": "Necesidad",
    "THESIS": "Tesis (antecedente)",
    "PROJECT": "Proyecto (antecedente)",
    "RESEARCHER": "Investigador/a",
    "CAPABILITY": "Capacidad institucional",
    "SUBJECT": "Asignatura",
    "LAB": "Laboratorio",
    "PROP": "Propuesta generada (nueva)",
}

TYPE_SHAPES = {
    "NEED": "diamond",
    "PROP": "star",
}

DEFAULT_COLOR = "#B0B0B0"
DEFAULT_SHAPE = "dot"

_MAX_LABEL_LEN = 34


def _short_label(text: str, max_len: int = _MAX_LABEL_LEN) -> str:
    """El texto completo va en la nota (al clic); en el grafo solo un
    adelanto, para que no se superponga con los nodos vecinos."""
    text = text or ""
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"


def render_legend(team_data: dict) -> None:
    """Leyenda de colores SOLO para los tipos que realmente aparecen en
    este grafo (no satura con tipos que no vienen al caso)."""
    tipos_presentes = {n.get("type", "UNKNOWN") for n in team_data.get("nodes", [])}
    if not tipos_presentes:
        return

    chips = []
    for tipo in sorted(tipos_presentes, key=lambda t: list(TYPE_COLORS).index(t) if t in TYPE_COLORS else 99):
        color = TYPE_COLORS.get(tipo, DEFAULT_COLOR)
        label = TYPE_LABELS_ES.get(tipo, tipo)
        chips.append(
            f'<span style="display:inline-flex;align-items:center;margin-right:14px;'
            f'font-size:0.85rem;white-space:nowrap;">'
            f'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;'
            f'background:{color};margin-right:5px;"></span>{label}</span>'
        )
    st.markdown(
        f'<div style="margin-bottom:6px;">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )
    st.caption("Se lee de izquierda a derecha: Necesidad → antecedente/propuesta → equipo que la cubre.")


def render_graph(team_data: dict, height: int = 550) -> str | None:
    render_legend(team_data)

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
                label=_short_label(n.get("label", n["id"])),
                title=n.get("label", n["id"]),  # tooltip con el texto completo al pasar el mouse
                size=26 if node_type == "NEED" else 18,
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
        width="100%",
        height=height,
        directed=True,
        physics=False,          # sin física libre: queremos una CADENA legible, no un blob
        hierarchical=True,
        direction="LR",         # izquierda -> derecha, como se lee una cadena/ruta
        sortMethod="directed",
        levelSeparation=220,
        nodeSpacing=140,
        nodeHighlightBehavior=True,
        highlightColor="#F7F7F7",
        collapsible=False,
        node={"labelProperty": "label"},
    )

    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)
    return clicked_node_id
