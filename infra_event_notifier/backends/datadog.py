import time
import os
import json

from urllib.request import Request, urlopen
from typing import Mapping


DD_API_BASE = "https://api.datadoghq.com"

DATADOG_API_KEY = os.getenv("DATADOG_API_KEY") or os.getenv("DD_API_KEY")
assert DATADOG_API_KEY, "Please set either DATADOG_API_KEY or DD_API_KEY env var."


def report_event_to_datadog(
    title: str, text: str, tags: Mapping[str, str], alert_type: str = "user_update"
) -> Mapping[str, str]:
    """
    Sends an event to Datadog.
    Requires either the DATADOG_API_KEY or DD_API_KEY env var to be set.
    """
    # API docs: https://docs.datadoghq.com/api/latest/events/#post-an-event
    payload = {
        "title": title,
        "text": text,
        "tags": [f"{k}:{v}" for k, v in tags.items()],
        "date_happened": int(time.time()),
        "alert_type": alert_type,
    }
    jsonData = json.dumps(payload)
    data = jsonData.encode("utf-8")
    req = Request(f"{DD_API_BASE}/api/v1/events", data=data)
    req.add_header("DD-API-KEY", DATADOG_API_KEY)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        return res


if __name__ == "__main__":
    report_event_to_datadog(title="test_from_main", text="text", tags={})
