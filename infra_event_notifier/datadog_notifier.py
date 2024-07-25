from typing import Dict

from infra_event_notifier.backends.datadog import send_event


class DatadogNotifier:
    """
    Class that supports sending Datadog notifications.
    A Datadog API key is required.
    """

    def __init__(self, datadog_api_key: str) -> None:
        self.datadog_api_key = datadog_api_key

    def send(
        self,
        title: str,
        body: str,
        tags: Dict[str, str] = {},
        alert_type: str = "",
    ) -> None:
        """
        Sends the event to Datadog with the specified fields.

        Args:
            title (str): Title of the event
            body (str): Main body of the event
            tags (Dict[str, str], Optional): List of tags to add to event.
                Defaults to {}.
            alert_type (str, Optional): Alert type for Datadog event
                Defaults to "".
        """
        if self.datadog_api_key is not None:
            send_event(
                title=title,
                text=body,
                tags=tags,
                datadog_api_key=self.datadog_api_key,
                alert_type=alert_type,
            )
