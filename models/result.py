from dataclasses import dataclass


@dataclass
class ExecutionResult:
    status: str
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    output_truncated: bool = False

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_time": self.execution_time,
            "output_truncated": self.output_truncated
        }