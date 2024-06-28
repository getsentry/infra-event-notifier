import os

from typing import Dict

from backends.datadog import report_event_to_datadog

SENTRY_REGION = os.getenv("SENTRY_REGION", "unknown")


def notify_datadog(
    title: str,
    text: str,
    tags: Dict[str, str],
) -> None:
    """
    Sends an event to datadog.
    Useful if you want to send different payloads to different backends, otherwise use notify().
    """
    report_event_to_datadog(title, text, tags)


def notify_slack(
    title: str,
    text: str,
) -> None:
    """
    Sends a notification to slack.
    Useful if you want to send different payloads to different backends, otherwise use notify().
    """
    # TODO: implement
    pass


def notify_jira(
    title: str,
    text: str,
    tags: Dict[str, str],
) -> None:
    """
    Create an issue in Jira.
    Useful if you want to send different payloads to different backends, otherwise use notify().
    """
    # TODO: implement
    pass


def notify(
    title: str,
    text: str,
    tags: Dict[str, str],
    datadog_event: bool = True,
    slack_notification: bool = True,
    jira_ticket: bool = True,
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
