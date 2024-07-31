import json
import urllib.request  # must use urllib.request.urlopen() in order to do tests
from base64 import b64encode
from enum import Enum
from typing import Any, Dict, Mapping
from urllib.request import Request

MAX_JIRA_DESCRIPTION_LENGTH = 32000


class JiraApiException(Exception):
    pass


class JiraConfig:
    """
    Contains Jira Config info

    Args:
        url (str): Base Jira API URL
        project_key (str): Project ID of the project to create events for
        user_email (str): Email of the User sending Jira issues
        api_key (str): Jira API Key
    """

    def __init__(
        self, url: str, project_key: str, user_email: str, api_key: str
    ) -> None:
        self.url = url
        self.project_key = project_key
        self.user_email = user_email
        self.api_key = api_key


class IssueType(Enum):
    TASK = "Task"
    BUG = "Bug"
    STORY = "Story"
    EPIC = "Epic"


class JiraFields:
    """
    Contains the fields for a Jira Issue

    Args:
        title (str): Title of issue
        text (str): Text body for issue
        tags (Dict[str, str], optional): List of tags to add to jira issue
            Used to identify and update jira issues if one already exists
            with the given title and tags. Defaults to {}.
        issue_type (IssueType): Type of issue.
            Can be: Task | Story | Bug | Epic
    """

    def __init__(
        self,
        title: str,
        text: str,
        issue_type: IssueType,
        tags: Dict[str, str] = {},
    ) -> None:
        self.title = title
        self.text = text
        self.tags = tags
        self.issue_type = issue_type


def http_basic_auth(username: str, api_key: str, req: Request) -> Request:
    """
    Does the equivalent of requests' HTTPBasicAuth but for a urllib Request

    Args:
        username (str): Username for basic auth
        api_key (str): API key for basic auth
        req (Request): Request object to attach headers to
    """
    base64string = b64encode(bytes(f"{username}:{api_key}", "utf-8"))
    req.add_header("Authorization", f"Basic {base64string.decode('utf-8')}")
    return req


def create_or_update_issue(
    jira: JiraConfig,
    fields: JiraFields,
    fallback_comment_text: str | None,
    update_text_body: bool = False,
) -> None:
    """
    Attempts to create a Jira issue with the given title/text/tags.
    If an issue matching that title and tags already exists, optionally update
    that issue's text body and add a comment.

    Args:
        jira (JiraConfig): Config containing URL/project/email/API Key
        fields (JiraFields): Fields of the Jira Issue
        fallback_comment_text (str | None, optional): Optional comment to
            include on jira issue if issue already exists. Defaults to None.
        update_text_body (bool, optional): If set, will update the
            body of an existing Jira issue with whatever is passed
            as the `text` parameter. Defaults to False.
    """
    key = _find_jira_issue(jira, fields.title, fields.tags)
    if key is not None:
        if update_text_body:
            _update_jira_issue(jira, key, fields.text)
        if fallback_comment_text:
            _add_jira_comment(jira, key, fallback_comment_text)
    else:
        _create_jira_issue(
            jira,
            fields.title,
            fields.text,
            fields.tags,
            fields.issue_type.value,
        )


def _create_jira_issue(
    jira: JiraConfig,
    title: str,
    body: str,
    tags: Mapping[str, str],
    issue_type: str,
) -> None:
    """
    Attempts to create a new jira issue.
    """
    api_url = f"{jira.url}/rest/api/2/issue"
    payload = {
        "fields": {
            "project": {"key": jira.project_key},
            "summary": title,
            "description": body,
            "issuetype": {"name": issue_type},
            "labels": [f"{k}:{v}" for k, v in tags.items()],
        }
    }
    json_data = json.dumps(payload)
    send_request(
        api_url, json_data, "POST", 201, jira.user_email, jira.api_key
    )


def _update_jira_issue(jira: JiraConfig, issue_key: str, body: str) -> None:
    """
    Attempts to update a jira issue given the issue key.
    """
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}"
    payload = {"fields": {"description": body}}
    json_data = json.dumps(payload)
    send_request(api_url, json_data, "PUT", 204, jira.user_email, jira.api_key)


def _add_jira_comment(jira: JiraConfig, issue_key: str, comment: str) -> None:
    """
    Adds a comment to the given jira issue.
    """
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}/comment"
    payload = {"body": comment}
    json_data = json.dumps(payload)
    send_request(
        api_url, json_data, "POST", 201, jira.user_email, jira.api_key
    )


def send_request(
    url: str,
    payload: str,
    method: str,
    expected_status: int,
    user_email: str,
    api_key: str,
) -> None:
    """
    Sends an HTTP request using urllib. Raises a JiraApiException
    if the returned status does not match the expected status.
    """
    data = payload.encode("utf-8")
    req = Request(url, data=data, method=method)
    req = http_basic_auth(user_email, api_key, req)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as response:
        status = response.status

        if status != expected_status:
            raise JiraApiException(
                f"Failed to create or update issue: "
                f"{response.status_code}, {response.text}"
            )


# Find the jira issue using only the tags
# Not sure if we should also include the issue title in the search
def _find_jira_issue(
    jira: JiraConfig, title: str, tags: Mapping[str, str]
) -> Any:
    """
    Looks for an open existing jira issue. Return issue key if issue exists,
    otherwise return nothing.
    """
    api_key = jira.api_key
    api_url = f"{jira.url}/rest/api/2/search"

    jql = (
        f"project = {jira.project_key} "
        "AND status != Closed "
        "AND status != DONE"
    )
    for key in tags:
        jql += f" AND labels = {key}:{tags[key]}"

    payload = {"jql": jql, "fields": ["id", "key", "summary", "status"]}

    data = json.dumps(payload)
    data_bytes = data.encode("utf-8")
    req = Request(api_url, data=data_bytes, method="POST")
    req = http_basic_auth(jira.user_email, api_key, req)
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as response:
        res_body = json.loads(response.read().decode())
        status = response.status

        if status == 200:
            issues = res_body["issues"]
            if issues:
                return issues[0]["key"]
            return None
        else:
            raise JiraApiException(
                f"Failed to search issues: {status}, {response.reason}"
            )
