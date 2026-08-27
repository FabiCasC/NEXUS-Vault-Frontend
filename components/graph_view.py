"""
graph_view.py — LU-3 Enriquecido

Pinta el "camino de pertinencia" de un team_data (nodos + aristas) usando
streamlit-agraph:
- Layout JERÁRQUICO izquierda->derecha (cadena de pertinencia clara).
- Leyenda visual moderna con conteo de entidades y chips estilizados.
- Colores vibrantes de alto contraste con soporte de nodos institucionales vs generados.
- Nodos interactivos con selección inmediata de notas.
"""

from __future__ import annotations

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

TYPE_COLORS = {
    "NEED": "#FF4B4B",
    "THESIS": "#38BDF8",
    "PROJECT": "#6366F1",
    "RESEARCHER": "#10B981",
    "CAPABILITY": "#F59E0B",
    "SUBJECT": "#C084FC",
    "LAB": "#FB923C",
    "PROP": "#E879F9",
}

TYPE_LABELS_ES = {
    "NEED": "Necesidad",
    "THESIS": "Tesis",
    "PROJECT": "Proyecto",
    "RESEARCHER": "Investigador/a",
    "CAPABILITY": "Capacidad",
    "SUBJECT": "Asignatura",
    "LAB": "Laboratorio",
    "PROP": "Propuesta IA",
}

TYPE_SHAPES = {
    "NEED": "diamond",
    "PROP": "star",
}

DEFAULT_COLOR = "#94A3B8"
DEFAULT_SHAPE = "dot"
_MAX_LABEL_LEN = 36


def _short_label(text: str, max_len: int = _MAX_LABEL_LEN) -> str:
    text = text or ""
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"


def render_legend(team_data: dict) -> None:
    """Leyenda interactiva con conteo de elementos presentes en el grafo."""
    nodes = team_data.get("nodes", [])
    if not nodes:
        return

    type_counts = {}
    for n in nodes:
        t = n.get("type", "UNKNOWN")
        type_counts[t] = type_counts.get(t, 0) + 1

    chips = []
    for tipo, count in type_counts.items():
        color = TYPE_COLORS.get(tipo, DEFAULT_COLOR)
        label = TYPE_LABELS_ES.get(tipo, tipo)
        chips.append(
            f'<div class="legend-chip" style="border-left: 3px solid {color};">'
            f'<span class="legend-dot" style="background:{color};"></span>'
            f'<span class="legend-label">{label}</span>'
            f'<span class="legend-count">{count}</span>'
            f'</div>'
        )

    st.markdown(
        f"""
        <div class="legend-container">
            <div class="legend-header">
                <span style="font-weight: 600; color: #94A3B8; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.5px;">
                    🗺️ Entidades en este Camino de Pertinencia
                </span>
                <span style="font-size: 0.78rem; color: #64748B;">Flujo: Necesidad ➔ Antecedente / Propuesta ➔ Equipo ejecutor</span>
            </div>
            <div class="legend-chips-grid">
                {"".join(chips)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_graph(team_data: dict, height: int = 560) -> str | None:
    render_legend(team_data)

    nodes = []
    for n in team_data.get("nodes", []):
        node_type = n.get("type", "UNKNOWN")
        is_proposal = node_type == "PROP" or n.get("generado", False)

        extra = {}
        if is_proposal:
            extra["shapeProperties"] = {"borderDashes": [6, 4]}
            extra["borderWidth"] = 3
        else:
            extra["borderWidth"] = 1.5

        node_color = TYPE_COLORS.get(node_type, DEFAULT_COLOR)

        nodes.append(
            Node(
                id=n["id"],
                label=_short_label(n.get("label", n["id"])),
                title=f"[{n['id']}] {n.get('label', '')}\n(Haz clic para abrir nota)",
                size=28 if node_type == "NEED" else (22 if is_proposal else 18),
                color=node_color,
                shape=TYPE_SHAPES.get(node_type, DEFAULT_SHAPE),
                font={"color": "#F1F5F9", "size": 13, "face": "Inter, sans-serif"},
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
                color={"color": "#64748B", "highlight": "#A855F7"},
                font={"color": "#94A3B8", "size": 11, "align": "top"},
                smooth={"type": "cubicBezier", "roundness": 0.2},
            )
        )

    config = Config(
        width="100%",
        height=height,
        directed=True,
        physics=False,
        hierarchical=True,
        direction="LR",
        sortMethod="directed",
        levelSeparation=240,
        nodeSpacing=150,
        nodeHighlightBehavior=True,
        highlightColor="#A855F7",
        collapsible=False,
        node={"labelProperty": "label"},
    )

    clicked_node_id = agraph(nodes=nodes, edges=edges, config=config)
    return clicked_node_id

