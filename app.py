"""
app.py
Shell principal de NEXUS Vault (frontend puro).

Este repo NO calcula el equipo mínimo ni corre el algoritmo de set cover.
Eso vive en el backend (repo NEXUS-Vault-API, backend/team_formation.py +
backend/api.py). Este archivo:
  1. Le pega por HTTP a NEXUS_API_URL/form-team (backend real, otro proceso).
  2. Si la API no responde o falla, usa una fixture local en /fixtures para
     que la interfaz nunca se caiga (LU-5).
  3. Dibuja el grafo (graph_view.py) y el panel de nota (note_panel.py).
"""

import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from graph_view import render_graph
from note_panel import render_note

# El backend vive en OTRO repo/proceso — se habla por HTTP, no por import.
# Configurable por si alguien lo corre en otro puerto/máquina el día de la demo.
API_URL = os.environ.get("NEXUS_API_URL", "http://localhost:8000").rstrip("/")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FIXTURES_DIR = BASE_DIR / "fixtures"

st.set_page_config(page_title="NEXUS Vault", page_icon="🔗", layout="wide")


@st.cache_data
def load_needs() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "institutional_needs.csv")


@st.cache_data(ttl=5)
def api_is_alive() -> bool:
    """Chequeo rápido para el badge de estado (se re-evalúa cada 5s, por si
    Fabiana/Kevin levantan la API mientras la demo ya está abierta)."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        return r.ok
    except requests.RequestException:
        return False


def load_fixture(need_id: str | None) -> dict:
    """Fixture local de respaldo. Si no hay una fixture con ese id, usa default.json."""
    fixture_path = FIXTURES_DIR / f"{need_id}.json" if need_id else None
    if fixture_path is None or not fixture_path.exists():
        fixture_path = FIXTURES_DIR / "default.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


def fetch_from_api(need_id: str | None, free_text: str | None, timeout: float = 8.0) -> dict:
    params = {}
    if need_id:
        params["need_id"] = need_id
    if free_text:
        params["free_text"] = free_text
    resp = requests.get(f"{API_URL}/form-team", params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise ValueError(data["error"])
    return data


def get_graph_data(need_id: str | None = None, free_text: str | None = None) -> dict:
    """
    Punto único para conseguir el grafo a mostrar.
    Intenta la API real / si falla, cae a fixture. Nunca revienta la UI.
    """
    try:
        return fetch_from_api(need_id=need_id, free_text=free_text)
    except Exception as exc:  # la API puede fallar por mil razones distintas
        st.warning(f"No pude conectar con la API ({exc}). Mostrando datos de ejemplo.")
        return load_fixture(need_id)


def main() -> None:
    st.title("🔗 NEXUS Vault")
    st.caption("Cerebro institucional tipo Obsidian — cobertura de equipo + huecos + evidencia")

    needs_df = load_needs()
    backend_ok = api_is_alive()

    col_side, col_graph, col_note = st.columns([1, 2, 1.3])

    with col_side:
        badge = "🟢 API conectada" if backend_ok else "🔴 API no responde (usando ejemplos)"
        st.caption(f"{badge} · `{API_URL}`")

        st.subheader("Idea libre")
        free_text = st.text_area(
            "Describe una necesidad con tus palabras",
            placeholder="Ej: necesitamos reducir la deserción en primer año...",
            key="free_text_input",
        )
        run_free = st.button("Explorar idea", type="primary")

        st.markdown("---")
        st.subheader("O elige una NEED real")
        options = ["-- elegir --"] + [
            f"{row.id} · {row.title}" for row in needs_df.itertuples()
        ]
        choice = st.selectbox("NEED institucional (42 reales)", options, key="need_choice")

    need_id = None
    graph_data = None

    if run_free and free_text and free_text.strip():
        graph_data = get_graph_data(free_text=free_text)
    elif choice != "-- elegir --":
        need_id = choice.split(" · ")[0]
        graph_data = get_graph_data(need_id=need_id)

    if graph_data is None:
        with col_graph:
            st.info("Escribe una idea libre o elige una NEED del combo para ver el grafo.")
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
