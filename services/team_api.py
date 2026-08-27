"""
team_api.py — LU-5 (corregido según nota de Lucía sobre el front anterior)

En vez de importar form_team como módulo local, se llama a la API real:

    GET http://localhost:8000/form-team?need_id=NEED-001
    GET http://localhost:8000/form-team?free_text=texto+del+usuario

La respuesta ya viene en el mismo esquema que los fixtures locales:
{
  "nodes": [{"id": "...", "type": "NEED"|"THESIS"|..., "label": "...",
              "generado": bool, "evidencia": {...}|null, "frase": "..."}],
  "edges": [{"source": "...", "target": "...", "weight": 0.0}]
}

Si la API no responde (no está levantada, timeout, error), cae a un
fixture local para que la UI nunca se caiga durante desarrollo o demo.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import requests
import streamlit as st

FIXTURE_DIR = Path(__file__).parent.parent / "data" / "fixtures"
DEFAULT_FIXTURE = FIXTURE_DIR / "sample_team.json"


def _api_url() -> str:
    """Prioridad: .streamlit/secrets.toml -> variable de entorno -> default local."""
    try:
        return st.secrets["api"]["url"].rstrip("/")
    except Exception:
        return os.environ.get("NEXUS_API_URL", "http://localhost:8000").rstrip("/")


def explore(need_id: str | None = None, free_text: str | None = None, timeout: float = 8.0):
    """
    Devuelve (result: dict, source: "api"|"fixture", mapped: bool)
    result = {"need": {...} | None, "team_data": {"nodes": [...], "edges": [...]}}
    mapped = False cuando la idea libre no pudo procesarse de verdad
             (típicamente porque estamos en modo fixture).
    """
    params = {}
    if need_id:
        params["need_id"] = need_id
    if free_text:
        params["free_text"] = free_text

    if not params:
        return {"need": None, "team_data": {"nodes": [], "edges": []}}, "fixture", False

    try:
        resp = requests.get(f"{_api_url()}/form-team", params=params, timeout=timeout)
        resp.raise_for_status()
        team_data = resp.json()

        if not team_data or not team_data.get("nodes"):
            raise ValueError("la API respondió sin nodes")

        need = _need_from_team_data(team_data, need_id)
        return {"need": need, "team_data": team_data}, "api", True

    except Exception as e:
        print(f"[team_api] API no disponible ({_api_url()}/form-team), usando fixture: {e}")
        return _fallback(need_id, free_text)


# ---------------- fallback local (fixtures) ----------------

def _fallback(need_id, free_text):
    fixture_path = FIXTURE_DIR / f"{need_id}.json" if need_id else None

    if fixture_path and fixture_path.exists():
        team_data = _read_json(fixture_path)
        need = _need_from_team_data(team_data, need_id)
        return {"need": need, "team_data": team_data}, "fixture", True

    if not DEFAULT_FIXTURE.exists():
        return {"need": None, "team_data": {"nodes": [], "edges": []}}, "fixture", False

    team_data = _read_json(DEFAULT_FIXTURE)

    if free_text:
        fake_id = f"NEED-LOCAL-{hashlib.md5(free_text.encode()).hexdigest()[:6]}"
        team_data = _inject_free_text_need(team_data, fake_id, free_text)
        need = {"id": fake_id, "title": free_text, "generado": True}
        return {"need": need, "team_data": team_data}, "fixture", False

    need = _need_from_team_data(team_data, need_id)
    return {"need": need, "team_data": team_data}, "fixture", True


def _read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _need_from_team_data(team_data: dict, need_id: str | None) -> dict | None:
    for n in team_data.get("nodes", []):
        if n.get("type") == "NEED" and (need_id is None or n.get("id") == need_id):
            return n
    return None


def _inject_free_text_need(team_data: dict, fake_id: str, free_text: str) -> dict:
    """Reemplaza el nodo NEED del fixture por uno con el texto que escribió
    el usuario, y reapunta las aristas que salían del NEED original."""
    team_data = json.loads(json.dumps(team_data))  # copia profunda simple
    old_need_id = None

    for n in team_data.get("nodes", []):
        if n.get("type") == "NEED":
            old_need_id = n["id"]
            n["id"] = fake_id
            n["label"] = free_text
            n["generado"] = True
            n["evidencia"] = None
            n["frase"] = "Necesidad creada a partir de una idea libre (modo fixture, sin API todavía)."
            break

    if old_need_id:
        for e in team_data.get("edges", []):
            if e.get("source") == old_need_id:
                e["source"] = fake_id
            if e.get("target") == old_need_id:
                e["target"] = fake_id

    return team_data
