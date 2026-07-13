"""SQLite读写：用户历史提交与进步追踪，对应Docs/01-系统架构与Agent设计.md
「历史进步仪表盘」和Docs/04号文档里C负责的部分。只用标准库sqlite3，
不需要额外安装任何包。
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    essay_prompt_id INTEGER,
    quant_score REAL,
    trait_scores TEXT,
    qualitative_feedback TEXT,
    revision_plan TEXT,
    created_at TEXT NOT NULL
);
"""


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    db_path = db_path or DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    return conn


def save_submission(state: dict, db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    with conn:
        conn.execute(
            "INSERT INTO submissions (user_id, essay_prompt_id, quant_score, "
            "trait_scores, qualitative_feedback, revision_plan, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                state.get("user_id", "anonymous"),
                state.get("essay_prompt_id"),
                state.get("quant_score"),
                json.dumps(state.get("trait_scores") or {}, ensure_ascii=False),
                state.get("qualitative_feedback", ""),
                state.get("revision_plan", ""),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    conn.close()


def get_user_history(user_id: str, db_path: Optional[Path] = None) -> list[dict]:
    conn = get_connection(db_path)
    cur = conn.execute(
        "SELECT quant_score, trait_scores, created_at FROM submissions "
        "WHERE user_id = ? ORDER BY created_at ASC",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "quant_score": row[0],
            "trait_scores": json.loads(row[1]) if row[1] else {},
            "created_at": row[2],
        }
        for row in rows
    ]
