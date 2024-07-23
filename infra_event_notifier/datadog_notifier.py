from typing import Mapping, Self

from infra_event_notifier.backends.datadog import send_event

from infra_event_notifier.notifier import Notifier

class DatadogNotifier(Notifier):
    def __init__(self, 
                datadog_api_key:str) -> None:
        super().__init__()
        self.datadog_api_key = datadog_api_key

        # Notification fields
        self.tags = {}
        self.alert_type = None
        self.update_text_body = None

    def set_tags(self, tags: Mapping[str, str]) -> Self:
        """
        (Optional) List of tags to add to datadog event issue
        Used to identify and update datadog issues if one already exists with the given
        title and tags. Defaults to {}.
        
        Args:
            tags (Mapping[str, str]): Event tags
        """
        self.tags = tags
        return self

    def set_alert_type(self, alert_type:str) -> Self:
        """
        (Optional) Alert type for datadog event, see
        https://docs.datadoghq.com/api/latest/events/ for details. Defaults to None.
        
        Args:
            alert_type (str): Alert Type
        """
        self.alert_type = alert_type
        return self


    def send(self):
        """
        Sends the notification
        """
        if self.datadog_api_key is not None and self.title and self.body:
            send_event(
                title=self.title,
                text=self.body,
                tags=self.tags,
                datadog_api_key=self.datadog_api_key,
                alert_type=self.alert_type,
            )