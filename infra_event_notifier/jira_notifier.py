from typing import Dict, Self

from infra_event_notifier.backends.jira import (
    JiraConfig,
    JiraFields,
    create_or_update_issue,
)
from infra_event_notifier.notifier import Notifier


class JiraNotifier(Notifier):
    """
    Class that supports sending Jira notifications. A Title and Body
    are required, as well as Jira config settings.
    """

    def __init__(
        self,
        title: str,
        body: str,
        jira_api_key: str,
        jira_url: str,
        jira_project: str,
        jira_user_email: str,
    ) -> None:
        super().__init__(title, body)
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
        self.update_text_body: bool = False

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
        (Optional) Issue type for jira event,
        can be: Task | Story | Bug | Epic
        Defaults to Task.

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
        assert self.jira_config is not None, "Notification missing config"
        assert self.title is not None, "Notification missing title"
        assert self.body is not None, "Notification missing body"

        fields = JiraFields(self.title, self.body, self.tags, self.issue_type)
        create_or_update_issue(
            jira=self.jira_config,
            fields=fields,
            fallback_comment_text=self.fallback_comment_text,
            update_text_body=self.update_text_body,
        )
