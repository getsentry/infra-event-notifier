from typing import Dict

from infra_event_notifier.backends.jira import (
    JiraConfig,
    JiraFields,
    create_or_update_issue,
)


class JiraNotifier:
    """
    Class that supports sending Jira notifications.
    A Jira API Key, API URL, Project ID, and User email
    are required.
    """

    def __init__(
        self,
        jira_api_key: str,
        jira_url: str,
        jira_project: str,
        jira_user_email: str,
    ) -> None:
        self.jira_config = JiraConfig(
            url=jira_url,
            user_email=jira_user_email,
            project_key=jira_project,
            api_key=jira_api_key,
        )

    def send(
        self,
        title: str,
        body: str,
        tags: Dict[str, str] = {},
        issue_type: str = "Task",
        fallback_comment_text: str | None = None,
        update_text_body: bool = False,
    ) -> None:
        """
        Creates an issue on Jira with the specified fields.

        Args:
            title (str): Title of the issue
            body (str): Main body of the issue
            tags (Dict[str, str], Optional): List of tags to add to jira issue
                Used to identify and update jira issues if one already
                exists with the given title and tags. Defaults to {}.
            issue_type (str, Optional): Issue type for jira event,
                can be: Task | Story | Bug | Epic
                Defaults to Task.
            fallback_comment_text (str, Optional): Comment to include
                on jira issue if issue already exists. Defaults to None.
            update_text_body (bool, Optional): If set, will update the
                body of an existing Jira issue with whatever is passed
                as the `text` parameter. Defaults to False.
        """
        assert self.jira_config is not None, "Notification missing config"

        fields = JiraFields(title, body, tags, issue_type)
        create_or_update_issue(
            jira=self.jira_config,
            fields=fields,
            fallback_comment_text=fallback_comment_text,
            update_text_body=update_text_body,
        )
