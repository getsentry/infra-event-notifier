# TODO: this was all copied directly from https://github.com/getsentry/ops/blob/master/k8s/cli/libsentrykube/tests/test_jira.py,
# it needs to be made generic (and to fix whatever tests are broken by changes to the main code)

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
        assert response.status == 201


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


def test_update_ticket_success(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.status = 204
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        body = "tokyo drift"
        issue_key = "JIRA-123"

        response = _update_jira_issue(jiraConf, issue_key, body)
        mock_post.assert_called_once()

        # Comment: Not exactly sure what the point of the tests are if we're 
        # explicitly mocking the request responses, and are unable to check
        # the request headers
        assert response.status == 204


def test_update_ticket_failure(setup):
    jiraConf = setup
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value = mock_response) as mock_post:
        body = "tokyo drift"
        issue_key = "JIRA-123"
        with pytest.raises(JiraApiException):
            _update_jira_issue(jiraConf, issue_key, body)
        mock_post.assert_called_once()


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
