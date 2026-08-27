"""
NEXUS Vault — Frontend (Streamlit)
Knowledge Nexus LATAM · Hackathon Perú 2026

Interfaz de Alto Impacto Visual y Experiencia de Usuario (UX/UI):
- Estética Obsidian Dark Vault / Cyber Knowledge Network.
- Hero Header animado con badges de conexión y estado institucional.
- Presets rápidos de 1 clic para demos en vivo (Desafíos universitarios).
- KPI Cards con métricas de pertinencia, composición de equipo y trazabilidad.
- Layout de 3 Vistas en Pestañas:
  1. 🗺️ Grafo de Pertinencia & Panel de Nota Obsidian.
  2. 📋 Ficha Ejecutiva del Equipo (Executive Brief para Decanatura/VRIP).
  3. 🔍 Matriz de Evidencia & Trazabilidad Auditable (Data V1.0).
- Sidebar enriquecida con explorador de necesidades e ingreso de ideas libres.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from services.team_api import explore
from services.needs_loader import load_needs
from components.graph_view import render_graph
from components.note_panel import render_note, render_empty_state

# ---------- Configuración de Página ----------
st.set_page_config(
    page_title="NEXUS Vault — Cerebro Institucional",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Inyección de CSS Global de Alto Impacto ----------
st.markdown(
    """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Estilos Base & Tipografía */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E2E8F0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    code {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Fondo de la Aplicación con Gradiente Sutil */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #131728 0%, #0B0D14 60%, #07080C 100%);
    }

    /* Hero Banner Principal */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-title-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 8px;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 20%, #E9D5FF 60%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hero-badge-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .status-badge-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34D399;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 9999px;
        letter-spacing: 0.5px;
    }

    .status-badge-fixture {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #FBBF24;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 5px 12px;
        border-radius: 9999px;
        letter-spacing: 0.5px;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.96rem;
        line-height: 1.5;
        max-width: 900px;
        margin-bottom: 0;
    }

    /* KPI Metrics Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin-bottom: 22px;
    }

    .kpi-card {
        background: rgba(19, 23, 34, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 16px 20px;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(168, 85, 247, 0.4);
    }

    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
    }

    .kpi-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .kpi-icon {
        font-size: 1.1rem;
    }

    .kpi-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.65rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }

    .kpi-subtext {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Obsidian Note Card en Panel Lateral */
    .obsidian-note-card {
        background: linear-gradient(180deg, rgba(24, 28, 42, 0.9) 0%, rgba(15, 18, 28, 0.9) 100%);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
    }

    .note-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 12px;
    }

    .type-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 8px;
    }

    .badge-institucional {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        font-size: 0.74rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }

    .badge-generado {
        background: rgba(232, 121, 249, 0.15);
        color: #E879F9;
        border: 1px solid rgba(232, 121, 249, 0.3);
        font-size: 0.74rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        letter-spacing: 0.5px;
    }

    .note-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.35;
        margin-bottom: 6px;
    }

    .note-id-tag {
        font-size: 0.78rem;
        color: #64748B;
    }

    .obsidian-callout {
        background: rgba(30, 27, 75, 0.35);
        border-left: 3px solid #A855F7;
        border-radius: 0 10px 10px 0;
        padding: 14px 16px;
        margin: 14px 0;
    }

    .callout-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #C084FC;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .callout-body {
        font-size: 0.9rem;
        color: #E2E8F0;
        line-height: 1.5;
    }

    .evidence-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 10px;
        padding: 14px;
        margin-top: 14px;
    }

    .evidence-box-generated {
        background: rgba(30, 27, 75, 0.3);
        border: 1px dashed rgba(232, 121, 249, 0.4);
        border-radius: 10px;
        padding: 14px;
        margin-top: 14px;
    }

    .evidence-box-warning {
        background: rgba(30, 27, 40, 0.4);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px;
        padding: 12px;
        margin-top: 14px;
    }

    .evidence-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 0.86rem;
        color: #38BDF8;
    }

    .evidence-badge-verified {
        background: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 7px;
        border-radius: 4px;
    }

    .evidence-grid {
        display: grid;
        gap: 8px;
    }

    .evidence-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.82rem;
        padding: 4px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .evidence-item:last-child {
        border-bottom: none;
    }

    .ev-label {
        color: #94A3B8;
    }

    .ev-value code {
        background: rgba(0, 0, 0, 0.3);
        padding: 2px 6px;
        border-radius: 4px;
        color: #38BDF8;
        font-size: 0.8rem;
    }

    .backlink-chip {
        display: inline-block;
        background: rgba(148, 163, 184, 0.1);
        border: 1px solid rgba(148, 163, 184, 0.2);
        color: #CBD5E1;
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 6px;
        margin: 4px 4px 4px 0;
    }

    /* Estado Vacío de Nota */
    .empty-note-state {
        background: rgba(19, 23, 34, 0.4);
        border: 1px dashed rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 36px 20px;
        text-align: center;
    }

    .empty-icon {
        font-size: 2.4rem;
        margin-bottom: 10px;
        opacity: 0.7;
    }

    .empty-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-bottom: 6px;
    }

    .empty-text {
        font-size: 0.85rem;
        color: #94A3B8;
        line-height: 1.5;
        max-width: 280px;
        margin: 0 auto 12px auto;
    }

    .empty-hint {
        font-size: 0.78rem;
        color: #64748B;
    }

    /* Leyenda del Grafo */
    .legend-container {
        background: rgba(19, 23, 34, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 14px;
    }

    .legend-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 10px;
    }

    .legend-chips-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .legend-chip {
        display: inline-flex;
        align-items: center;
        background: rgba(15, 23, 42, 0.7);
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 0.8rem;
        gap: 6px;
    }

    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .legend-label {
        color: #CBD5E1;
        font-weight: 500;
    }

    .legend-count {
        background: rgba(255, 255, 255, 0.1);
        color: #94A3B8;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 1px 6px;
        border-radius: 999px;
    }

    /* Ficha Ejecutiva */
    .brief-card {
        background: linear-gradient(135deg, rgba(24, 28, 42, 0.9) 0%, rgba(15, 18, 28, 0.9) 100%);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-radius: 16px;
        padding: 26px;
        margin-bottom: 20px;
    }

    .brief-section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #C084FC;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brief-team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 14px;
        margin-top: 14px;
    }

    .brief-member-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 16px;
    }

    /* Sidebar Styling */
    .sidebar-section-title {
        font-size: 0.82rem;
        font-weight: 700;
        color: #A855F7;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
        margin-top: 14px;
    }

    /* Estilo de Botones Streamlit */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #9333EA 0%, #7E22CE 100%);
        border: 1px solid #C084FC;
        box-shadow: 0 4px 14px rgba(147, 51, 234, 0.35);
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #A855F7 0%, #9333EA 100%);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.5);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Estado de Sesión ----------
if "selected_node" not in st.session_state:
    st.session_state.selected_node = None
if "current_team_data" not in st.session_state:
    st.session_state.current_team_data = None
if "current_need" not in st.session_state:
    st.session_state.current_need = None
if "last_query_label" not in st.session_state:
    st.session_state.last_query_label = None
if "api_source" not in st.session_state:
    st.session_state.api_source = "fixture"
if "mapped_status" not in st.session_state:
    st.session_state.mapped_status = False


def find_node(team_data: dict, node_id: str) -> dict | None:
    for n in team_data.get("nodes", []):
        if n.get("id") == node_id:
            return n
    return None


# Helper para métricas ejecutivas
def calculate_metrics(team_data: dict) -> dict:
    if not team_data or not team_data.get("nodes"):
        return {}

    nodes = team_data.get("nodes", [])
    edges = team_data.get("edges", [])

    total_nodes = len(nodes)
    weights = [e.get("weight") for e in edges if isinstance(e.get("weight"), (int, float))]
    avg_relevance_raw = (sum(weights) / len(weights)) if weights else 0.0
    # "weight" es una suma de coincidencias de habilidades, no una probabilidad:
    # una entidad que coincide con varias skills a la vez puede pasar de 1.0.
    # Para mostrarlo como % (0-100) hay que acotarlo; el valor crudo se sigue
    # usando tal cual para decidir el equipo, esto es solo para la tarjeta KPI.
    avg_relevance = min(1.0, avg_relevance_raw)

    researchers = sum(1 for n in nodes if n.get("type") == "RESEARCHER")
    capabilities = sum(1 for n in nodes if n.get("type") == "CAPABILITY")
    subjects = sum(1 for n in nodes if n.get("type") == "SUBJECT")
    theses = sum(1 for n in nodes if n.get("type") == "THESIS")
    projects = sum(1 for n in nodes if n.get("type") == "PROJECT")

    institutional_count = sum(1 for n in nodes if not n.get("generado", False) and n.get("type") != "PROP")
    traceability_pct = int((institutional_count / total_nodes) * 100) if total_nodes > 0 else 0

    has_proposal = any(n.get("type") == "PROP" or n.get("generado", False) for n in nodes)

    return {
        "avg_relevance": avg_relevance,
        "total_nodes": total_nodes,
        "researchers": researchers,
        "capabilities": capabilities,
        "subjects": subjects,
        "theses": theses,
        "projects": projects,
        "institutional_count": institutional_count,
        "traceability_pct": traceability_pct,
        "has_proposal": has_proposal,
    }


# ---------- Hero Banner Header ----------
badge_html = (
    '<span class="status-badge-live">🟢 API EN VIVO CONECTADA</span>'
    if st.session_state.api_source == "api"
    else '<span class="status-badge-fixture">⚡ MODO RESILIENTE · DATA V1.0</span>'
)

st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-title-row">
            <h1 class="hero-title">
                <span>🗂️</span> NEXUS Vault
            </h1>
            <div class="hero-badge-container">
                {badge_html}
                <span style="font-size:0.78rem; background:rgba(255,255,255,0.06); padding:5px 10px; border-radius:999px; border:1px solid rgba(255,255,255,0.1); color:#94A3B8;">
                    Hackathon Perú 2026
                </span>
            </div>
        </div>
        <p class="hero-subtitle">
            Cerebro institucional de interconexión y pertinencia. Formula el <strong>equipo mínimo real</strong>
            (antecedente + investigador + capacidad + asignatura puente) con <strong>trazabilidad auditable</strong>
            hasta las fuentes oficiales de datos.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar de Exploración & Presets ----------
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">💡 Formular Nueva Necesidad</div>', unsafe_allow_html=True)
    st.caption("Escribe un desafío real de tu institución o industria para generar su equipo articulador:")

    # Preset selector rápido
    preset_choice = st.selectbox(
        "Sugerencias de Desafíos (1 Clic)",
        [
            "— Selecciona una idea rápida —",
            "Predicción y prevención de deserción estudiantil en ciencias básicas",
            "Monitoreo de calidad de agua y relaves en cuencas mineras con IoT",
            "Diagnóstico temprano de anemia infantil en zonas altoandinas con visión computacional",
            "Generación y almacenamiento de energía solar en comunidades aisladas",
        ],
        index=0,
    )

    default_text = "" if preset_choice.startswith("—") else preset_choice

    free_text = st.text_area(
        "Descripción del Problema o Necesidad",
        value=default_text,
        placeholder="Ej: Desarrollo de modelos de IA para predicción de rendimiento académico...",
        height=115,
        help="El sistema procesará tu texto para mapear antecedentes, investigadores idóneos y asignaturas vinculadas.",
    )

    create_submit = st.button("✨ Formular Equipo con IA", use_container_width=True, type="primary")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 18px 0;'>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">📚 Banco Institucional (Data V1.0)</div>', unsafe_allow_html=True)
    with st.expander("Explorar Necesidades Registradas", expanded=False):
        needs_df = load_needs()
        options = ["— Selecciona una necesidad —"] + [f"{row['id']} · {row['title']}" for _, row in needs_df.iterrows()]
        choice = st.selectbox("Catálogo de Necesidades (NEED)", options, index=0, label_visibility="collapsed")
        existing_submit = st.button("🔍 Explorar Selección", use_container_width=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 18px 0;'>", unsafe_allow_html=True)

    # Info Card en Sidebar
    st.markdown(
        """
        <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(148,163,184,0.12); border-radius:10px; padding:12px; font-size:0.8rem; color:#94A3B8;">
            <strong style="color:#C084FC;">📖 Cadena de Pertinencia</strong><br>
            El grafo vincula la <span style="color:#FF4B4B;">Necesidad</span> con un <span style="color:#38BDF8;">Antecedente</span> o <span style="color:#E879F9;">Propuesta</span>, identificando al <span style="color:#10B981;">Investigador líder</span>, la <span style="color:#F59E0B;">Capacidad</span> y la <span style="color:#C084FC;">Asignatura</span> que garantiza transferencia a docencia.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Disparo de la Consulta ----------
need_id = None
query_free_text = None

if create_submit and free_text.strip():
    query_free_text = free_text.strip()

if existing_submit and choice != "— Selecciona una necesidad —":
    need_id = choice.split(" · ")[0]

if need_id or query_free_text:
    with st.spinner("Analizando grafo de pertinencia y conformando equipo..."):
        result, source, mapped = explore(need_id=need_id, free_text=query_free_text)

    st.session_state.current_team_data = result.get("team_data")
    st.session_state.current_need = result.get("need")
    st.session_state.selected_node = None  # limpia selección anterior
    st.session_state.api_source = source
    st.session_state.mapped_status = mapped

    need_label = None
    if result.get("need"):
        need_label = f"{result['need'].get('id', '')} · {result['need'].get('title', '')}"
    st.session_state.last_query_label = need_label

    if source == "fixture":
        st.sidebar.info("Modo Resiliente: Visualizando estructura institucional verificada.", icon="⚡")
    if query_free_text and not mapped:
        st.sidebar.warning(
            "La necesidad se estructuró con el catálogo institucional local de Data V1.0.",
            icon="💡",
        )
    elif query_free_text and mapped:
        st.sidebar.success(f"Equipo conformado con éxito para: {need_label}", icon="✅")

# Carga automática por defecto si no hay nada en sesión para mostrar de inmediato la potencia del vault
# (NEED-019 arma equipo completo con propuesta; NEED-001 hoy da cobertura
# insuficiente y dejaría el grafo casi vacío como primera impresión)
if st.session_state.current_team_data is None:
    result, source, mapped = explore(need_id="NEED-019")
    st.session_state.current_team_data = result.get("team_data")
    st.session_state.current_need = result.get("need")
    st.session_state.api_source = source
    st.session_state.mapped_status = mapped
    if result.get("need"):
        st.session_state.last_query_label = f"{result['need'].get('id', '')} · {result['need'].get('title', '')}"

# ---------- Cálculo de Métricas y KPI Ribbon ----------
team_data = st.session_state.current_team_data
metrics = calculate_metrics(team_data) if team_data else {}

if metrics:
    relevance_pct = int(metrics.get("avg_relevance", 0.0) * 100)
    proposal_tag = "✨ Propuesta Articulada" if metrics.get("has_proposal") else "📜 Antecedente Directo"

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Índice de Pertinencia</span>
                    <span class="kpi-icon">🎯</span>
                </div>
                <div class="kpi-value" style="color: #38BDF8;">{relevance_pct}%</div>
                <div class="kpi-subtext">Afinidad promedio del equipo</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Equipo Mínimo</span>
                    <span class="kpi-icon">👥</span>
                </div>
                <div class="kpi-value" style="color: #A855F7;">{metrics.get('total_nodes', 0)} nodos</div>
                <div class="kpi-subtext">{metrics.get('researchers', 0)} inv · {metrics.get('capabilities', 0)} cap · {metrics.get('subjects', 0)} asig</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Trazabilidad de Evidencia</span>
                    <span class="kpi-icon">🔍</span>
                </div>
                <div class="kpi-value" style="color: #34D399;">{metrics.get('traceability_pct', 0)}%</div>
                <div class="kpi-subtext">{metrics.get('institutional_count', 0)} entidades auditables Data V1.0</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Estado de Articulación</span>
                    <span class="kpi-icon">⚡</span>
                </div>
                <div class="kpi-value" style="font-size: 1.15rem; color: #E879F9; padding-top: 4px;">{proposal_tag}</div>
                <div class="kpi-subtext">Integración multi-disciplinaria</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Pestañas de Navegación Multidimensional ----------
tab_graph, tab_brief, tab_matrix = st.tabs([
    "🗺️ Grafo de Pertinencia & Nota",
    "📋 Ficha Ejecutiva del Equipo (Executive Brief)",
    "🔍 Matriz de Evidencia & Trazabilidad Auditable",
])

# ==================== TAB 1: GRAFO Y PANEL DE NOTAS ====================
with tab_graph:
    col_graph, col_note = st.columns([1.9, 1.1], gap="medium")

    with col_graph:
        if st.session_state.last_query_label:
            st.markdown(
                f"<div style='font-size: 0.95rem; color: #E2E8F0; font-weight: 600; margin-bottom: 8px;'>"
                f"🎯 Desafío Seleccionado: <span style='color: #C084FC;'>{st.session_state.last_query_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        if team_data and team_data.get("nodes"):
            clicked_id = render_graph(team_data)
            if clicked_id:
                st.session_state.selected_node = clicked_id
        else:
            st.info("Escribe una idea en el panel lateral o elige una necesidad para generar el grafo.")

    with col_note:
        if st.session_state.selected_node and team_data:
            node = find_node(team_data, st.session_state.selected_node)
            if node:
                render_note(node)
            else:
                render_empty_state()
        else:
            render_empty_state()

# ==================== TAB 2: FICHA EJECUTIVA DEL EQUIPO ====================
with tab_brief:
    if team_data and team_data.get("nodes"):
        nodes = team_data.get("nodes", [])
        need_node = next((n for n in nodes if n.get("type") == "NEED"), {})
        prop_node = next((n for n in nodes if n.get("type") == "PROP"), {})
        researcher_nodes = [n for n in nodes if n.get("type") == "RESEARCHER"]
        capability_nodes = [n for n in nodes if n.get("type") == "CAPABILITY"]
        subject_nodes = [n for n in nodes if n.get("type") == "SUBJECT"]
        thesis_nodes = [n for n in nodes if n.get("type") in ("THESIS", "PROJECT")]

        st.markdown(
            f"""
            <div class="brief-card">
                <div class="brief-section-title">🎯 Objetivo del Desafío Institucional</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;">
                    {need_node.get('label', 'Necesidad Institucional')}
                </div>
                <div style="color: #94A3B8; font-size: 0.92rem; line-height: 1.5;">
                    {need_node.get('frase', 'Identificación de capacidades y talento humano para la resolución del problema.')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="brief-card">
                <div class="brief-section-title">✨ Propuesta de Articulación y Equipo Ejecutor</div>
                <div style="font-size: 1.05rem; font-weight: 600; color: #E879F9; margin-bottom: 6px;">
                    {prop_node.get('label', 'Equipo Interdisciplinario Formulado')}
                </div>
                <div style="color: #CBD5E1; font-size: 0.9rem; line-height: 1.5; margin-bottom: 16px;">
                    {prop_node.get('frase', 'Equipo mínimo viable que cubre las dimensiones técnicas y curriculares requeridas.')}
                </div>

                <div class="brief-team-grid">
                    <div class="brief-member-card">
                        <div style="font-weight: 700; color: #10B981; font-size: 0.88rem; margin-bottom: 6px;">
                            👤 Investigador(es) Líder
                        </div>
                        {"".join([f"<div style='color:#F8FAFC; font-weight:600; font-size:0.95rem;'>{r.get('label')}</div><div style='color:#94A3B8; font-size:0.8rem; margin-top:2px;'>{r.get('frase', '')}</div>" for r in researcher_nodes]) or "<div style='color:#64748B;'>No asignado</div>"}
                    </div>

                    <div class="brief-member-card">
                        <div style="font-weight: 700; color: #38BDF8; font-size: 0.88rem; margin-bottom: 6px;">
                            📜 Antecedente / Tesis Base
                        </div>
                        {"".join([f"<div style='color:#F8FAFC; font-weight:600; font-size:0.92rem;'>{t.get('label')}</div><div style='color:#94A3B8; font-size:0.8rem; margin-top:2px;'>{t.get('frase', '')}</div>" for t in thesis_nodes]) or "<div style='color:#64748B;'>Propuesta innovadora sin antecedente previo</div>"}
                    </div>

                    <div class="brief-member-card">
                        <div style="font-weight: 700; color: #F59E0B; font-size: 0.88rem; margin-bottom: 6px;">
                            ⚡ Capacidad Institucional Clave
                        </div>
                        {"".join([f"<div style='color:#F8FAFC; font-weight:600; font-size:0.92rem;'>{c.get('label')}</div>" for c in capability_nodes]) or "<div style='color:#64748B;'>Por definir</div>"}
                    </div>

                    <div class="brief-member-card">
                        <div style="font-weight: 700; color: #C084FC; font-size: 0.88rem; margin-bottom: 6px;">
                            📚 Asignatura Puente (Transferencia)
                        </div>
                        {"".join([f"<div style='color:#F8FAFC; font-weight:600; font-size:0.92rem;'>{s.get('label')}</div>" for s in subject_nodes]) or "<div style='color:#64748B;'>Por definir</div>"}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Genera o selecciona una necesidad para ver la Ficha Ejecutiva del Equipo.")

# ==================== TAB 3: MATRIZ DE EVIDENCIA AUDITABLE ====================
with tab_matrix:
    if team_data and team_data.get("nodes"):
        st.markdown(
            """
            <div style="margin-bottom: 14px; color: #94A3B8; font-size: 0.9rem;">
                Trazabilidad completa de cada entidad vinculada en el equipo mínimo.
                Cada registro institucional cuenta con su origen exacto en el banco de datos oficial (Data V1.0).
            </div>
            """,
            unsafe_allow_html=True,
        )

        matrix_rows = []
        for n in team_data.get("nodes", []):
            ev = n.get("evidencia") or {}
            is_gen = n.get("generado", False) or n.get("type") == "PROP"

            matrix_rows.append({
                "ID": n.get("id"),
                "Tipo": n.get("type"),
                "Nombre / Título": n.get("label"),
                "Estatus": "✨ PROPUESTA IA" if is_gen else "🟢 INSTITUCIONAL",
                "Archivo Fuente": ev.get("archivo", "— (Generado)"),
                "ID Registro": ev.get("id", "—"),
                "Campo": ev.get("campo", "—"),
            })

        df_matrix = pd.DataFrame(matrix_rows)
        st.dataframe(
            df_matrix,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Tipo": st.column_config.TextColumn("Tipo Entidad", width="small"),
                "Nombre / Título": st.column_config.TextColumn("Entidad / Descripción", width="large"),
                "Estatus": st.column_config.TextColumn("Origen", width="medium"),
                "Archivo Fuente": st.column_config.TextColumn("Archivo CSV", width="medium"),
                "ID Registro": st.column_config.TextColumn("Registro ID", width="small"),
                "Campo": st.column_config.TextColumn("Campo", width="small"),
            },
        )
    else:
        st.info("Genera o selecciona una necesidad para auditar la matriz de evidencias.")

