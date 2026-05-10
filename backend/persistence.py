import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path


class PersistenceStore:
    DEFAULT_LIMIT = 50

    def __init__(self, db_path=None):
        self.db_path = Path(db_path or self.default_db_path())
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @staticmethod
    def default_db_path():
        env_path = os.environ.get("CALCULATOR_SUITE_DB")
        if env_path:
            return env_path
        return Path.home() / ".calculator_suite" / "calculator_suite.sqlite3"

    def connect(self):
        return sqlite3.connect(self.db_path)

    def initialize(self):
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    expression TEXT NOT NULL,
                    result TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_functions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expression TEXT NOT NULL,
                    visible INTEGER NOT NULL DEFAULT 1,
                    color TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

    def add_history(self, category, expression, result, metadata=None):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO history(category, expression, result, metadata, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    category,
                    str(expression),
                    str(result),
                    json.dumps(metadata or {}, ensure_ascii=False),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

    def list_history(self, category=None, limit=DEFAULT_LIMIT):
        query = "SELECT id, category, expression, result, metadata, created_at FROM history"
        params = []
        if category:
            query += " WHERE category = ?"
            params.append(category)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "id": row[0],
                "category": row[1],
                "expression": row[2],
                "result": row[3],
                "metadata": json.loads(row[4] or "{}"),
                "created_at": row[5],
            }
            for row in rows
        ]

    def clear_history(self, category=None):
        with self.connect() as conn:
            if category:
                conn.execute("DELETE FROM history WHERE category = ?", (category,))
            else:
                conn.execute("DELETE FROM history")

    def get_setting(self, key, default=None):
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if not row:
            return default
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return row[0]

    def set_setting(self, key, value):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO settings(key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, json.dumps(value, ensure_ascii=False)),
            )

    def get_settings(self, defaults):
        return {key: self.get_setting(key, default) for key, default in defaults.items()}

    def set_settings(self, values):
        for key, value in values.items():
            self.set_setting(key, value)

    def save_graph_functions(self, functions):
        with self.connect() as conn:
            conn.execute("DELETE FROM graph_functions")
            conn.executemany(
                """
                INSERT INTO graph_functions(expression, visible, color, created_at)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        item.get("expression", ""),
                        1 if item.get("visible", True) else 0,
                        item.get("color"),
                        datetime.now().isoformat(timespec="seconds"),
                    )
                    for item in functions
                ],
            )

    def list_graph_functions(self):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT expression, visible, color FROM graph_functions ORDER BY id ASC"
            ).fetchall()
        return [
            {"expression": row[0], "visible": bool(row[1]), "color": row[2]}
            for row in rows
        ]


_default_store = None


def get_store():
    global _default_store
    if _default_store is None:
        _default_store = PersistenceStore()
    return _default_store
