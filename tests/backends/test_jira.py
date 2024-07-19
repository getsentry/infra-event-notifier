# TODO: this was all copied directly from https://github.com/getsentry/ops/blob/master/k8s/cli/libsentrykube/tests/test_jira.py,
# it needs to be made generic (and to fix whatever tests are broken by changes to the main code)

import json
import pytest
from unittest.mock import MagicMock, patch
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
    mock_response = MagicMock()
    jiraConf = setup
    mock_response.status = 201
    mock_response.read.return_value = b'{"key": "JIRA-123"}'
    with patch("urllib.request.urlopen", return_value=mock_response) as mock_post:
        body = "tokyo drift"
        title = "[Infra Event] Test"
        tags = {
            "region": "TESTINC",
            "service":"test-infra-event-notifier",
            "issue_type":"test_issue"
        }
        issue_type = "Task"

        with pytest.raises(JiraApiException):
            response = _create_jira_issue(jiraConf, title, body, tags, issue_type)
        mock_post.assert_called_once_with(
            "https://test.atlassian.net/rest/api/2/issue",
            data={
                "fields": {
                    "project": {"key": "TEST"},
                    "summary": title,
                    "description": body,
                    "issuetype": {"name": issue_type},
                    "labels": [f"{k}:{v}" for k, v in tags.items()]
                }
            },
            method="POST",
        )

        # assert res_body[0]["key"] == "JIRA-123"
        assert mock_post.status == 201


def test_create_issue_failure(setup):
    mock_response = MagicMock()
    mock_response.status_code = 400
    jiraConf = setup

    with patch("requests.post", return_value=mock_response) as mock_post:
        region = "saas"
        service = "relay"
        body = ["slowly drifting"]

        with pytest.raises(JiraApiException):
            _create_jira_issue(jiraConf, region, service, body)
        mock_post.assert_called_once_with(
            "https://test.atlassian.net/rest/api/2/issue",
            json={
                "fields": {
                    "project": {"key": "TEST"},
                    "summary": f"[Drift Detection]: {region} {service} drifted",
                    "description": f"There has been drift detected on {service} for {region}.\n\n{body}",
                    "issuetype": {"name": "Task"},
                    "labels": [
                        f"region:{region}",
                        f"service:{service}",
                        "issue_type:drift_detection",
                    ],
                }
            },
            auth=HTTPBasicAuth("test@test.com", "test_token"),
            headers={"Content-Type": "application/json"},
        )


def test_update_ticket_success(setup):
    mock_response = MagicMock()
    mock_response.status_code = 204
    jiraConf = setup

    with patch("requests.put", return_value=mock_response) as mock_put:
        issue_key = "JIRA-123"
        region = "saas"
        service = "relay"
        body = ["toyko drift"]

        response = _update_jira_issue(
            jiraConf, region, service, body, issue_key
        )
        mock_put.assert_called_once_with(
            f"https://test.atlassian.net/rest/api/2/issue/{issue_key}",
            json={
                "fields": {
                    "description": f"There has been drift detected on {service} for {region}.\n\n{body}"
                }
            },
            auth=HTTPBasicAuth("test@test.com", "test_token"),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 204


def test_update_ticket_failure(setup):
    mock_response = MagicMock()
    jiraConf = setup

    with patch("requests.put", return_value=mock_response):
        issue_key = "JIRA-123"
        region = "saas"
        service = "relay"
        body = ["update: drift persistence noticed"]
        with pytest.raises(JiraApiException):
            _update_jira_issue(jiraConf, issue_key, region, service, body)


def test_find_jira_issue_success(setup):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"issues": [{"key": "JIRA-123"}]}
    jiraConf = setup

    with patch("requests.get", return_value=mock_response):
        region = "saas"
        service = "relay"

        issue_key = _find_jira_issue(jiraConf, region, service)
        assert issue_key == "JIRA-123"


def test_find_jira_issue_not_found(setup):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"issues": []}
    jiraConf = setup

    with patch("requests.get", return_value=mock_response):
        region = "saas"
        service = "relay"

        issue_key = _find_jira_issue(jiraConf, region, service)
        assert issue_key is None


def test_find_jira_issue_failure(setup):
    mock_response = MagicMock()
    mock_response.status_code = 400
    jiraConf = setup

    with patch("requests.get", return_value=mock_response):
        region = "saas"
        service = "relay"
        with pytest.raises(JiraApiException):
            _find_jira_issue(jiraConf, region, service)


def test_create_comment_success(setup):
    mock_response = MagicMock()
    mock_response.status_code = 201
    jiraConf = setup

    with patch("requests.post", return_value=mock_response) as mock_post:
        issue_key = "JIRA-123"
        test_comment = "test comment"
        response = _add_jira_comment(jiraConf, issue_key, test_comment)

        mock_post.assert_called_once_with(
            f"https://test.atlassian.net/rest/api/2/issue/{issue_key}/comment",
            json={"body": test_comment},
            auth=HTTPBasicAuth("test@test.com", "test_token"),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 201


def test_create_comment_failure(setup):
    mock_response = MagicMock()
    mock_response.status_code = 400
    jiraConf = setup

    with patch("requests.post", return_value=mock_response):
        issue_key = "JIRA-123"
        test_comment = "test comment"
        with pytest.raises(JiraApiException):
            _add_jira_comment(jiraConf, issue_key, test_comment)
