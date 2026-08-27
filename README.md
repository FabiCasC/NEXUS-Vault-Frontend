# NEXUS Vault — Frontend

Frontend en Streamlit para **Knowledge Nexus LATAM** (Hackathon Perú 2026).
Interfaz estilo Obsidian: grafo a la izquierda, panel de "nota" a la derecha.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Abre en `http://localhost:8501`.

## Cómo funciona (sin backend levantado)

El repo ya trae un fixture (`data/fixtures/sample_team.json`) para que la UI
funcione de punta a punta sin depender de la API. Prueba:

1. Escribe cualquier idea en la caja de texto y dale a **"Crear necesidad y
   explorar"** → se crea un NEED local y se ve el grafo.
2. O abre el desplegable **"O elige una necesidad que ya existe"**, elige
   `NEED-001` y dale a explorar.
3. Haz clic en cualquier nodo del grafo → se abre su nota a la derecha.

## Conectar la API real

Por defecto el frontend apunta a `http://localhost:8000`. Para apuntar a
otra URL:

**Opción A — secrets.toml** (recomendado para no tocar código):
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edita la URL dentro de ese archivo
```

**Opción B — variable de entorno:**
```bash
export NEXUS_API_URL="https://tu-api.ejemplo.com"
streamlit run app.py
```

### Contrato con el backend

```
GET {API_URL}/form-team?need_id=NEED-001
GET {API_URL}/form-team?free_text=predicción+de+deserción+estudiantil
```

Respuesta esperada (200) — mismo esquema que los fixtures, directo sin wrapper:

```json
{
  "nodes": [
    {
      "id": "NEED-042",
      "type": "NEED",
      "label": "...",
      "generado": true,
      "evidencia": null,
      "frase": "..."
    },
    {
      "id": "PROP-007",
      "type": "PROP",
      "label": "Propuesta: ...",
      "generado": true
    }
  ],
  "edges": [
    {"source": "NEED-042", "target": "PROP-007", "weight": 0.83}
  ]
}
```

Tipos de nodo soportados por el frontend: `NEED`, `THESIS`, `PROJECT`,
`RESEARCHER`, `CAPABILITY`, `SUBJECT`, `LAB`, `PROP`. `PROP` (o cualquier
nodo con `"generado": true`) se dibuja con borde punteado.

Si la API no responde (no está levantada, timeout, error 5xx), el frontend
cae automáticamente al fixture — la demo nunca se cae.

## Estructura

```
app.py                        # shell principal (layout, estado, orquestación)
components/
  graph_view.py                # pinta el grafo (streamlit-agraph), devuelve nodo clickeado
  note_panel.py                # panel de nota: tipo, INSTITUCIONAL/GENERADO, evidencia
services/
  team_api.py                  # llama a GET /form-team, con fallback a fixture
  needs_loader.py               # carga institutional_needs.csv para el combo secundario
data/
  institutional_needs.csv       # (falta) poner aquí el CSV real de Data V1.0
  fixtures/
    sample_team.json            # grafo de ejemplo (deserción estudiantil)
    NEED-001.json                # mismo ejemplo, mapeado al combo secundario
.streamlit/
  config.toml                   # tema oscuro
  secrets.toml.example          # plantilla de config de la API
```

## Flujo de uso

1. **Forma principal**: el usuario escribe una idea/problema en la sidebar
   y da clic en "Crear necesidad y explorar" → crea un NEED nuevo vía API.
2. **Forma secundaria**: despliega "O elige una necesidad que ya existe" y
   selecciona una de las que ya están cargadas.
3. El grafo se pinta a la izquierda. Los nodos `PROP` (propuesta generada,
   no existe todavía en Data V1.0) se ven con borde punteado.
4. Clic en cualquier nodo → el panel derecho muestra tipo, badge
   INSTITUCIONAL/GENERADO, evidencia (archivo/id/campo) y frase.

## Checklist de tareas (Lucía)

- [x] **LU-1** `app.py` shell — título NEXUS Vault, columna izq. grafo / der. nota
- [x] **LU-2** Combo NEED — lee `institutional_needs.csv` (id+title), placeholder de 42 si aún no está el CSV real
- [x] **LU-3** `graph_view.py` — pinta nodos/aristas, color por tipo, PROP punteado
- [x] **LU-4** Click en nodo → `note_panel.render_note` (archivo tuyo, ajustable)
- [x] **LU-5** `team_api.py` — `GET /form-team` con params, fallback a fixture si no responde
- [x] **LU-6** Caja de idea libre — forma principal de crear un NEED, nunca crashea

## Pendiente para ustedes

- Reemplazar `data/institutional_needs.csv` con el CSV real de Data V1.0 (columnas `id`, `title`).
- Confirmar con backend que `GET /form-team` devuelve exactamente el formato de arriba.
- Ajustar colores/textos de `note_panel.py` a gusto — esa parte es tuya.
