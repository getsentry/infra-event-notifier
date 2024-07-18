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

        # Notification fields
        self.title = None
        self.text = None
        self.tags = {}
        self.alert_type = None
        self.fallback_comment_text = None
        self.update_text_body = None

    def with_datadog(self, datadog_api_key: str) -> Self:
        """
        Specify that the notification is for Datadog.

        Args:
            datadog_api_key (str): Datadog API Key
        """
        self.datadog_api_key = datadog_api_key
        return self

    def with_jira(
        self,
        jira_url: str,
        jira_project: str,
        jira_user_email: str,
        jira_api_key: str,
    ) -> Self:
        """
        Specify that the notification is for Jira.

        Args:
            jira_url (str): Jira URL
            jira_project (str): Jira Project string
            jira_user_email (str): Jira user email
            jira_api_key (str): Jira API Key
        """
        self.jira_api_key = jira_api_key
        self.jira_config = JiraConfig(
            url=jira_url,
            user_email=jira_user_email,
            project_key=jira_project,
        )
        return self

    def with_slack(self, slack_api_key: str) -> Self:
        """
        Specify that the notification is for Slack.

        Args:
            slack_api_key (str): Slack API Key
        """
        self.slack_api_key = slack_api_key
        return self
    
    def set_title(self, title: str):
        """
        (Required) Sets the title for the notification
        
        Args:
            title (str): Notification title
        """
        self.title = title
    
    def set_text(self, text: str):
        """
        (Required) Sets the main text for the notification
        
        Args:
            text (str): Notification text
        """
        self.text = text

    def set_tags(self, tags: Mapping[str, str]):
        """
        (Optional) Sets additional tags for the notification
        Used with Datadog and Jira. Defaults to {}.
        
        Args:
            tags (Mapping[str, str]): Notification tags
        """
        self.tags = tags

    def set_alert_type(self, alert_type:str):
        """
        (Optional) Sets Datadog alert type
        Used with Datadog. Defaults to None.
        
        Args:
            alert_type (str): Alert Type
        """
        self.alert_type = alert_type

    def set_fallback_comment_text(self, jira_fallback_comment_text: str):
        """
        (Optional) Sets the backup comment text
        Used with Jira. Defaults to None.
        
        Args:
            jira_fallback_comment_text (str): Fallback comment text
        """
        self.fallback_comment_text = jira_fallback_comment_text

    def set_update_text_body(self, update_text_body:bool):
        """
        (Optional) Sets whether to update the Jira ticket body (if already existing)
        Used with Jira. Defaults to None.
        
        Args:
            update_text_body (bool): Update ticket body?
        """
        self.update_text_body = update_text_body

    def send(self)->bool:
        """
        Sends notifications to whatever backends were configured via with_{backend}()
        For more details on each backend see their respective file
        
        Returns True if the notification was successfully sent, False otherwise
        """
        # send DD event
        if self.datadog_api_key:
            if self.title != None and self.text != None:
                return send_event(
                    title=self.title,
                    text=self.text,
                    tags=self.tags,
                    datadog_api_key=self.datadog_api_key,
                    alert_type=self.alert_type,
                )
            return False

        # send slack notification
        if self.slack_api_key:
            # TODO: implement
            if self.title != None and self.text != None:
                return send_notification(
                    title=self.title, text=self.text, slack_api_key=self.slack_api_key
                )
            return False

        # create jira issue
        if self.jira_api_key:
            if self.title != None and self.text != None:
                return create_or_update_issue(
                    jira=self.jira_config,
                    title=self.title,
                    text=self.text,
                    tags=self.tags,
                    fallback_comment_text=self.fallback_comment_text,
                    update_text_body=self.update_text_body,
                    jira_api_key=self.jira_api_key,
                )
            return False

        return False


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
