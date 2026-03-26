"""OCF Gateway WebSocket server — speaks the OpenClaw gateway protocol.

Mission Control connects to gateways via WebSocket using JSON-RPC style messages.

Protocol:
1. Client connects
2. Gateway sends connect.challenge event (optional)
3. Client sends connect request
4. Gateway responds with server metadata (including version)
5. Client calls methods: health, status, agents.list, config.get, etc.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

import yaml

logger = logging.getLogger("ocf.gateway")

AGENTS_DIR = Path(__file__).parent.parent / "agents"
GATEWAY_VERSION = "2026.3.26"


class GatewayProtocol:
    """Handles the OpenClaw gateway WebSocket protocol."""

    def __init__(self) -> None:
        self.agents = self._load_agents()

    async def handle_connection(self, websocket) -> None:
        """Handle a single WebSocket connection."""
        print(f"[gateway] New connection from {websocket.remote_address}", flush=True)

        # Step 1: Send connect challenge
        challenge = {
            "type": "event",
            "event": "connect.challenge",
            "payload": {"nonce": str(uuid4())},
        }
        await websocket.send(json.dumps(challenge))

        # Step 2-N: Handle messages
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type")
                msg_id = data.get("id")
                method = data.get("method", "")

                print(f"[gateway] Received: type={msg_type} method={method} id={msg_id}", flush=True)
                if msg_type == "req":
                    result = await self._handle_request(method, data.get("params", {}))
                    response = {
                        "type": "res",
                        "id": msg_id,
                        "payload": result,
                    }
                    await websocket.send(json.dumps(response))
        except Exception as e:
            logger.debug(f"Connection closed: {e}")

    async def _handle_request(self, method: str, params: Dict[str, Any]) -> Any:
        """Route a request to the appropriate handler."""
        handlers = {
            "connect": self._handle_connect,
            "health": self._handle_health,
            "status": self._handle_status,
            "agents.list": self._handle_agents_list,
            "config.get": self._handle_config_get,
            "models.list": self._handle_models_list,
            "skills.status": self._handle_skills_status,
        }

        handler = handlers.get(method)
        if handler:
            return await handler(params)

        # Unknown method — return empty success
        logger.debug(f"Unhandled method: {method}")
        return {"ok": True}

    async def _handle_connect(self, params: Dict) -> Dict:
        """Respond to the connect handshake."""
        return {
            "server": {
                "version": GATEWAY_VERSION,
                "name": "OCF Gateway",
                "capabilities": ["agents", "health"],
            },
            "session": {
                "id": str(uuid4()),
            },
        }

    async def _handle_health(self, params: Dict) -> Dict:
        return {"ok": True, "gateway": "ocf", "version": GATEWAY_VERSION}

    async def _handle_status(self, params: Dict) -> Dict:
        return {
            "gateway": "ocf",
            "version": GATEWAY_VERSION,
            "agents": len(self.agents),
            "ok": True,
        }

    async def _handle_agents_list(self, params: Dict) -> Dict:
        return {"agents": self.agents}

    async def _handle_config_get(self, params: Dict) -> Dict:
        return {
            "config": {
                "meta": {
                    "lastTouchedVersion": GATEWAY_VERSION,
                },
            },
        }

    async def _handle_models_list(self, params: Dict) -> Dict:
        return {"models": []}

    async def _handle_skills_status(self, params: Dict) -> Dict:
        return {"skills": [], "installed": []}

    def _load_agents(self) -> list:
        agents = []
        if not AGENTS_DIR.exists():
            return agents
        for d in sorted(AGENTS_DIR.iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                config_path = d / "agent.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        cfg = yaml.safe_load(f) or {}
                    agents.append({
                        "name": cfg.get("name", d.name),
                        "type": cfg.get("type", "definition"),
                        "description": cfg.get("description", ""),
                        "status": "active",
                    })
        return agents


async def run_ws_gateway(host: str = "0.0.0.0", port: int = 9400) -> None:
    """Start the WebSocket gateway server."""
    try:
        import websockets
    except ImportError:
        print("Error: 'websockets' package required. pip install websockets")
        return

    protocol = GatewayProtocol()
    print(f"OCF Gateway (WebSocket) listening on ws://{host}:{port}")
    print(f"Version: {GATEWAY_VERSION}")
    print(f"Agents: {len(protocol.agents)}")

    async with websockets.serve(protocol.handle_connection, host, port):
        await asyncio.Future()  # run forever