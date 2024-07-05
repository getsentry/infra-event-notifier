from typing import Mapping

from infra_event_notifier.backends.datadog import send_event
from infra_event_notifier.backends.jira import create_issue
from infra_event_notifier.backends.slack import send_notification


class Notifier:
    def __init__(
        self,
        datadog_api_key: str | None = None,
        slack_api_key: str | None = None,
        jira_api_key: str | None = None,
    ) -> None:
        self.datadog_api_key = datadog_api_key
        self.slack_api_key = slack_api_key
        self.jira_api_key = jira_api_key

    def notify(
        self, title: str, text: str, tags: Mapping[str, str], alert_type: str
    ) -> None:
        # send DD event
        if self.datadog_api_key:
            send_event(
                title=title,
                text=text,
                tags=tags,
                datadog_api_key=self.datadog_api_key,
                alert_type=alert_type,
            )

        # send slack notification
        if self.slack_api_key:
            # TODO: implement
            send_notification(
                title=title, text=text, slack_api_key=self.slack_api_key
            )

        # create jira issue
        if self.jira_api_key:
            # TODO: implement
            create_issue(
                title=title,
                text=text,
                tags=tags,
                jira_api_key=self.jira_api_key,
            )
