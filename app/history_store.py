import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass(frozen=True)
class SavedAnalysis:
    id: int
    created_at: str
    sender: str
    subject: str
    url: str
    score: int
    risk_level: str
    red_flags: list[str]
    rule_hits: list[dict[str, Any]]
    ai_explanation: str
    recommended_action: str


class HistoryStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._lock = Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    url TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    red_flags_json TEXT NOT NULL,
                    rule_hits_json TEXT NOT NULL DEFAULT '[]',
                    ai_explanation TEXT NOT NULL,
                    recommended_action TEXT NOT NULL
                )
                """
            )
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(analysis_history)").fetchall()}
            if "rule_hits_json" not in columns:
                conn.execute("ALTER TABLE analysis_history ADD COLUMN rule_hits_json TEXT NOT NULL DEFAULT '[]'")

    def save_analysis(
        self,
        *,
        sender: str,
        subject: str,
        url: str,
        score: int,
        risk_level: str,
        red_flags: list[str],
        rule_hits: list[dict[str, Any]],
        ai_explanation: str,
        recommended_action: str,
    ) -> int:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO analysis_history (
                        created_at, sender, subject, url, score, risk_level,
                        red_flags_json, rule_hits_json, ai_explanation, recommended_action
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        created_at,
                        sender,
                        subject,
                        url,
                        score,
                        risk_level,
                        json.dumps(red_flags),
                        json.dumps(rule_hits),
                        ai_explanation,
                        recommended_action,
                    ),
                )
                return int(cursor.lastrowid)

    def list_recent(self, limit: int) -> list[SavedAnalysis]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, sender, subject, url, score, risk_level,
                      red_flags_json, rule_hits_json, ai_explanation, recommended_action
                FROM analysis_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._row_to_model(row) for row in rows]

    def get_by_id(self, analysis_id: int) -> SavedAnalysis | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, created_at, sender, subject, url, score, risk_level,
                      red_flags_json, rule_hits_json, ai_explanation, recommended_action
                FROM analysis_history
                WHERE id = ?
                """,
                (analysis_id,),
            ).fetchone()

        if row is None:
            return None
        return self._row_to_model(row)

    def _row_to_model(self, row: sqlite3.Row) -> SavedAnalysis:
        return SavedAnalysis(
            id=int(row["id"]),
            created_at=str(row["created_at"]),
            sender=str(row["sender"]),
            subject=str(row["subject"]),
            url=str(row["url"]),
            score=int(row["score"]),
            risk_level=str(row["risk_level"]),
            red_flags=list(json.loads(row["red_flags_json"])),
            rule_hits=list(json.loads(row["rule_hits_json"])),
            ai_explanation=str(row["ai_explanation"]),
            recommended_action=str(row["recommended_action"]),
        )


def model_to_dict(item: SavedAnalysis) -> dict[str, Any]:
    return {
        "id": item.id,
        "created_at": item.created_at,
        "sender": item.sender,
        "subject": item.subject,
        "url": item.url,
        "score": item.score,
        "risk_level": item.risk_level,
        "red_flags": item.red_flags,
        "rule_hits": item.rule_hits,
        "ai_explanation": item.ai_explanation,
        "recommended_action": item.recommended_action,
    }
