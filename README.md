# NEXUS Vault — frontend

Repo exclusivo de frontend (Streamlit) para NEXUS Vault. No calcula el
equipo mínimo ni corre ningún algoritmo de set cover / team formation:
solo pinta lo que le llega en un JSON y navega como Obsidian
(nodos, clic, nota, backlinks).

## Correr localmente

El backend vive en **otro repo/proceso** (`NEXUS-Vault-API`). Hay que
levantar los dos:

```bash
# 1) en el repo NEXUS-Vault-API
pip install -r requirements.txt
uvicorn backend.api:app --reload --port 8000

# 2) en este repo (otra terminal)
pip install -r requirements.txt
streamlit run app.py
```

Abre en el navegador, escribe una idea libre o elige una de las 42 NEEDs
reales del combo (`data/institutional_needs.csv`, ya no son de ejemplo:
salen del dataset oficial). Si la API no responde, la UI cae sola a
`fixtures/` — nunca se cae, y arriba a la izquierda ves un badge 🟢/🔴 que
dice si está hablando con la API real.

Por defecto apunta a `http://localhost:8000`. Para apuntar a otro lado
(por ejemplo si Fabiana la despliega en Railway):

```bash
export NEXUS_API_URL="https://tu-api-en-railway.up.railway.app"
```

## Estructura

```
app.py                  # shell principal: idea libre, combo, llamada HTTP a la API
graph_view.py           # pinta el grafo (streamlit-agraph), colorea por tipo, PROP punteado
note_panel.py           # render_note(): panel de la nota al hacer clic en un nodo
data/institutional_needs.csv   # las 42 NEEDs reales del dataset (id + title)
fixtures/NEED-001.json         # respaldo offline: salida REAL de la API para NEED-001
fixtures/NEED-019.json         # respaldo offline: caso con propuesta GENERADA completa
fixtures/default.json          # grafo mínimo genérico si no hay fixture para el id pedido
```

## Contrato con la API (`NEXUS-Vault-API`)

Este repo le pega por HTTP, no por import (son repos/procesos separados):

```
GET {NEXUS_API_URL}/form-team?need_id=NEED-001
GET {NEXUS_API_URL}/form-team?free_text=texto libre del evaluador
GET {NEXUS_API_URL}/health
```

Respuesta esperada (documentada también en `backend/graph_adapter.py` del
repo de la API):

```json
{
  "root": "NEED-001",
  "need_id": "NEED-001",
  "nodes": [
    {
      "id": "RES-014",
      "type": "NEED|THESIS|PROJECT|RESEARCHER|CAPABILITY|SUBJECT|PROP",
      "label": "Texto corto para el nodo",
      "phrase": "Frase/evidencia citada del CSV",
      "source": {"file": "researchers.csv", "id": "RES-014", "field": "title"},
      "skills": ["skill_a", "skill_b"],
      "generated": false
    }
  ],
  "edges": [
    {"source": "NEED-001", "target": "RES-014", "label": "cubierta por", "generated": false}
  ]
}
```

Si la API no responde (o devuelve error), `app.py` cae automáticamente a
`fixtures/<need_id>.json`, o a `fixtures/default.json` si no hay fixture
para ese id. Así la UI vive sin depender de que la API esté arriba en
ese instante.
