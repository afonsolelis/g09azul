import json
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "analises.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analises (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                score_final REAL NOT NULL,
                nivel TEXT NOT NULL,
                parecer TEXT NOT NULL,
                dados TEXT NOT NULL
            )
            """
        )
        conn.commit()


def salvar_analise(resultado: dict) -> None:
    init_db()
    dados = json.dumps(resultado, ensure_ascii=False)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO analises
            (id, timestamp, score_final, nivel, parecer, dados)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resultado["id"],
                resultado["timestamp"],
                resultado["score_final"],
                resultado["nivel"],
                resultado["parecer"],
                dados,
            ),
        )
        conn.commit()


def listar_analises() -> list[dict]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT dados FROM analises ORDER BY timestamp DESC"
        ).fetchall()
    return [json.loads(r["dados"]) for r in rows]


def obter_analise(analise_id: str) -> Optional[dict]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT dados FROM analises WHERE id = ?", (analise_id,)
        ).fetchone()
    return json.loads(row["dados"]) if row else None


def limpar_analises() -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM analises")
        conn.commit()
