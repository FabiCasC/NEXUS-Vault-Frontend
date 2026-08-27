"""
note_panel.py — LU-4 Enriquecido

Renderiza el panel de "nota" (estilo Obsidian Vault) para el nodo que el
usuario clickeó en el grafo:
- Tipo de entidad con badge y color institucional.
- Badge INSTITUCIONAL (Data V1.0) vs GENERADO (Propuesta IA).
- Evidencia auditable: archivo, ID y campo con trazabilidad directa.
- Justificación / Frase en callout destacado.
- Backlinks e interconexiones del cerebro institucional.
"""

from __future__ import annotations

import streamlit as st

TYPE_CONFIG = {
    "NEED": {
        "label": "Necesidad Institucional",
        "icon": "🎯",
        "color": "#FF4B4B",
        "bg_color": "rgba(255, 75, 75, 0.12)",
        "border": "#FF4B4B",
    },
    "THESIS": {
        "label": "Tesis (Antecedente)",
        "icon": "📜",
        "color": "#38BDF8",
        "bg_color": "rgba(56, 189, 248, 0.12)",
        "border": "#38BDF8",
    },
    "PROJECT": {
        "label": "Proyecto de Investigación",
        "icon": "🔬",
        "color": "#6366F1",
        "bg_color": "rgba(99, 102, 241, 0.12)",
        "border": "#6366F1",
    },
    "RESEARCHER": {
        "label": "Investigador/a",
        "icon": "👤",
        "color": "#10B981",
        "bg_color": "rgba(16, 185, 129, 0.12)",
        "border": "#10B981",
    },
    "CAPABILITY": {
        "label": "Capacidad Institucional",
        "icon": "⚡",
        "color": "#F59E0B",
        "bg_color": "rgba(245, 158, 11, 0.12)",
        "border": "#F59E0B",
    },
    "SUBJECT": {
        "label": "Asignatura / Curso",
        "icon": "📚",
        "color": "#C084FC",
        "bg_color": "rgba(192, 132, 252, 0.12)",
        "border": "#C084FC",
    },
    "LAB": {
        "label": "Laboratorio",
        "icon": "🧪",
        "color": "#FB923C",
        "bg_color": "rgba(251, 146, 60, 0.12)",
        "border": "#FB923C",
    },
    "PROP": {
        "label": "Propuesta Generada (Nueva)",
        "icon": "✨",
        "color": "#E879F9",
        "bg_color": "rgba(232, 121, 249, 0.12)",
        "border": "#E879F9",
    },
}

DEFAULT_TYPE_CFG = {
    "label": "Entidad",
    "icon": "📌",
    "color": "#94A3B8",
    "bg_color": "rgba(148, 163, 184, 0.12)",
    "border": "#94A3B8",
}


def render_note(node: dict) -> None:
    node_type = node.get("type", "UNKNOWN")
    cfg = TYPE_CONFIG.get(node_type, DEFAULT_TYPE_CFG)
    is_generado = node.get("generado", False) or node_type == "PROP"

    # Encabezado estilo Obsidian Note con metadata frontmatter
    node_id = node.get("id", "NODE")
    node_label = node.get("label", node_id)

    status_badge_html = (
        f'<span class="badge-generado">✨ PROPUESTA IA</span>'
        if is_generado
        else f'<span class="badge-institucional">🟢 INSTITUCIONAL DATA V1.0</span>'
    )

    st.markdown(
        f"""
        <div class="obsidian-note-card">
            <div class="note-header-row">
                <div class="type-pill" style="background:{cfg['bg_color']}; color:{cfg['color']}; border:1px solid {cfg['border']}40;">
                    {cfg['icon']} {cfg['label']}
                </div>
                {status_badge_html}
            </div>
            <div class="note-title">{node_label}</div>
            <div class="note-id-tag">ID: <code>{node_id}</code></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Frase o descripción destacada
    frase = node.get("frase") or node.get("descripcion")
    if frase:
        st.markdown(
            f"""
            <div class="obsidian-callout">
                <div class="callout-title">💬 Justificación de Pertinencia</div>
                <div class="callout-body">{frase}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Evidencia Auditable
    evidencia = node.get("evidencia")
    if evidencia:
        archivo = evidencia.get("archivo", "—")
        ev_id = evidencia.get("id", node_id)
        campo = evidencia.get("campo", "—")

        st.markdown(
            f"""
            <div class="evidence-box">
                <div class="evidence-header">
                    <span>🔍 <strong>Evidencia Auditable</strong></span>
                    <span class="evidence-badge-verified">Verificado en Origen</span>
                </div>
                <div class="evidence-grid">
                    <div class="evidence-item">
                        <span class="ev-label">📁 Archivo Fuente</span>
                        <span class="ev-value"><code>{archivo}</code></span>
                    </div>
                    <div class="evidence-item">
                        <span class="ev-label">🔑 Registro ID</span>
                        <span class="ev-value"><code>{ev_id}</code></span>
                    </div>
                    <div class="evidence-item">
                        <span class="ev-label">📋 Campo Mapeado</span>
                        <span class="ev-value"><code>{campo}</code></span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif is_generado:
        st.markdown(
            """
            <div class="evidence-box-generated">
                <div style="font-weight: 600; color: #E879F9; margin-bottom: 6px;">
                    ✨ Hallazgo / Propuesta Generada
                </div>
                <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">
                    Este nodo actúa como nodo articulador o equipo mínimo viable formulado
                    a partir de las capacidades institucionales mapeadas.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="evidence-box-warning">
                <span style="font-size: 0.85rem; color: #FBBF24;">
                    ⚠️ Sin archivo de evidencia directo asignado a este nodo.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Backlinks & Conexiones
    backlinks = node.get("backlinks")
    if backlinks:
        st.markdown("<div style='margin-top: 14px; font-weight: 600; font-size: 0.9rem; color: #94A3B8;'>🔗 Backlinks & Vínculos Directos</div>", unsafe_allow_html=True)
        for b in backlinks:
            st.markdown(f"<div class='backlink-chip'>🖇️ {b}</div>", unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-note-state">
            <div class="empty-icon">🗂️</div>
            <div class="empty-title">Panel de Nota (Obsidian Vault)</div>
            <div class="empty-text">
                Haz clic en cualquier nodo del grafo para desplegar su ficha técnica institucional,
                trazabilidad de evidencia y justificación del modelo.
            </div>
            <div class="empty-hint">
                💡 <em>Los nodos diamante son necesidades, estrellas son propuestas y círculos son entidades institucionales reales.</em>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

