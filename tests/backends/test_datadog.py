from unittest.mock import patch

from infra_event_notifier.backends.datadog import notify_datadog


class TestDatadog:
    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_send_event_payload_to_datadog(self, mock_urlopen, mock_request):
        notify_datadog(title="test", text="test", tags={}, datadog_api_key="fakeapikey")
        # mock_urlopen.assert_called_once_with(something)
