import os
import subprocess
import sys
import time

from models.result import ExecutionResult


class ExecutionService:
    def run(
        self,
        code: str,
        workspace: str,
        timeout: int,
        output_limit: int
    ) -> ExecutionResult:
        script_path = os.path.join(workspace, "script.py")

        with open(script_path, "w", encoding="utf-8") as file:
            file.write(code)

        start_time = time.time()

        try:
            process = subprocess.run(
                [sys.executable, "script.py"],
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = round(time.time() - start_time, 4)

            stdout_full = process.stdout or ""
            stderr_full = process.stderr or ""

            output_truncated = (
                len(stdout_full) > output_limit or
                len(stderr_full) > output_limit
            )

            stdout = stdout_full[:output_limit]
            stderr = stderr_full[:output_limit]

            status = "ok" if process.returncode == 0 else "error"

            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                output_truncated=output_truncated
            )

        except subprocess.TimeoutExpired:
            execution_time = round(time.time() - start_time, 4)

            return ExecutionResult(
                status="timeout",
                stdout="",
                stderr="Execution timeout exceeded",
                execution_time=execution_time,
                output_truncated=False
            )