import ast

from core.config import ConfigManager


class CodeValidator:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def validate(self, code: str) -> tuple[bool, str]:
        max_size = self.config_manager.get_max_code_size()

        if not code or not code.strip():
            return False, "Code field is required"

        if len(code) > max_size:
            return False, "Code size limit exceeded"

        try:
            tree = ast.parse(code)
        except SyntaxError as error:
            return False, f"Syntax error: {error.msg}"

        forbidden = self.config_manager.get_forbidden_imports()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name in forbidden:
                        return False, f"Forbidden import: {module_name}"

            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    if module_name in forbidden:
                        return False, f"Forbidden import: {module_name}"

        return True, ""