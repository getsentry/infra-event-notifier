import click
import time
import httpx
import os

from typing import Any, Dict


DD_API_BASE = "https://api.datadoghq.com"

DATADOG_API_KEY = os.getenv("DATADOG_API_KEY") or os.getenv("DD_API_KEY")
assert DATADOG_API_KEY, "Please set either DATADOG_API_KEY or DD_API_KEY env var."


def send_event_payload_to_datadog(payload: Dict[str, Any]) -> None:
    # API docs: https://docs.datadoghq.com/api/latest/events/#post-an-event
    res = httpx.post(
        f"{DD_API_BASE}/api/v1/events",
        headers={
            "DD-API-KEY": DATADOG_API_KEY,
        },
        json=payload,
    )
    res.raise_for_status()
    click.echo("\nReported the action to DataDog events:")
    click.echo(res.json()['event']['url'])


def report_event_to_datadog(title: str, text: str, tags: dict) -> None:
    payload = {
        "title": title,
        "text": text,
        "tags": [f"{k}:{v}" for k, v in tags.items()],
        "date_happened": int(time.time()),
        "alert_type": "user_update",
    }
    return send_event_payload_to_datadog(payload)
