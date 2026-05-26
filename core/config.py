import json


class ConfigManager:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict:
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self, config: dict) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)

    def update(self, updates: dict) -> dict:
        config = self.load()

        allowed_fields = {
            "timeout",
            "output_limit",
            "max_code_size"
        }

        for key, value in updates.items():
            if key in allowed_fields:
                config[key] = value

        self.save(config)
        return config

    def get_tokens(self) -> list[str]:
        return self.load().get("tokens", [])

    def get_admin_tokens(self) -> list[str]:
        return self.load().get("admin_tokens", [])

    def get_timeout(self) -> int:
        return int(self.load().get("timeout", 3))

    def get_output_limit(self) -> int:
        return int(self.load().get("output_limit", 4000))

    def get_max_code_size(self) -> int:
        return int(self.load().get("max_code_size", 10000))

    def get_sandbox_root(self) -> str:
        return self.load().get("sandbox_root", "sandbox")

    def get_forbidden_imports(self) -> set[str]:
        return set(self.load().get("forbidden_imports", []))