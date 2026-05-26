from dataclasses import dataclass


@dataclass
class ExecutionRequest:
    code: str
    token: str
    client_id: str = "unknown"