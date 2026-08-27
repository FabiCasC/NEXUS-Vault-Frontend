"""
app.py
Shell principal de NEXUS Vault (frontend puro).

Este repo NO calcula el equipo mínimo ni corre el algoritmo de set cover.
Eso vive en form_team.py (backend/Kevin). Este archivo:
  1. Intenta llamar a form_team(need_id, free_text).
  2. Si form_team no existe todavía o falla, usa una fixture local en
     /fixtures para que la interfaz nunca se caiga (LU-5).
  3. Dibuja el grafo (graph_view.py) y el panel de nota (note_panel.py).
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from graph_view import render_graph
from note_panel import render_note

try:
    from form_team import form_team  # backend real, aún no existe en este repo

    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FIXTURES_DIR = BASE_DIR / "fixtures"

st.set_page_config(page_title="NEXUS Vault", page_icon="🔗", layout="wide")


@st.cache_data
def load_needs() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "institutional_needs.csv")


def load_fixture(need_id: str | None) -> dict:
    """Fixture local de respaldo. Si no hay una fixture con ese id, usa default.json."""
    fixture_path = FIXTURES_DIR / f"{need_id}.json" if need_id else None
    if fixture_path is None or not fixture_path.exists():
        fixture_path = FIXTURES_DIR / "default.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


def get_graph_data(need_id: str | None = None, free_text: str | None = None) -> dict:
    """
    Punto único para conseguir el grafo a mostrar.
    try form_team (real) / except -> fixture (local). Nunca revienta la UI.
    """
    if HAS_BACKEND:
        try:
            return form_team(need_id=need_id, free_text=free_text)
        except Exception as exc:  # el backend puede fallar por mil razones distintas
            st.warning(f"form_team falló ({exc}). Mostrando datos de ejemplo.")

    return load_fixture(need_id)


def main() -> None:
    st.title("🔗 NEXUS Vault")
    st.caption("Cerebro institucional tipo Obsidian — cobertura de equipo + huecos + evidencia")

    needs_df = load_needs()

    col_side, col_graph, col_note = st.columns([1, 2, 1.3])

    with col_side:
        st.subheader("Buscar")
        options = ["-- elegir --"] + [
            f"{row.id} · {row.title}" for row in needs_df.itertuples()
        ]
        choice = st.selectbox("NEED institucional", options, key="need_choice")

        st.markdown("---")
        st.subheader("Idea libre")
        free_text = st.text_area(
            "Describe una necesidad con tus palabras",
            placeholder="Ej: necesitamos reducir la deserción en primer año...",
            key="free_text_input",
        )
        run_free = st.button("Explorar idea")

        if not HAS_BACKEND:
            st.markdown("---")
            st.caption("⚠️ form_team.py aún no está conectado — usando fixtures de ejemplo.")

    need_id = None
    graph_data = None

    if choice != "-- elegir --":
        need_id = choice.split(" · ")[0]
        graph_data = get_graph_data(need_id=need_id)
    elif run_free:
        if free_text and free_text.strip():
            graph_data = get_graph_data(free_text=free_text)
        else:
            st.info("Usa el combo de arriba, o escribe algo en la caja de idea libre.")

    if graph_data is None:
        with col_graph:
            st.info("Elige una NEED en el combo o escribe una idea libre para ver el grafo.")
        with col_note:
            st.caption("Aquí aparecerá la nota del nodo que elijas.")
        return

    with col_graph:
        st.subheader("Grafo")
        clicked = render_graph(graph_data)
        if clicked:
            st.session_state["selected_node"] = clicked

    with col_note:
        st.subheader("Nota")
        selected = st.session_state.get("selected_node")
        if selected:
            render_note(selected, graph_data)
        else:
            st.caption("Haz clic en un nodo del grafo para ver su nota.")


if __name__ == "__main__":
    main()
