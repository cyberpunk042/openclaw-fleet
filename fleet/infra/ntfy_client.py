"""Fleet ntfy client — push notifications to human via ntfy.sh instance.

Sends classified notifications to ntfy topics with priority routing.
Topics: fleet-progress (info), fleet-review (important), fleet-alert (urgent).
"""

from __future__ import annotations

import os
from typing import Optional

import httpx


# Priority mapping (ntfy uses 1-5, where 5 is max/urgent)
PRIORITY_MAP = {
    "info": 3,        # Default — shows in notification list
    "important": 4,   # High — prominent notification
    "urgent": 5,      # Max — persistent, makes sound
    "low": 2,         # Low — quiet
    "min": 1,         # Min — no notification, just in list
}

# Topic routing by priority
TOPIC_MAP = {
    "info": "fleet-progress",
    "important": "fleet-review",
    "urgent": "fleet-alert",
    "low": "fleet-progress",
    "min": "fleet-progress",
}


class NtfyClient:
    """Publishes notifications to a self-hosted ntfy instance."""

    def __init__(
        self,
        base_url: str = "",
        default_topic: str = "fleet-progress",
    ):
        self._base_url = (
            base_url.rstrip("/")
            or os.environ.get("NTFY_URL", "http://192.168.40.11:10222")
        )
        self._default_topic = default_topic
        self._client = httpx.AsyncClient(timeout=10.0)

    async def publish(
        self,
        title: str,
        message: str,
        *,
        priority: str = "info",
        topic: str = "",
        tags: Optional[list[str]] = None,
        click_url: str = "",
    ) -> bool:
        """Publish a notification to ntfy.

        Args:
            title: Notification title.
            message: Body text.
            priority: "info", "important", "urgent", "low", "min".
            topic: ntfy topic (auto-routed by priority if not specified).
            tags: ntfy tags (support emoji shortcodes).
            click_url: URL to open when notification is clicked.

        Returns:
            True if published successfully.
        """
        resolved_topic = topic or TOPIC_MAP.get(priority, self._default_topic)
        ntfy_priority = PRIORITY_MAP.get(priority, 3)

        headers: dict[str, str] = {
            "Title": title[:120],
            "Priority": str(ntfy_priority),
        }

        if tags:
            headers["Tags"] = ",".join(tags)

        if click_url:
            headers["Click"] = click_url

        try:
            resp = await self._client.post(
                f"{self._base_url}/{resolved_topic}",
                content=message,
                headers=headers,
            )
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()