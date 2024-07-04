import json
import pytest

from unittest.mock import patch, MagicMock
from urllib.error import HTTPError

from infra_event_notifier.backends.datadog import send_event


def mock_context_manager() -> MagicMock:
    # mocking context managers is hard
    cm = MagicMock()
    cm.status = 200
    cm.__enter__.return_value = cm
    return cm


class TestDatadog:
    @patch("infra_event_notifier.backends.datadog.urllib.request.urlopen")
    @patch("time.time", MagicMock(return_value=12345))
    def test_send_event_request(self, mock_urlopen):
        mock_urlopen.return_value = mock_context_manager()

        data = json.dumps(
            {
                "title": "test",
                "text": "test",
                "tags": [],
                "date_happened": 12345,
                "alert_type": "user_update",
            }
        ).encode("utf-8")
        headers = {
            "Dd-api-key": "fakeapikey",
            "Content-type": "application/json; charset=utf-8",
        }
        send_event(
            title="test",
            text="test",
            tags={},
            datadog_api_key="fakeapikey",
            alert_type="user_update",
        )
        req = mock_urlopen.call_args.args[0]
        assert req._full_url == "https://api.datadoghq.com/api/v1/events"
        assert req._data == data
        assert req.headers == headers

    @patch("infra_event_notifier.backends.datadog.urllib.request.urlopen")
    def test_bad_request(self, mock_urlopen):
        mock_urlopen.return_value = mock_context_manager()
        mock_urlopen.side_effect = HTTPError(
            "https://app.datadoghq.com/event/",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=None,
        )
        with pytest.raises(HTTPError):
            send_event(
                title="test",
                text="test",
                tags={},
                datadog_api_key="fakeapikey",
                alert_type="user_update",
            )
