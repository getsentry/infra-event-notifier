from unittest.mock import patch

from infra_event_notifier.backends.datadog import report_event_to_datadog


class TestDatadog:
    @patch("infra_event_notifier.backends.datadog.DATADOG_API_KEY", "fakeapikey")
    @patch("urllib.request.urlopen")
    @patch("urllib.request.Request")
    def test_send_event_payload_to_datadog(self, mock_urlopen, mock_request):
        report_event_to_datadog(title="test", text="test", tags={})
        # mock_urlopen.assert_called_once_with(something)
