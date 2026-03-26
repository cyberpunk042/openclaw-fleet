"""Entry point for python -m gateway."""

import asyncio
import os

from gateway.ws_server import run_ws_gateway

port = int(os.environ.get("OCF_GATEWAY_PORT", "9400"))
asyncio.run(run_ws_gateway(port=port))