import json
from datetime import datetime

from core.database import Database


class AuditLog:
    def __init__(self, path: str, database: Database):
        self.path = path
        self.database = database

    def write(self, event: str, client_id: str = "unknown", status: str = "") -> None:
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "client_id": client_id,
            "event": event,
            "status": status
        }

        with open(self.path, "a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

        self.database.save_log(client_id, event, status)

    def read_last(self, limit: int = 50) -> list[dict]:
        return self.database.get_logs(limit)