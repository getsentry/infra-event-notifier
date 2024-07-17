from typing import Mapping, Self

from infra_event_notifier.backends.datadog import send_event
from infra_event_notifier.backends.jira import (
    create_or_update_issue,
    JiraConfig,
)
from infra_event_notifier.backends.slack import send_notification


class Notifier:
    def __init__(self) -> None:
        # datadog fields
        self.datadog_api_key = None
        # slack fields
        self.slack_api_key = None
        # jira fields
        self.jira_api_key = None
        self.jira_config = None

    def with_datadog(self, datadog_api_key: str) -> Self:
        self.datadog_api_key = datadog_api_key
        return self

    def with_jira(
        self,
        jira_url: str,
        jira_project: str,
        jira_user_email: str,
        jira_api_key: str,
    ) -> Self:
        self.jira_api_key = jira_api_key
        self.jira_config = JiraConfig(
            url=jira_url,
            user_email=jira_user_email,
            project_key=jira_project,
        )
        return self

    def with_slack(self, slack_api_key: str) -> Self:
        self.slack_api_key = slack_api_key
        return self

    def notify(
        self,
        title: str,
        text: str,
        tags: Mapping[str, str] = {},
        datadog_alert_type: str | None = None,
        jira_fallback_comment_text: str | None = None,
        jira_update_text_body: bool | None = None,
    ) -> None:
        """
        Sends notifications to whatever backends were configured via with_{backend}()
        For more details on each backend see their respective file

        Args:
            title (str): Title of event
            text (str): Text body for event
            tags (Mapping[str, str], optional): List of tags to add to datadog event/jira issue
                Used to identify and update jira issues if one already exists with the given
                title and tags. Defaults to {}.
            datadog_alert_type (str | None, optional): Alert type for datadog event, see
                https://docs.datadoghq.com/api/latest/events/ for details. Defaults to None.
            jira_fallback_comment_text (str | None, optional): Optional comment to include on jira issue if
                issue already exists. Defaults to None.
            jira_update_text_body (bool | None, optional): If set, will update the body of an existing Jira issue with whatever is passed
                as the `text` parameter. Defaults to None.
        """
        # send DD event
        if self.datadog_api_key:
            send_event(
                title=title,
                text=text,
                tags=tags,
                datadog_api_key=self.datadog_api_key,
                alert_type=datadog_alert_type,
            )

        # send slack notification
        if self.slack_api_key:
            # TODO: implement
            send_notification(
                title=title, text=text, slack_api_key=self.slack_api_key
            )

        # create jira issue
        if self.jira_api_key:
            create_or_update_issue(
                jira=self.jira_config,
                title=title,
                text=text,
                tags=tags,
                fallback_comment_text=jira_fallback_comment_text,
                update_text_body=jira_update_text_body,
                jira_api_key=self.jira_api_key,
            )
