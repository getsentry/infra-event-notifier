import time
import json

import urllib.request

from typing import Mapping


def send_event(
    title: str,
    text: str,
    tags: Mapping[str, str],
    datadog_api_key: str,
    alert_type: str = "user_update",
) -> Mapping[str, str]:
    """
    Sends an event to Datadog.

    :param title: Title of DD event
    :param text: Body of event
    :param tags: dict storing event tags
    :param datadog_api_key: DD API key for sending events
    :param alert_type: Type of event if using an event monitor, see https://docs.datadoghq.com/api/latest/events/
    """
    # API docs: https://docs.datadoghq.com/api/latest/events/#post-an-event
    payload = {
        "title": title,
        "text": text,
        "tags": [f"{k}:{v}" for k, v in tags.items()],
        "date_happened": int(time.time()),
        "alert_type": alert_type,
    }
    json_data = json.dumps(payload)
    data = json_data.encode("utf-8")
    req = urllib.request.Request("https://api.datadoghq.com/api/v1/events", data=data)
    req.add_header("DD-API-KEY", datadog_api_key)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode("utf-8"))
        return res
