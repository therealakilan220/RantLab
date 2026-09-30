"""SQLite storage (Member 2). No name/email columns on purpose: reports are anonymous."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS cards (
    id          TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    input_type  TEXT NOT NULL,
    transcript  TEXT NOT NULL,
    problem     TEXT NOT NULL,
    pattern     TEXT NOT NULL,
    affected    TEXT NOT NULL,
    fixes_json  TEXT NOT NULL,
    cluster_id  TEXT,
    embedding_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cards_created_at ON cards(created_at);
CREATE INDEX IF NOT EXISTS idx_cards_cluster_id ON cards(cluster_id);
"""


@contextmanager
def _conn():
    con = sqlite3.connect(config.DB_PATH, timeout=30.0)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with _conn() as con:
        con.executescript(SCHEMA)


def _row_to_card(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "input_type": row["input_type"],
        "transcript": row["transcript"],
        "problem": row["problem"],
        "pattern": row["pattern"],
        "affected": row["affected"],
        "fixes": json.loads(row["fixes_json"]),
        "cluster_id": row["cluster_id"],
    }


def save_card(card: dict, embedding: list[float]) -> None:
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO cards VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                card["id"], card["created_at"], card["input_type"], card["transcript"],
                card["problem"], card["pattern"], card["affected"],
                json.dumps(card["fixes"]), card.get("cluster_id"), json.dumps(embedding),
            ),
        )


def get_card(card_id: str) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    return _row_to_card(row) if row else None


def all_cards_with_embeddings() -> list[tuple[dict, list[float]]]:
    with _conn() as con:
        rows = con.execute("SELECT * FROM cards ORDER BY created_at").fetchall()
    return [(_row_to_card(r), json.loads(r["embedding_json"])) for r in rows]


def set_cluster_ids(mapping: dict[str, str]) -> None:
    with _conn() as con:
        con.executemany("UPDATE cards SET cluster_id = ? WHERE id = ?", [(k, c) for c, k in mapping.items()])


def count_cards() -> int:
    with _conn() as con:
        row = con.execute("SELECT COUNT(*) AS cnt FROM cards").fetchone()
    return int(row["cnt"]) if row else 0


def get_cards_by_cluster(cluster_id: str) -> list[dict]:
    with _conn() as con:
        rows = con.execute("SELECT * FROM cards WHERE cluster_id = ? ORDER BY created_at DESC", (cluster_id,)).fetchall()
    return [_row_to_card(r) for r in rows]
