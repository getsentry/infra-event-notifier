# TODO: this was all copied directly from https://github.com/getsentry/ops/blob/master/k8s/cli/libsentrykube/tests/test_jira.py,
# it needs to be made generic (and to fix whatever tests are broken by changes to the main code)

from base64 import b64encode
import io
import json
import pytest
from unittest.mock import MagicMock, patch
from unittest import mock
from infra_event_notifier.backends.jira import (
    JiraConfig,
    _create_jira_issue,
    _find_jira_issue,
    _update_jira_issue,
    _add_jira_comment,
    JiraApiException,
    http_basic_auth,
)
import urllib.request

# from requests.auth import HTTPBasicAuth


@pytest.fixture(autouse=True)
def setup():
    url = "https://test.atlassian.net"
    project_key = "TESTINC"
    user_email = "test@test.com"
    api_token = "test_token"
    return JiraConfig(url, project_key, user_email, api_token)
       

def test_create_issue_success(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 201
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        body = "tokyo drift"
        title = "[Infra Event] Test"
        tags = {
            "region": "TESTINC",
            "service":"test-infra-event-notifier",
            "issue_type":"test_issue"
        }
        issue_type = "Task"

        response = _create_jira_issue(jiraConf, title, body, tags, issue_type)
        mock_post.assert_called_once()
        expected_data = json.dumps(
            {
            "fields": {
                "project": {"key": jiraConf.project_key},
                "summary": title,
                "description": body,
                "issuetype": {"name": issue_type},
                "labels": [f"{k}:{v}" for k, v in tags.items()],
            }
            }
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/issue"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert response.status == 201
        assert req.get_method() == "POST"


def test_create_issue_failure(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 400
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        body = "tokyo drift"
        title = "[Infra Event] Test"
        tags = {
            "region": "TESTINC",
            "service":"test-infra-event-notifier",
            "issue_type":"test_issue"
        }
        issue_type = "Task"
        with pytest.raises(JiraApiException) as exc:
            response = _create_jira_issue(jiraConf, title, body, tags, issue_type)
        mock_post.assert_called_once()
        expected_data = json.dumps(
            {
            "fields": {
                "project": {"key": jiraConf.project_key},
                "summary": title,
                "description": body,
                "issuetype": {"name": issue_type},
                "labels": [f"{k}:{v}" for k, v in tags.items()],
            }
            }
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/issue"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "POST"


def test_update_ticket_success(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 204
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_put:
        body = "tokyo drift"
        issue_key = "JIRA-123"

        response = _update_jira_issue(jiraConf, issue_key, body)
        mock_put.assert_called_once()

        assert response.status == 204
        expected_data = json.dumps(
            {
                "fields": {
                    "description": body
                }
            }
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_put.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/issue/{issue_key}"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "PUT"


def test_update_ticket_failure(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_put:
        body = "tokyo drift"
        issue_key = "JIRA-123"
        with pytest.raises(JiraApiException):
            _update_jira_issue(jiraConf, issue_key, body)
        mock_put.assert_called_once()
        expected_data = json.dumps(
            {
                "fields": {
                    "description": body
                }
            }
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_put.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/issue/{issue_key}"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "PUT"


def test_find_jira_issue_success(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b'{"issues": [{"key": "JIRA-123"}]}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        title = "[Infra Event] Test"
        tags = {
            "region": "TESTINC",
            "service":"test-infra-event-notifier",
            "issue_type":"test_issue"
        }
        issue_key = _find_jira_issue(jiraConf, title, tags)
        mock_post.assert_called_once()

        assert issue_key == "JIRA-123"
        jql = (
            f'project = {jiraConf.project_key} '
            'AND status != Closed '
            'AND status != DONE'
        )
        for key in tags:
            jql += f' AND labels = {key}:{tags[key]}'

        payload = {"jql": jql, "fields": ["id", "key", "summary", "status"]}
        expected_data = json.dumps(
            payload
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/search"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "POST"


def test_find_jira_issue_not_found(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = b'{"issues": []}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        title = "[Infra Event] Test"
        tags = {
            "region": "TESTINC",
            "service":"test-infra-event-notifier",
            "issue_type":"test_issue"
        }
        issue_key = _find_jira_issue(jiraConf, title, tags)
        mock_post.assert_called_once()

        assert issue_key is None
        jql = (
            f'project = {jiraConf.project_key} '
            'AND status != Closed '
            'AND status != DONE'
        )
        for key in tags:
            jql += f' AND labels = {key}:{tags[key]}'

        payload = {"jql": jql, "fields": ["id", "key", "summary", "status"]}
        expected_data = json.dumps(
            payload
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/search"
        assert req._data == expected_data
        print(req.headers)
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "POST"


def test_find_jira_issue_failure(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 400
    mock_response.read.return_value = b'{"issues": []}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        title = ""
        tags = {}
        with pytest.raises(JiraApiException):
            _find_jira_issue(jiraConf, title, tags)
        mock_post.assert_called_once()
        jql = (
            f'project = {jiraConf.project_key} '
            'AND status != Closed '
            'AND status != DONE'
        )
        for key in tags:
            jql += f' AND labels = {key}:{tags[key]}'

        payload = {"jql": jql, "fields": ["id", "key", "summary", "status"]}
        expected_data = json.dumps(
            payload
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))
                                          
        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/search"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "POST"


def test_create_comment_success(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 201
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        issue_key = "JIRA-123"
        test_comment = "test comment"

        response = _add_jira_comment(jiraConf, issue_key, test_comment)

        mock_post.assert_called_once()
        assert response.status == 201

        expected_data = json.dumps(
            {
                "body": test_comment
            }
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/issue/{issue_key}/comment"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "POST"


def test_create_comment_failure(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 400
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        issue_key = "JIRA-123"
        test_comment = "test comment"

        with pytest.raises(JiraApiException):
            _add_jira_comment(jiraConf, issue_key, test_comment)

        mock_post.assert_called_once()

        expected_data = json.dumps(
            {
                "body": test_comment
            }
        ).encode("utf-8")
        base64string = b64encode(bytes(f"{jiraConf.user_email}:{jiraConf.api_key}", "utf-8"))

        req = mock_post.call_args.args[0]
        assert req._full_url == f"{jiraConf.url}/rest/api/2/issue/{issue_key}/comment"
        assert req._data == expected_data
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["Authorization"] == f"Basic {base64string.decode('utf-8')}"
        assert req.get_method() == "POST"