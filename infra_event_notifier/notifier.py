import os
from typing import Mapping, Self

from infra_event_notifier.backends.datadog import send_event
from infra_event_notifier.backends.jira import (
    create_or_update_issue,
    JiraConfig,
)
from infra_event_notifier.backends.slack import send_notification
#

class Notifier:
    def __init__(self, 
                datadog_api_key:str = None, 
                slack_api_key:str = None, 
                jira_api_key:str = None, 
                jira_url: str = None,
                jira_project: str = None,
                jira_user_email: str = None) -> None:
        # datadog fields
        self.datadog_api_key = datadog_api_key
        # slack fields
        self.slack_api_key = slack_api_key
        # jira fields
        self.jira_config = None
        if jira_api_key != None:
            self.jira_config = JiraConfig(
                url=jira_url,
                user_email=jira_user_email,
                project_key=jira_project,
                api_key=jira_api_key
            )

        self.use_slack = False
        self.use_datadog = False
        self.use_jira = False

        # Notification fields
        self.title = None
        self.text = None
        self.tags = {}
        self.issue_type = None
        self.alert_type = None
        self.fallback_comment_text = None
        self.update_text_body = None

    def slack(self, use_slack:bool = False) -> Self:
        """
        Tell the notifier to notify to Slack. 
        Requires a Slack API Key
        
        Args:
            use_slack (bool): True/False
        """
        self.use_slack = use_slack
        return self

    def datadog(self, use_datadog:bool = False) -> Self:
        """
        Tell the notifier to notify to Datadog. 
        Requires a Datadog API Key
        
        Args:
            use_datadog (bool): True/False
        """
        self.use_datadog = use_datadog
        return self

    def jira(self, use_jira:bool = False) -> Self:
        """
        Tell the notifier to notify to Jira. 
        Requires a Jira API Key
        
        Args:
            use_jira (bool): True/False
        """
        self.use_jira = use_jira
        return self
    
    def set_title(self, title: str) -> Self:
        """
        (Required) Title for the event
        
        Args:
            title (str): Event title
        """
        self.title = title
        return self
    
    def set_text(self, text: str) -> Self:
        """
        (Required) Main body of the event
        
        Args:
            text (str): Event body text
        """
        self.text = text
        return self

    def set_tags(self, tags: Mapping[str, str]) -> Self:
        """
        (Optional) List of tags to add to datadog event/jira issue
        Used to identify and update jira issues if one already exists with the given
        title and tags. Defaults to {}.
        
        Args:
            tags (Mapping[str, str]): Event tags
        """
        self.tags = tags
        return self

    def set_issue_type(self, issue_type:str) -> Self:
        """
        (Optional) Issue type for datadog event, see
        https://docs.datadoghq.com/api/latest/events/ for details. Defaults to None.
        
        Args:
            issue_type (str): issue Type
        """
        self.issue_type = issue_type
        return self
    
    def set_alert_type(self, alert_type:str) -> Self:
        """
        (Optional) Alert type for datadog event, see
        https://docs.datadoghq.com/api/latest/events/ for details. Defaults to None.
        
        Args:
            alert_type (str): Alert Type
        """
        self.alert_type = alert_type
        return self

    def set_fallback_comment_text(self, jira_fallback_comment_text: str) -> Self:
        """
        (Optional) Optional comment to include on jira issue if
        issue already exists. Defaults to None.
        
        Args:
            jira_fallback_comment_text (str): Fallback comment text
        """
        self.fallback_comment_text = jira_fallback_comment_text
        return self

    def set_update_text_body(self, update_text_body:bool) -> Self:
        """
        (Optional) If set, will update the body of an existing Jira issue with whatever is passed
        as the `text` parameter. Defaults to None.
        
        Args:
            update_text_body (bool): Update ticket body?
        """
        self.update_text_body = update_text_body
        return self

    def send(self):
        """
        Sends notifications to whatever backends were configured via with_{backend}()
        For more details on each backend see their respective file
        
        Returns True if the event was successfully sent, False otherwise
        """
        # send DD event
        if self.use_datadog:
            if self.datadog_api_key is not None and self.title and self.text:
                send_event(
                    title=self.title,
                    text=self.text,
                    tags=self.tags,
                    datadog_api_key=self.datadog_api_key,
                    alert_type=self.alert_type,
                )

        # send slack notification
        if self.use_slack:
            # TODO: implement
            if self.slack_api_key is not None and self.title and self.text:
                send_notification(
                    title=self.title, text=self.text, slack_api_key=self.slack_api_key
                )

        # create jira issue
        if self.use_jira:
            if self.jira_config is not None and self.title and self.text:
                create_or_update_issue(
                    jira=self.jira_config,
                    title=self.title,
                    text=self.text,
                    tags=self.tags,
                    issue_type=self.issue_type,
                    fallback_comment_text=self.fallback_comment_text,
                    update_text_body=self.update_text_body
                )


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
            self.datadog(True)
            self.set_title(title)
            self.set_text(text)
            self.set_tags(tags)
            self.set_alert_type(datadog_alert_type)
            self.send()

        # send slack notification
        if self.slack_api_key:
            # TODO: implement
            self.slack(True)
            self.set_title(title)
            self.set_text(text)
            self.send()

        # create jira issue
        if self.jira_api_key:
            self.jira(True)
            self.set_title(title)
            self.set_text(text)
            self.set_tags(tags)
            self.set_fallback_comment_text(jira_fallback_comment_text)
            self.set_update_text_body(jira_update_text_body)
            self.send()

# Testing code, remove before merging
if __name__ == "__main__":
    notif = Notifier(jira_api_key=os.getenv("JIRA_API_KEY", ""), 
                     jira_project="TESTINC", # Must be the id of the project, not the name
                     jira_url="https://getsentry.atlassian.net/", 
                     jira_user_email=os.getenv("JIRA_USER_EMAIL", ""))
    notif.jira(True)
    notif.set_title("Test Infra-Event-Notifier")
    notif.set_text("test updating")
    notif.set_tags({
        "region": "TESTINC",
        "service":"test-infra-event-notifier",
        "issue_type":"test_issue"
    })
    notif.set_issue_type("Task")
    notif.set_fallback_comment_text("Test Comment")
    notif.set_update_text_body(True)
    notif.send()
