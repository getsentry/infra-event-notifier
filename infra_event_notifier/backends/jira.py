from urllib.request import Request, urlopen
import json
from base64 import b64encode
from typing import Mapping
from urllib.parse import quote_plus

MAX_JIRA_DESCRIPTION_LENGTH = 32000


class JiraConfig:
    def __init__(self, url: str, project_key: str, user_email: str):
        self.url = url
        self.project_key = project_key
        self.user_email = user_email


class JiraApiException(Exception):
    def __init__(self, stderr):
        self.message = stderr
        super().__init__(self.message)


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
    title: str,
    text: str,
    tags: Mapping[str, str],
    issue_type: str,
    jira_api_key: str,
    fallback_comment_text: str | None,
    update_text_body: bool | None,
):
    """
    Attempts to create a Jira issue with the given title/text/tags.
    If an issue matching that title and tags already exists, optionally update
    that issue's text body and add a comment.

    Args:
        jira (JiraConfig): Config containing URL/project/email
        title (str): Title of issue
        text (str): Text body for issue
        tags (Mapping[str, str], optional): List of tags to add to jira issue
            Used to identify and update jira issues if one already exists with the given
            title and tags. Defaults to {}.
        issue_type (str): Type of issue. Can be: Task | Story | Bug | Epic
        fallback_comment_text (str | None, optional): Optional comment to include on jira issue if
            issue already exists. Defaults to None.
        update_text_body (bool | None, optional): If set, will update the body of an existing Jira issue with whatever is passed
            as the `text` parameter. Defaults to None.
        jira_api_key (str): Jira API key
    """
    # _create_jira_issue(jira, title, text, tags, issue_type, jira_api_key)
    # return
    key = _find_jira_issue(jira, title, tags, jira_api_key)
    # return
    if key is not None:
        print("Issue Found")
        if update_text_body:
            print("Attempting to update")
            _update_jira_issue(jira, key, text, jira_api_key)
        if fallback_comment_text:
            print("Adding comment")
            _add_jira_comment(jira, key, fallback_comment_text, jira_api_key)
    else:
        print("Creating new Issue")
        _create_jira_issue(jira, title, text, tags, issue_type, jira_api_key)


# TODO: make generic, port to urllib
def _create_jira_issue(
    jira: JiraConfig, 
    title: str, 
    body: str, 
    tags: Mapping[str, str], 
    issue_type: str, 
    api_key: str
):
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
    data = json_data.encode("utf-8")
    req = Request(
        api_url, data=data, method="POST"
    )
    req = http_basic_auth(jira.user_email, api_key, req)
    req.add_header("Content-Type", "application/json")

    with urlopen(req) as response:
        status = response.status

        if status == 201:
            return response
        else:
            raise JiraApiException(
                f"Failed to create issue: {response.status_code}, {response.text}"
            )


# TODO: make generic, port to urllib
def _update_jira_issue(
    jira: JiraConfig,
    issue_key: str,
    body: str,
    api_key: str,
):
    """
    Attempts to update a jira issue given the issue key.
    """
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}"
    payload = {
        "fields": {
            "description": body
        }
    }
    json_data = json.dumps(payload)
    data = json_data.encode("utf-8")
    req = Request(
        api_url, data=data, method="PUT"
    )
    req = http_basic_auth(jira.user_email, api_key, req)
    req.add_header("Content-Type", "application/json")

    with urlopen(req) as response:
        status = response.status

        if status == 204:
            return response
        else:
            raise JiraApiException(
                f"Failed to update issue: {response.status_code}, {response.text}"
            )


# TODO: make generic, port to urllib
def _add_jira_comment(
    jira: JiraConfig, issue_key: str, comment: str, api_key: str
):
    """
    Adds a comment to the given jira issue.
    """
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}/comment"
    payload = {"body": comment}
    json_data = json.dumps(payload)
    data = json_data.encode("utf-8")
    req = Request(
        api_url, data=data, method="POST"
    )
    req = http_basic_auth(jira.user_email, api_key, req)
    req.add_header("Content-Type", "application/json")

    with urlopen(req) as response:
        status = response.status

        if status == 201:
            return response
        else:
            raise JiraApiException(
                f"Failed to update issue: {response.status_code}, {response.text}"
            )


# TODO: fix 400 response from Jira
def _find_jira_issue(
    jira: JiraConfig, title: str, tags: Mapping[str, str], api_key: str
):
    """
    Looks for an open existing jira issue. Return issue key if issue exists, otherwise return nothing.
    """
    api_url = f"{jira.url}/rest/api/2/search"

    jql = (
        f'project = {jira.project_key} '
        # 'AND status != Closed '
        # 'AND status != DONE'
    )
    for key in tags:
        jql += f' AND labels = {key}:{tags[key]}'

    payload = {"jql": jql, "fields": ["id", "key", "summary", "status"]}

    data = json.dumps(payload)
    data = data.encode("utf-8")
    req = Request(api_url, data=data, method="POST")
    req = http_basic_auth(jira.user_email, api_key, req)
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")

    with urlopen(req) as response:
        res_body = json.loads(response.read().decode())
        status = response.status
        print(res_body)
        print(status)
        if status == 200:
            issues = res_body["issues"]
            if issues:
                return issues[0]["key"]
            return None
        else:
            raise JiraApiException(
                f"Failed to search issues: {status}, {response.reason}"
            )


# testing code, remove before merging
if __name__ == "__main__":
    key = _find_jira_issue(
        JiraConfig(
            url="https://getsentry.atlassian.net",
            project_key="TESTINC",
            user_email="ops-incident-bot@sentry.io",
        ),
        title="Test issue please ignore",
        tags={"foo": "bar", "one": "two"},
        api_key="fakeapikey",
    )
    print(key)
