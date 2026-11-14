"""SQLite persistence: analyses, reference collection, match candidates, audit events."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .config import get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    filename TEXT,
    size_bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    image_format TEXT,
    width INTEGER,
    height INTEGER,
    phash TEXT,
    warning_count INTEGER NOT NULL DEFAULT 0,
    metrics_json TEXT NOT NULL,
    findings_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS collection_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    label TEXT NOT NULL,
    filename TEXT,
    sha256 TEXT NOT NULL,
    phash TEXT NOT NULL,
    width INTEGER,
    height INTEGER
);
CREATE TABLE IF NOT EXISTS match_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    analysis_id INTEGER NOT NULL REFERENCES analyses(id),
    collection_id INTEGER NOT NULL REFERENCES collection_images(id),
    exact_match INTEGER NOT NULL,
    hamming_distance INTEGER NOT NULL,
    similarity REAL NOT NULL,
    disposition TEXT NOT NULL DEFAULT 'pending',
    reviewer TEXT,
    note TEXT,
    reviewed_at TEXT
);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    detail_json TEXT
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_conn():
    path = Path(get_settings()["db_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def audit(conn, action: str, entity: str, entity_id=None, detail=None, actor: str = "system") -> None:
    conn.execute(
        "INSERT INTO audit_events (created_at, actor, action, entity, entity_id, detail_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (now(), actor, action, entity, entity_id, json.dumps(detail) if detail else None),
    )
