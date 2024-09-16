import os
import json
import time
import urllib.request
from typing import Mapping
from urllib.error import HTTPError


# This category is supposed to be shared by other Sentry tools (terraform,
# salt, etc.) that report event to DataDog.
DEFAULT_EVENT_SOURCE_CATEGORY = "infra-tools"


def api_key_from_env() -> str:
    dd_api_key = os.getenv("DATADOG_API_KEY") or os.getenv("DD_API_KEY")
    if dd_api_key is None or dd_api_key == "":
        raise ValueError(
            "ERROR: You must provide a Datadog API key. Set "
            "environment variable DATADOG_API_KEY or DD_API_KEY."
        )
    return dd_api_key


def markdown_text(text: str) -> str:
    return f"%%%\n{text}\n%%%"


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
