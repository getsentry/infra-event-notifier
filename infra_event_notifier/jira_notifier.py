from typing import Dict, Self

from infra_event_notifier.backends.jira import (
    JiraConfig,
    create_or_update_issue,
)
from infra_event_notifier.notifier import Notifier


class JiraNotifier(Notifier):
    def __init__(
        self,
        jira_api_key: str,
        jira_url: str,
        jira_project: str,
        jira_user_email: str,
    ) -> None:
        super().__init__()
        self.jira_config = JiraConfig(
            url=jira_url,
            user_email=jira_user_email,
            project_key=jira_project,
            api_key=jira_api_key,
        )

        # Notification fields
        self.tags: Dict[str, str] = {}
        self.issue_type: str = "Task"
        self.fallback_comment_text: None | str = None
        self.update_text_body: None | bool = None

    def set_tags(self, tags: Dict[str, str]) -> Self:
        """
        (Optional) List of tags to add to jira issue
        Used to identify and update jira issues if one already
        exists with the given title and tags. Defaults to {}.

        Args:
            tags (Dict[str, str]): Event tags
        """
        self.tags = tags
        return self

    def set_issue_type(self, issue_type: str) -> Self:
        """
        (Optional) Issue type for jira event, see
        https://docs.datadoghq.com/api/latest/events/ for details.
        Defaults to None.

        Args:
            issue_type (str): issue Type
        """
        self.issue_type = issue_type
        return self

    def set_fallback_comment_text(
        self, jira_fallback_comment_text: str
    ) -> Self:
        """
        (Optional) Optional comment to include on jira issue if
        issue already exists. Defaults to None.

        Args:
            jira_fallback_comment_text (str): Fallback comment text
        """
        self.fallback_comment_text = jira_fallback_comment_text
        return self

    def set_update_text_body(self, update_text_body: bool) -> Self:
        """
        (Optional) If set, will update the body of an existing Jira
        issue with whatever is passed as the `text` parameter.
        Defaults to None.

        Args:
            update_text_body (bool): Update ticket body?
        """
        self.update_text_body = update_text_body
        return self

    def send(self) -> None:
        if self.jira_config is not None and self.title and self.body:
            create_or_update_issue(
                jira=self.jira_config,
                title=self.title,
                text=self.body,
                tags=self.tags,
                issue_type=self.issue_type,
                fallback_comment_text=self.fallback_comment_text,
                update_text_body=self.update_text_body,
            )
