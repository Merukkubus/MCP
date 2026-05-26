import json
from datetime import datetime


class AuditLog:
    def __init__(self, path: str):
        self.path = path

    def write(self, event: str, client_id: str = "unknown", status: str = "") -> None:
        record = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "client_id": client_id,
            "event": event,
            "status": status
        }

        with open(self.path, "a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_last(self, limit: int = 50) -> list[dict]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError:
            return []

        records = []
        for line in lines[-limit:]:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return records