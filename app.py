from flask import Flask, request, jsonify

from api.handler import APIHandler
from core.auth import AuthManager
from core.code_validator import CodeValidator
from core.config import ConfigManager
from core.executor import ExecutionService
from core.logger import AuditLog
from core.sandbox import SandboxService
from models.request import ExecutionRequest

app = Flask(__name__)

config = ConfigManager("data/config.json")
logger = AuditLog("data/logs.jsonl")

api_handler = APIHandler(
    auth_manager=AuthManager(config),
    config_manager=config,
    sandbox_service=SandboxService(config),
    executor=ExecutionService(),
    logger=logger,
    code_validator=CodeValidator(config)
)


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "MCP server is running",
        "endpoints": [
            "GET /health",
            "POST /execute",
            "GET /admin/logs",
            "GET /admin/config"
        ]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "status": "bad_request",
            "stdout": "",
            "stderr": "Invalid JSON",
            "execution_time": 0.0,
            "output_truncated": False
        }), 400

    exec_request = ExecutionRequest(
        code=data.get("code", ""),
        token=data.get("token", ""),
        client_id=data.get("client_id", "unknown")
    )

    result = api_handler.handle_execute(exec_request)

    status_code = 200
    if result.status == "bad_request":
        status_code = 400
    elif result.status == "unauthorized":
        status_code = 401
    elif result.status == "forbidden":
        status_code = 403

    return jsonify(result.to_dict()), status_code


@app.route("/admin/logs", methods=["GET"])
def get_logs():
    token = request.headers.get("X-Admin-Token", "")
    result, status_code = api_handler.handle_get_logs(token)
    return jsonify(result), status_code


@app.route("/admin/config", methods=["GET"])
def get_config():
    token = request.headers.get("X-Admin-Token", "")

    if not api_handler.auth_manager.verify_admin(token):
        return jsonify({
            "status": "unauthorized",
            "error": "Invalid admin token"
        }), 401

    return jsonify({
        "status": "ok",
        "config": api_handler.config_manager.load()
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)