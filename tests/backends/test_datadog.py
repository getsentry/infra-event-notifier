import json
import time

from unittest.mock import patch, MagicMock

from infra_event_notifier.backends.datadog import send_event


class TestDatadog:
    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    @patch("json.loads")
    @patch("time.time", MagicMock(return_value=12345))
    def test_send_event_request(self, mock_urlopen, mock_request, mock_loads):
        payload = json.dumps(
            {
                "title": "test",
                "text": "test",
                "tags": [],
                "date_happened": 12345,
                "alert_type": "user_update",
            }
        ).encode("utf-8")
        send_event(
            title="test",
            text="test",
            tags={},
            datadog_api_key="fakeapikey",
        )
        mock_request.assert_called_once_with(
            "https://api.datadoghq.com/api/v1/events",
            data=payload,
        )
