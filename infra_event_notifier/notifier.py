from typing import Self


class Notifier:
    """
    Generic class that supports sending notifications to various
    output channels (Jira | Datadog | Slack). To use, see the
    child classes (JiraNotifier | DatadogNotifier | SlackNotifier)
    """

    def __init__(self, title: str, body: str) -> None:
        # Notification fields
        self.title: str = title
        self.body: str = body

    def set_title(self, title: str) -> Self:
        """
        (Required) Title for the event

        Args:
            title (str): Event title
        """
        self.title = title
        return self

    def set_body(self, text: str) -> Self:
        """
        (Required) Main body of the event

        Args:
            text (str): Event body text
        """
        self.body = text
        return self
