from typing import Mapping

from backends.datadog import send_event
from backends.jira import create_issue
from backends.slack import send_notification


def notify(
    title: str,
    text: str,
    tags: Mapping[str, str],
    datadog_api_key: str,
    slack_api_key: str,
    jira_api_key: str,
    datadog_event: bool = False,
    slack_notification: bool = False,
    jira_ticket: bool = False,
) -> None:
    """
    Notifies various backends of a given event.
    The same text bodies and titles will be used for each backend.
    To send different text bodies to different backends, use the `notify_{backend}()`
    function within each backend.

    :param title: Title of slack alert/DD event
    :param text: Body of alert/event
    :param tags: dict storing event tags (datadog/jira)
    :param datadog_api_key: DD API key for sending events
    :param slack_api_key: Slack API key for sending notifications
    :param jira_api_key: Jira API key for creating issues
    :param datadog_event: Sends a datadog event using the given title/text
    :param slack_notification: Sends a slack notification using the given title/text
    :param jira_ticket: Creates a jira ticket using the given title/text
    """
    if datadog_event:
        send_event(title, text, tags, datadog_api_key)
    if slack_notification:
        send_notification(title, text, slack_api_key)
    if jira_ticket:
        create_issue(title, text, tags, jira_api_key)
