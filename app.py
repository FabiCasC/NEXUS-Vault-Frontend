"""
NEXUS Vault — Frontend (Streamlit)
Knowledge Nexus LATAM · Hackathon Perú 2026

Shell principal: layout de dos columnas (grafo | nota).

Flujo principal: el usuario escribe una idea/problema en texto libre
y eso CREA un NEED (vía API). El combo de necesidades existentes es
secundario, para explorar lo que ya está en Data V1.0.

Tareas cubiertas:
LU-1 shell + layout
LU-2 combo de NEEDs (secundario)
LU-3 graph_view (delegado)
LU-4 click en nodo -> note_panel.render_note
LU-5 team_api: llamada a API real con fallback a fixture
LU-6 caja de idea libre -> crea un NEED nuevo, sin crashear
"""

from __future__ import annotations

import streamlit as st

from services.team_api import explore
from services.needs_loader import load_needs
from components.graph_view import render_graph
from components.note_panel import render_note, render_empty_state

st.set_page_config(
    page_title="NEXUS Vault",
    page_icon="🗂️",
    layout="wide",
)

# ---------- estado de sesión ----------
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None
if "current_team_data" not in st.session_state:
    st.session_state.current_team_data = None
if "current_need" not in st.session_state:
    st.session_state.current_need = None
if "last_query_label" not in st.session_state:
    st.session_state.last_query_label = None


def find_node(team_data: dict, node_id: str) -> dict | None:
    for n in team_data.get("nodes", []):
        if n.get("id") == node_id:
            return n
    return None


# ---------- header ----------
st.title("🗂️ NEXUS Vault")
st.caption("Cerebro institucional tipo Obsidian — Knowledge Nexus LATAM")

# ---------- sidebar ----------
with st.sidebar:
    st.subheader("💡 Nueva necesidad")
    st.caption("Escribe un problema o idea — se crea un NEED nuevo.")

    free_text = st.text_area(
        "¿Qué problema quieres explorar?",
        placeholder="Ej: predicción de deserción en cursos de ciencias básicas...",
        height=110,
        label_visibility="collapsed",
    )
    create_submit = st.button("✨ Crear necesidad y explorar", use_container_width=True, type="primary")

    st.divider()

    with st.expander("O elige una necesidad que ya existe"):
        needs_df = load_needs()
        options = ["— Selecciona —"] + [f"{row['id']} · {row['title']}" for _, row in needs_df.iterrows()]
        choice = st.selectbox("Necesidad institucional (NEED)", options, index=0, label_visibility="collapsed")
        existing_submit = st.button("Explorar esta necesidad", use_container_width=True)

# ---------- disparo de la consulta ----------
need_id = None
query_free_text = None

if create_submit and free_text.strip():
    query_free_text = free_text.strip()

if existing_submit and choice != "— Selecciona —":
    need_id = choice.split(" · ")[0]

if need_id or query_free_text:
    with st.spinner("Armando equipo..."):
        result, source, mapped = explore(need_id=need_id, free_text=query_free_text)

    st.session_state.current_team_data = result.get("team_data")
    st.session_state.current_need = result.get("need")
    st.session_state.selected_node = None  # limpia selección anterior

    need_label = None
    if result.get("need"):
        need_label = f"{result['need'].get('id', '')} · {result['need'].get('title', '')}"
    st.session_state.last_query_label = need_label

    if source == "fixture":
        st.sidebar.info("API aún no disponible — mostrando datos de ejemplo (fixture).", icon="⚠️")
    if query_free_text and not mapped:
        st.sidebar.warning(
            "El NEED se creó localmente porque la API no respondió todavía. "
            "En cuanto esté arriba, esta idea se mandará de verdad.",
            icon="💡",
        )
    elif query_free_text and mapped:
        st.sidebar.success(f"Necesidad creada: {need_label}", icon="✅")

# ---------- layout principal: grafo | nota ----------
col_graph, col_note = st.columns([2, 1], gap="large")

with col_graph:
    st.subheader("Grafo")
    if st.session_state.last_query_label:
        st.caption(st.session_state.last_query_label)

    if st.session_state.current_team_data and st.session_state.current_team_data.get("nodes"):
        clicked_id = render_graph(st.session_state.current_team_data)
        if clicked_id:
            st.session_state.selected_node = clicked_id
    else:
        st.info("Escribe una idea y crea una necesidad, o elige una existente, para ver el grafo.")

with col_note:
    st.subheader("Nota")
    if st.session_state.selected_node and st.session_state.current_team_data:
        node = find_node(st.session_state.current_team_data, st.session_state.selected_node)
        if node:
            render_note(node)
        else:
            render_empty_state()
    else:
        render_empty_state()
