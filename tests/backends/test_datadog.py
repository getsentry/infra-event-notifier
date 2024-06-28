import json
import time

from unittest.mock import patch

from infra_event_notifier.backends.datadog import notify_datadog


class TestDatadog:
    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    @patch("json.loads")
    def test_notify_datadog_request(self, mock_urlopen, mock_request, mock_loads):
        epoch = int(time.time())
        payload = json.dumps(
            {
                "title": "test",
                "text": "test",
                "tags": [],
                "date_happened": epoch,
                "alert_type": "user_update",
            }
        ).encode("utf-8")
        notify_datadog(
            title="test",
            text="test",
            tags={},
            epoch=epoch,
            datadog_api_key="fakeapikey",
        )
        mock_request.assert_called_once_with(
            "https://api.datadoghq.com/api/v1/events",
            data=payload,
        )
