"""
note_panel.py — LU-4

Renderiza el panel de "nota" (estilo Obsidian) para el nodo que el
usuario clickeó en el grafo:
- Tipo de entidad (Necesidad, Tesis, Investigador, ...).
- Badge INSTITUCIONAL (viene del ZIP) vs GENERADO (lo escribió el LLM).
- Evidencia: archivo / id / campo — trazabilidad hasta Data V1.0.
- Frase o descripción del nodo, si existe.
- Backlinks, si el backend los manda.

Este archivo es TUYO (LU-4 dice explícitamente "el archivo TÚ") —
la lógica ya funciona con el fixture, ajusta textos/orden a gusto.
"""

from __future__ import annotations

import streamlit as st

TYPE_LABELS = {
    "NEED": "Necesidad",
    "THESIS": "Tesis",
    "PROJECT": "Proyecto",
    "RESEARCHER": "Investigador",
    "CAPABILITY": "Capacidad",
    "SUBJECT": "Asignatura",
    "LAB": "Laboratorio",
    "PROP": "Propuesta (nota nueva)",
}


def render_note(node: dict) -> None:
    node_type = node.get("type", "UNKNOWN")
    is_generado = node.get("generado", False) or node_type == "PROP"

    st.markdown(f"### {node.get('label', node.get('id'))}")

    badge = "🟣 GENERADO" if is_generado else "🟢 INSTITUCIONAL"
    st.markdown(f"**{TYPE_LABELS.get(node_type, node_type)}** · {badge}")

    st.divider()

    evidencia = node.get("evidencia")
    if evidencia:
        st.markdown("**Evidencia**")
        st.code(
            f"archivo: {evidencia.get('archivo', '—')}\n"
            f"id: {evidencia.get('id', node.get('id', '—'))}\n"
            f"campo: {evidencia.get('campo', '—')}",
            language="text",
        )
    elif is_generado:
        st.info(
            "Esta nota fue generada porque el equipo cubre la necesidad "
            "pero todavía no existe como proyecto o tesis en Data V1.0.",
            icon="✨",
        )
    else:
        st.warning("Sin evidencia registrada para este nodo todavía.", icon="⚠️")

    frase = node.get("frase") or node.get("descripcion")
    if frase:
        st.divider()
        st.markdown("**Frase / descripción**")
        st.write(frase)

    backlinks = node.get("backlinks")
    if backlinks:
        st.divider()
        st.markdown("**Backlinks**")
        for b in backlinks:
            st.markdown(f"- {b}")


def render_empty_state() -> None:
    st.info("Haz clic en un nodo del grafo para abrir su nota aquí.", icon="👈")
