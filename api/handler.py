from core.auth import AuthManager
from core.code_validator import CodeValidator
from core.config import ConfigManager
from core.executor import ExecutionService
from core.logger import AuditLog
from core.sandbox import SandboxService
from models.request import ExecutionRequest
from models.result import ExecutionResult


class APIHandler:
    def __init__(
        self,
        auth_manager: AuthManager,
        config_manager: ConfigManager,
        sandbox_service: SandboxService,
        executor: ExecutionService,
        logger: AuditLog,
        code_validator: CodeValidator
    ):
        self.auth_manager = auth_manager
        self.config_manager = config_manager
        self.sandbox_service = sandbox_service
        self.executor = executor
        self.logger = logger
        self.code_validator = code_validator

    def handle_execute(self, request: ExecutionRequest) -> ExecutionResult:
        self.logger.write("execute_request_received", request.client_id)

        if not self.auth_manager.verify(request.token):
            self.logger.write("auth_failed", request.client_id, "unauthorized")
            return ExecutionResult(
                status="unauthorized",
                stderr="Invalid token"
            )

        is_valid, error_message = self.code_validator.validate(request.code)
        if not is_valid:
            status = "forbidden" if "Forbidden import" in error_message else "bad_request"
            self.logger.write("code_validation_failed", request.client_id, status)
            return ExecutionResult(
                status=status,
                stderr=error_message
            )

        workspace = self.sandbox_service.prepare_workspace(request.client_id)

        try:
            result = self.executor.run(
                code=request.code,
                workspace=workspace,
                timeout=self.config_manager.get_timeout(),
                output_limit=self.config_manager.get_output_limit()
            )

            self.logger.write("execute_finished", request.client_id, result.status)
            return result

        finally:
            self.sandbox_service.cleanup_workspace(workspace)

    def handle_get_logs(self, admin_token: str) -> tuple[dict, int]:
        if not self.auth_manager.verify_admin(admin_token):
            return {"status": "unauthorized", "error": "Invalid admin token"}, 401

        logs = self.logger.read_last(limit=50)
        return {"status": "ok", "logs": logs}, 200