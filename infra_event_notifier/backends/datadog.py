import json
import time
import urllib.request
from typing import Mapping
from urllib.error import HTTPError


def send_event(
    title: str,
    text: str,
    tags: Mapping[str, str],
    datadog_api_key: str,
    alert_type: str,
) -> None:
    """
    Sends an event to Datadog.

    :param title: Title of DD event
    :param text: Body of event
    :param tags: dict storing event tags
    :param datadog_api_key: DD API key for sending events
    :param alert_type: Type of event if using an event monitor,
        see https://docs.datadoghq.com/api/latest/events/
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
    req = urllib.request.Request(
        "https://api.datadoghq.com/api/v1/events", data=data
    )
    req.add_header("DD-API-KEY", datadog_api_key)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req) as response:
        status = response.status
        # XXX(ben): docs say events API returns 200,
        # in practice I was getting 202s
        if status > 202:
            raise HTTPError(
                url=response.url,
                code=status,
                msg=f"Recieved {status} response from Datadog",
                hdrs=response.headers,
                fp=None,
            )
