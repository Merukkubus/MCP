import sqlite3
from datetime import datetime


class Database:
    def __init__(self, path: str = "data/server.db"):
        self.path = path
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.path)

    def init_db(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_requests (
                    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    code TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(client_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    stdout TEXT,
                    stderr TEXT,
                    execution_time REAL,
                    output_truncated INTEGER,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES execution_requests(request_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT,
                    event TEXT NOT NULL,
                    status TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()

    def ensure_client(self, client_id: str):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO clients (client_id, created_at)
                VALUES (?, ?)
                """,
                (client_id, datetime.now().isoformat(timespec="seconds"))
            )
            conn.commit()

    def create_request(self, client_id: str, code: str, status: str = "received") -> int:
        self.ensure_client(client_id)

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO execution_requests (client_id, code, status, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    client_id,
                    code,
                    status,
                    datetime.now().isoformat(timespec="seconds")
                )
            )
            conn.commit()
            return cursor.lastrowid

    def update_request_status(self, request_id: int, status: str):
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE execution_requests
                SET status = ?
                WHERE request_id = ?
                """,
                (status, request_id)
            )
            conn.commit()

    def save_result(self, request_id: int, result):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO execution_results (
                    request_id,
                    status,
                    stdout,
                    stderr,
                    execution_time,
                    output_truncated,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    result.status,
                    result.stdout,
                    result.stderr,
                    result.execution_time,
                    int(result.output_truncated),
                    datetime.now().isoformat(timespec="seconds")
                )
            )
            conn.commit()

    def save_log(self, client_id: str, event: str, status: str = ""):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO log_entries (client_id, event, status, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    client_id,
                    event,
                    status,
                    datetime.now().isoformat(timespec="seconds")
                )
            )
            conn.commit()

    def get_logs(self, limit: int = 50) -> list[dict]:
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT log_id, client_id, event, status, created_at
                FROM log_entries
                ORDER BY log_id DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()

            return [dict(row) for row in rows]

    def get_requests(self, limit: int = 50) -> list[dict]:
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT request_id, client_id, status, created_at
                FROM execution_requests
                ORDER BY request_id DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()

            return [dict(row) for row in rows]