"""OCF Gateway HTTP server — receives tasks from Mission Control."""

from __future__ import annotations

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict

from gateway.executor import execute_task


AGENTS_DIR = Path(__file__).parent.parent / "agents"


class GatewayHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "gateway": "ocf"})
        elif self.path == "/agents":
            self._json(200, {"agents": _list_agents()})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path == "/execute":
            self._handle_execute()
        else:
            self._json(404, {"error": "not found"})

    def _handle_execute(self) -> None:
        body = self._read_body()
        agent_name = body.get("agent")
        task = body.get("task", {})

        if not agent_name:
            self._json(400, {"error": "missing 'agent' field"})
            return

        agent_dir = AGENTS_DIR / agent_name
        if not agent_dir.exists():
            self._json(404, {"error": f"agent not found: {agent_name}"})
            return

        result = execute_task(agent_dir, task)
        status = 200 if result.get("error") is None else 500
        self._json(status, result)

    def _read_body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        return json.loads(raw) if raw else {}

    def _json(self, status: int, data: Dict) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def _list_agents() -> list:
    agents = []
    for d in sorted(AGENTS_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            config_path = d / "agent.yaml"
            if config_path.exists():
                import yaml
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}
                agents.append({
                    "name": cfg.get("name", d.name),
                    "type": cfg.get("type", "definition"),
                    "description": cfg.get("description", ""),
                })
    return agents


def run_gateway(port: int = 9400) -> None:
    server = HTTPServer(("0.0.0.0", port), GatewayHandler)
    print(f"OCF Gateway listening on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()