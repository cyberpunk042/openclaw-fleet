"""Fleet IRC notification client.

Implements core.interfaces.NotificationClient.
Sends messages to IRC channels via the OpenClaw gateway send RPC.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from typing import Optional

import websockets

from fleet.core.interfaces import NotificationClient
from fleet.infra.config_loader import resolve_vendor_client_id


class IRCClient(NotificationClient):
    """Send messages to IRC via OpenClaw gateway WebSocket RPC."""

    def __init__(
        self,
        gateway_url: str = f"ws://localhost:{os.environ.get('OCF_GATEWAY_PORT', '9400')}",
        gateway_token: str = "",
        account_id: str = "fleet",
    ):
        self._gateway_url = gateway_url
        self._gateway_token = gateway_token
        self._account_id = account_id

    async def notify(self, channel: str, message: str) -> bool:
        """Send a message to an IRC channel.

        Args:
            channel: IRC channel name (e.g., "#fleet", "#alerts", "#reviews")
            message: Message text to send.

        Returns:
            True if message was sent successfully.
        """
        try:
            async with websockets.connect(
                self._gateway_url,
                origin=self._gateway_url.replace("ws://", "http://"),
            ) as ws:
                # Wait for challenge
                await asyncio.wait_for(ws.recv(), timeout=5)

                # Connect
                connect_id = str(uuid.uuid4())
                await ws.send(json.dumps({
                    "type": "req",
                    "id": connect_id,
                    "method": "connect",
                    "params": {
                        "minProtocol": 3,
                        "maxProtocol": 3,
                        "role": "operator",
                        "scopes": ["operator.read", "operator.admin"],
                        "client": {
                            "id": resolve_vendor_client_id(),
                            "version": "1.0.0",
                            "platform": "python",
                            "mode": "ui",
                        },
                        "auth": {"token": self._gateway_token},
                    },
                }))

                raw = await asyncio.wait_for(ws.recv(), timeout=5)
                if not json.loads(raw).get("ok"):
                    return False

                # Send message
                req_id = str(uuid.uuid4())
                await ws.send(json.dumps({
                    "type": "req",
                    "id": req_id,
                    "method": "send",
                    "params": {
                        "channel": "irc",
                        "to": channel,
                        "message": message,
                        "accountId": self._account_id,
                        "idempotencyKey": str(uuid.uuid4()),
                    },
                }))

                while True:
                    data = json.loads(
                        await asyncio.wait_for(ws.recv(), timeout=10)
                    )
                    if data.get("id") == req_id:
                        return data.get("ok", False)

        except Exception:
            return False

    async def notify_fleet(self, message: str) -> bool:
        """Shorthand: send to #fleet."""
        return await self.notify("#fleet", message)

    async def notify_alerts(self, message: str) -> bool:
        """Shorthand: send to #alerts."""
        return await self.notify("#alerts", message)

    async def notify_reviews(self, message: str) -> bool:
        """Shorthand: send to #reviews."""
        return await self.notify("#reviews", message)

    async def notify_event(
        self,
        *,
        agent: str,
        event: str,
        title: str = "",
        url: str = "",
        channel: str = "#fleet",
    ) -> bool:
        """Send a structured fleet event message.

        Produces: [agent] EVENT: title — url
        """
        msg = f"[{agent}] {event}"
        if title:
            msg = f"{msg}: {title}"
        if url:
            msg = f"{msg} — {url}"
        return await self.notify(channel, msg)