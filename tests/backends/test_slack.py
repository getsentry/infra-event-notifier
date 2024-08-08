import json
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import pytest

from infra_event_notifier.backends.slack import send_notification


def mock_context_manager() -> MagicMock:
    # mocking context managers is hard
    cm = MagicMock()
    cm.status = 200
    cm.__enter__.return_value = cm
    return cm


class TestSlack:
    @patch("infra_event_notifier.backends.datadog.urllib.request.urlopen")
    def test_send_notification_request(self, mock_urlopen):
        mock_urlopen.return_value = mock_context_manager()

        data = json.dumps(
            {
                "source": "infra-event-notifier",
                "title": "test",
                "body": "test",
            },
            separators=(",", ":"),
        ).encode("utf-8")
        headers = {
            "X-infra-event-notifier-signature": (
                "ea943dbec103c09d406eea667bd549c4094a750d94a651297109887d1cb86513"  # noqa
            ),
            "Content-type": "application/json; charset=utf-8",
        }
        send_notification(
            title="test",
            text="test",
            eng_pipes_key="fakeapikey",
            eng_pipes_url="https://example.com/",
        )
        req = mock_urlopen.call_args.args[0]
        assert req._full_url == "https://example.com/"
        assert req._data == data
        assert req.headers == headers

    @patch("infra_event_notifier.backends.datadog.urllib.request.urlopen")
    def test_bad_request(self, mock_urlopen) -> None:
        mock_urlopen.return_value = mock_context_manager()
        mock_urlopen.side_effect = HTTPError(
            "https://example.com/",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=None,
        )
        with pytest.raises(HTTPError):
            send_notification(
                title="test",
                text="test",
                eng_pipes_key="fakeapikey",
                eng_pipes_url="https://example.com/",
            )
