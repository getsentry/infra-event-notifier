import time
from urllib.request import Request, urlopen
import os
import json

from typing import Any, Dict


DD_API_BASE = "https://api.datadoghq.com"

DATADOG_API_KEY = os.getenv("DATADOG_API_KEY") or os.getenv("DD_API_KEY")
assert DATADOG_API_KEY, "Please set either DATADOG_API_KEY or DD_API_KEY env var."


def send_event_payload_to_datadog(payload: Dict[str, Any]) -> str:
    # API docs: https://docs.datadoghq.com/api/latest/events/#post-an-event
    jsonData = json.dumps(payload)
    data = jsonData.encode("utf-8")
    req = Request(f"{DD_API_BASE}/api/v1/events", data=data)
    req.add_header("DD-API-KEY", DATADOG_API_KEY)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urlopen(req) as response:
        response.read().decode("utf-8")


def report_event_to_datadog(
    title: str, text: str, tags: Dict[str, Any], alert_type: str = "user_update"
) -> None:
    payload = {
        "title": title,
        "text": text,
        "tags": [f"{k}:{v}" for k, v in tags.items()],
        "date_happened": int(time.time()),
        "alert_type": alert_type,
    }
    return send_event_payload_to_datadog(payload)
