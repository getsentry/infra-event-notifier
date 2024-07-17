from urllib.request import Request, urlopen
import json
from base64 import b64encode
from typing import Mapping

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
    username = username.encode("latin1")
    api_key = api_key.encode("latin1")
    base64string = b64encode(bytes(f"{username}:{api_key}", "ascii"))
    req.add_header("Authorization", f"Basic {base64string.decode('utf-8')}")
    return req


def create_or_update_issue(
    jira: JiraConfig,
    title: str,
    text: str,
    tags: Mapping[str, str],
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
        fallback_comment_text (str | None, optional): Optional comment to include on jira issue if
            issue already exists. Defaults to None.
        update_text_body (bool | None, optional): If set, will update the body of an existing Jira issue with whatever is passed
            as the `text` parameter. Defaults to None.
        jira_api_key (str): Jira API key
    """

    if key := _find_jira_issue(jira, title, tags, jira_api_key):
        if update_text_body:
            _update_jira_issue(jira, tags, text, key, jira_api_key)
        if fallback_comment_text:
            _add_jira_comment(jira, key, fallback_comment_text, jira_api_key)
    else:
        _create_jira_issue(jira, tags, text, jira_api_key)


# TODO: make generic, port to urllib
def _create_jira_issue(
    jira: JiraConfig, region: str, service: str, body: str, api_key: str
):
    """
    Attempts to create a new jira issue.
    """
    api_url = f"{jira.url}/rest/api/2/issue"
    issue_data = {
        "fields": {
            "project": {"key": jira.project_key},
            "summary": f"[Drift Detection]: {region} {service} drifted",
            "description": f"There has been drift detected on {service} for {region}.\n\n{body}",
            "issuetype": {"name": "Task"},
            "labels": [
                f"region:{region}",
                f"service:{service}",
                "issue_type:drift_detection",
            ],
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


# TODO: make generic, port to urllib
def _update_jira_issue(
    jira: JiraConfig,
    region: str,
    service: str,
    body: str,
    issue_key: str,
    api_key: str,
):
    """
    Attempts to update a jira issue given the issue key.
    """
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}"
    issue_data = {
        "fields": {
            "description": f"There has been drift detected on {service} for {region}.\n\n{body}"
        }
    }
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


# TODO: make generic, port to urllib
def _add_jira_comment(
    jira: JiraConfig, issue_key: str, comment: str, api_key: str
):
    """
    Adds a comment to the given jira issue.
    """
    api_url = f"{jira.url}/rest/api/2/issue/{issue_key}/comment"
    payload = {"body": comment}
    response = requests.post(
        api_url,
        json=payload,
        auth=HTTPBasicAuth(jira.user_email, jira.api_token),
        headers={
            "Content-Type": "application/json",
        },
    )
    if response.status_code == 201:
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
        f'project = "{jira.project_key}" '
        'AND status != "CLOSED" '
        'AND status != "DONE"'
    )
    for key in tags:
        jql += f' AND labels = "{key}:{tags[key]}"'

    payload = {"jql": jql, "fields": ["id", "key", "summary", "status"]}

    data = json.dumps(payload)
    data = data.encode("utf-8")
    req = Request(api_url, data=data)
    req = http_basic_auth(jira.user_email, api_key, req)
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")

    with urlopen(req) as response:
        res_body = response.read().decode()
        status = response.status
        print(res_body)
        print(status)
        if status == 200:
            issues = response.json()["issues"]
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
