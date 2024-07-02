from typing import Mapping

from backends.datadog import send_event
from backends.jira import create_issue
from backends.slack import send_notification


class Notifier:
    def __init__(
        self,
        datadog_api_key: str = None,
        slack_api_key: str = None,
        jira_api_key: str = None,
    ) -> None:
        self.datadog_api_key = datadog_api_key
        self.slack_api_key = slack_api_key
        self.jira_api_key = jira_api_key

    def send_datadog_event(
        self,
        title: str,
        text: str,
        tags: Mapping[str, str],
        alert_type: str,
    ):
        """
        Sends an event to Datadog.

        :param title: Title of DD event
        :param text: Body of event
        :param tags: dict storing event tags
        :param alert_type: Type of event if using an event monitor, see https://docs.datadoghq.com/api/latest/events/
        """
        if not self.datadog_api_key:
            raise ValueError("datadog_api_key must be set to send events")
        api_key = self.datadog_api_key
        send_event(
            title=title,
            text=text,
            tags=tags,
            datadog_api_key=api_key,
            alert_type=alert_type,
        )

    def send_slack_notification(self, title, text):
        if not self.slack_api_key:
            raise ValueError("slack_api_key must be set to send notifications")
        # TODO: implement
        send_notification(title=title, text=text, slack_api_key=self.slack_api_key)

    def create_jira_issue(self, title, text, tags):
        if not self.jira_api_key:
            raise ValueError("jira_api_key must be set to create issues")
        # TODO: implement
        create_issue(title=title, text=text, tags=tags, jira_api_key=self.jira_api_key)
