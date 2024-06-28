from typing import Mapping

from backends.datadog import notify_datadog
from backends.jira import notify_jira
from backends.slack import notify_slack


def notify(
    title: str,
    text: str,
    tags: Mapping[str, str],
    datadog_api_key: str,
    slack_api_key: str,
    jira_api_key: str,
    datadog_event: bool = True,
    slack_notification: bool = True,
    jira_ticket: bool = True,
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
        notify_datadog(title, text, tags, datadog_api_key)
    if slack_notification:
        notify_slack(title, text, slack_api_key)
    if jira_ticket:
        notify_jira(title, text, tags, jira_api_key)
