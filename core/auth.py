from core.config import ConfigManager


class AuthManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def verify(self, token: str) -> bool:
        return token in self.config_manager.get_tokens()

    def verify_admin(self, token: str) -> bool:
        return token in self.config_manager.get_admin_tokens()