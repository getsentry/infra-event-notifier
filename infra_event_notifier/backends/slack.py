import hashlib
import hmac
import json
import urllib.request
from urllib.error import HTTPError


def send_notification(
    title: str, text: str, eng_pipes_key: str, eng_pipes_url: str
) -> None:
    """
    Sends an event to Slack via eng-pipes.
    See: https://github.com/getsentry/eng-pipes

    :param title: Title of Slack Message
    :param text: Body of Slack Message
    :param channel_id: ID of the Slack channel to send the message to
    :param eng_pipes_key: Secret Key used to HMAC sign request
    :param eng_pipes_url: Full URL for eng-pipes slack webhooks
    """
    payload = {"source": "infra-event-notifier", "title": title, "body": text}
    json_data = json.dumps(
        payload, separators=(",", ":")
    )  # must not allow whitespace in json string
    data = json_data.encode("utf-8")
    req = urllib.request.Request(eng_pipes_url, data=data)
    signature = hmac.new(
        bytes(eng_pipes_key, "utf-8"), msg=data, digestmod=hashlib.sha256
    ).hexdigest()
    req.add_header("x-infra-event-notifier-signature", signature)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req) as response:
        status = response.status
        if status > 202:
            raise HTTPError(
                url=response.url,
                code=status,
                msg=f"Recieved {status} response from Datadog",
                hdrs=response.headers,
                fp=None,
            )
