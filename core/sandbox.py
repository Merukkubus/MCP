import os
import re
import shutil
import uuid

from core.config import ConfigManager


class SandboxService:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def _safe_client_id(self, client_id: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]", "_", client_id)

    def prepare_workspace(self, client_id: str) -> str:
        root = self.config_manager.get_sandbox_root()
        os.makedirs(root, exist_ok=True)

        safe_client = self._safe_client_id(client_id)
        workspace = os.path.abspath(
            os.path.join(root, f"{safe_client}_{uuid.uuid4().hex}")
        )

        os.makedirs(workspace, exist_ok=True)
        return workspace

    def cleanup_workspace(self, workspace: str) -> None:
        if workspace and os.path.exists(workspace):
            shutil.rmtree(workspace, ignore_errors=True)