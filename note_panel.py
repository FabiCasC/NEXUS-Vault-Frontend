"""
note_panel.py
Dibuja el panel de "nota" tipo Obsidian para el nodo seleccionado en el grafo.

Reglas del reto que este archivo respeta:
- Si el nodo es GENERADO (propuesta), se marca claramente como tal.
- Si el nodo es INSTITUCIONAL, se muestra su fuente exacta: archivo / id / campo.
- Nunca inventa un profesor, laboratorio o dato que no venga en graph_data.
"""

import streamlit as st

TYPE_LABELS = {
    "NEED": "Necesidad",
    "THESIS": "Tesis",
    "PROJECT": "Proyecto",
    "RESEARCHER": "Investigador/a",
    "CAPABILITY": "Capacidad",
    "SUBJECT": "Asignatura",
    "LAB": "Laboratorio",
    "PROP": "Propuesta generada",
}


def _find_node(node_id: str, graph_data: dict):
    for n in graph_data.get("nodes", []):
        if n["id"] == node_id:
            return n
    return None


def _edges_for_node(node_id: str, graph_data: dict):
    return [
        e
        for e in graph_data.get("edges", [])
        if e.get("source") == node_id or e.get("target") == node_id
    ]


def render_note(node_id: str, graph_data: dict) -> None:
    """Punto de entrada llamado desde app.py al hacer clic en un nodo."""
    node = _find_node(node_id, graph_data)
    if node is None:
        st.warning("No encontré ese nodo en los datos actuales.")
        return

    node_type = node.get("type", "UNKNOWN")
    is_generated = node_type == "PROP" or node.get("generated", False)

    badge = "🟡 GENERADO" if is_generated else "🟢 INSTITUCIONAL"
    st.markdown(f"**{node.get('label', node_id)}**")
    st.caption(f"{badge} · {TYPE_LABELS.get(node_type, node_type)}")

    phrase = node.get("phrase") or node.get("frase")
    if phrase:
        st.markdown(f"> {phrase}")

    source = node.get("source")
    if source:
        archivo = source.get("file", "—")
        rid = source.get("id", "—")
        campo = source.get("field", "—")
        st.caption(f"Fuente: `{archivo}` · id `{rid}` · campo `{campo}`")
    elif is_generated:
        st.caption("Fuente: propuesta generada por el sistema, sin fila directa en Data V1.0.")
    else:
        st.caption("Fuente: no especificada en estos datos.")

    skills = node.get("skills")
    if skills:
        st.markdown("**Habilidades**")
        st.write(", ".join(skills))

    related = _edges_for_node(node_id, graph_data)
    if related:
        st.markdown("**Conexiones**")
        for e in related:
            other_id = e["target"] if e["source"] == node_id else e["source"]
            other_node = _find_node(other_id, graph_data)
            other_label = other_node.get("label", other_id) if other_node else other_id
            label = e.get("label", "")
            st.caption(f"— {other_label}" + (f" ({label})" if label else ""))
