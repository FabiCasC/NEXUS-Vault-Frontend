"""
needs_loader.py — combo secundario de necesidades existentes.

Carga institutional_needs.csv (columnas id + title). Si el CSV real
de Data V1.0 todavía no está en data/institutional_needs.csv, genera
un placeholder de 42 filas para que la UI no se caiga mientras llega
el dataset real.

Nota: esto ya NO es la forma principal de crear un NEED — eso ahora
lo hace la caja de idea libre en app.py, que crea el need vía API.
Este combo sirve solo para explorar necesidades que ya existen.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent.parent / "data" / "institutional_needs.csv"

ID_ALIASES = ["id", "need_id", "ID"]
TITLE_ALIASES = ["title", "name", "titulo", "descripcion", "description"]


def load_needs() -> pd.DataFrame:
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        id_col = _find_column(df, ID_ALIASES)
        title_col = _find_column(df, TITLE_ALIASES)
        if id_col and title_col:
            return df.rename(columns={id_col: "id", title_col: "title"})[["id", "title"]]
        print("[needs_loader] no se encontraron columnas id/title esperadas, usando placeholder")

    return _placeholder_needs()


def _find_column(df: pd.DataFrame, aliases: list[str]):
    for alias in aliases:
        if alias in df.columns:
            return alias
    return None


def _placeholder_needs(n: int = 42) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [f"NEED-{i:03d}" for i in range(1, n + 1)],
            "title": [f"[placeholder] Necesidad institucional {i}" for i in range(1, n + 1)],
        }
    )
