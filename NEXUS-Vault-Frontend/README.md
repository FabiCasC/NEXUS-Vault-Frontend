# NEXUS Vault — frontend

Repo exclusivo de frontend (Streamlit) para NEXUS Vault. No calcula el
equipo mínimo ni corre ningún algoritmo de set cover / team formation:
solo pinta lo que le llega en un JSON y navega como Obsidian
(nodos, clic, nota, backlinks).

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre en el navegador, elige una NEED en el combo (hay 42 de ejemplo en
`data/institutional_needs.csv`) o escribe una idea libre. Si no existe
todavía `form_team.py` (el backend de Kevin), la UI usa automáticamente
los datos de `fixtures/` — nunca se cae.

## Estructura

```
app.py              # shell principal: layout, combo, caja de idea libre
graph_view.py        # pinta el grafo (streamlit-agraph), colorea por tipo, PROP punteado
note_panel.py         # render_note(): panel de la nota al hacer clic en un nodo
data/institutional_needs.csv   # 42 NEEDs de ejemplo (id + title)
fixtures/NEED-001.json          # grafo de ejemplo completo (se ve sin backend)
fixtures/default.json           # grafo mínimo genérico de respaldo
```

## Contrato esperado de `form_team.py` (aún no incluido, es de Kevin)

Este repo intenta importar una función con esta firma:

```python
def form_team(need_id: str | None = None, free_text: str | None = None) -> dict:
    """
    Devuelve un dict con esta forma exacta (mismo esquema que las fixtures):

    {
        "root": "NEED-001",
        "nodes": [
            {
                "id": "RES-014",
                "type": "NEED|THESIS|PROJECT|RESEARCHER|CAPABILITY|SUBJECT|LAB|PROP",
                "label": "Texto corto para el nodo",
                "phrase": "Frase textual tomada del CSV, como evidencia",
                "source": {"file": "researchers.csv", "id": "RES-014", "field": "expertise"},
                "skills": ["skill_a", "skill_b"],
                "generated": False  # True solo para nodos tipo PROP
            },
            ...
        ],
        "edges": [
            {"source": "NEED-001", "target": "RES-014", "label": "cubierta por", "generated": False},
            ...
        ]
    }
    """
```

Mientras `form_team.py` no exista (o si lanza una excepción), `app.py`
cae automáticamente a `fixtures/<need_id>.json`, o a `fixtures/default.json`
si no hay fixture para ese id. Así la UI vive sin depender del backend.

## Estado de tareas (LU-1 a LU-6)

- **LU-1** `app.py` — título NEXUS Vault, columnas grafo/nota, corre con `streamlit run`.
- **LU-2** Combo NEED — lee `institutional_needs.csv` (id + title), 42 opciones.
- **LU-3** `graph_view.py` — pinta nodos/aristas del JSON (fixture o form_team), color por tipo, PROP punteado. `NEED-001` se ve con `fixtures/NEED-001.json`.
- **LU-4** Clic en nodo — llama a `note_panel.render_note`, muestra la frase y la fuente en pantalla.
- **LU-5** `try/except` — `try form_team except fixture`. Sin el archivo de Kevin, la UI vive igual.
- **LU-6** Caja de idea libre — input de texto; si no hay mapeo real, muestra sugerencia de usar el combo y nunca truena.
