import os

from typing import Dict

from backends.datadog import report_event_to_datadog

SENTRY_REGION = os.getenv("SENTRY_REGION", "unknown")


def notify(
    title: str,
    text: str,
    tags: Dict[str, str],
    datadog_event: bool = False,
    slack_notification: bool = False,
    jira_ticket: bool = False,
) -> None:
    """
    Notifies various backends of a given event.

    :param title: Title of slack alert/DD event
    :param text: Body of alert/event
    :param tags: dict storing event tags (datadog/jira)
    :param datadog_event: Sends a datadog event using the given title/text
    :param slack_notification: Sends a slack notification using the given title/text
    :param jira_ticket: Creates a jira ticket using the given title/text
    """
    if datadog_event:
        report_event_to_datadog(title, text, tags)
        # report_event_to_datadog(
        #     title="test-title",
        #     text="test body",
        #     tags={"foo": "bar"},
        #     alert_type="warning",
        # )
    if slack_notification:
        # TODO: implement
        pass
    if jira_ticket:
        # TODO: implement
        pass


if __name__ == "__main__":
    notify()
