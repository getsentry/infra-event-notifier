from typing import cast, Optional, Sequence
import requests
from requests.auth import HTTPBasicAuth


MAX_JIRA_DESCRIPTION_LENGTH = 32000

class JiraConfig:
    def __init__(
        self, url: str, project_key: str, user_email: str, api_token: str
    ):
        self.url = url
        self.project_key = project_key
        self.user_email = user_email
        self.api_token = api_token


class JiraApiException(Exception):
    def __init__(self, stderr: str) -> None:
        self.message = stderr
        super().__init__(self.message)


def create_issue(
    title: str, text: str, labels: Sequence[str], jira: JiraConfig
) -> requests.Response:
    api_url = f"{jira.url}/rest/api/2/issue"

    issue_data = {
        "fields": {
            "project": {"key": jira.project_key},
            "summary": title,
            "description": text[:MAX_JIRA_DESCRIPTION_LENGTH],
            "issuetype": {"name": "Task"},
            "labels": labels,
        }
    }

    response = requests.post(
        api_url,
        json=issue_data,
        auth=HTTPBasicAuth(jira.user_email, jira.api_token),
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 201:
        return response
    else:
        raise JiraApiException(
            f"Failed to create issue: {response.status_code}, {response.text}"
        )


def update_issue(
    jira: JiraConfig, issue_key: str, title: str, text: str
) -> requests.Response:
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}"
    issue_data = {"fields": {"description": text[:MAX_JIRA_DESCRIPTION_LENGTH]}}
    response = requests.put(
        api_url,
        json=issue_data,
        auth=HTTPBasicAuth(jira.user_email, jira.api_token),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 204:
        return response
    else:
        raise JiraApiException(
            f"Failed to update issue: {response.status_code}, {response.text}"
        )


def comment_on_issue(
    jira: JiraConfig, issue_key: str, comment: str
) -> requests.Response:
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}/comment"
    payload = {"body": comment}
    response = requests.post(
        api_url,
        json=payload,
        auth=HTTPBasicAuth(jira.user_email, jira.api_token),
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 201:
        return response
    else:
        raise JiraApiException(
            f"Failed to update issue: {response.status_code}, {response.text}"
        )


def find_issue(jira: JiraConfig, labels: Sequence[str]) -> Optional[str]:
    """
    Searches for a jira issue by labels. Returns the issue key.
    All labels must match, and only the first match is returned.
    """

    api_url = f"{jira.url}/rest/api/2/search"

    jql = f'project = "{jira.project_key}" AND labels in ({", ".join(f"\'{label}\'" for label in labels)})'

    params = {"jql": jql, "fields": "id,key,summary,status"}

    response = requests.get(
        api_url,
        headers={"Accept": "application/json"},
        auth=HTTPBasicAuth(jira.user_email, jira.api_token),
        params=params,
    )

    if response.status_code == 200:
        issues = response.json()["issues"]
        if issues:
            # returns the first issue match
            return cast(str, issues[0]["key"])
        return None
    else:
        raise JiraApiException(
            f"Failed to search issues: {response.status_code}, {response.text}"
        )
