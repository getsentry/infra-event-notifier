import argparse
import os
import pytest
from argparse import Namespace
from unittest.mock import MagicMock, patch

from infra_event_notifier.cli.datadog import DatadogCommand

FAKE_DD_KEY = "I_AM_A_DATADOG_KEY"


def _mock_getenv_empty(key: str, default=None):
    if key in ("DATADOG_API_KEY", "DD_API_KEY"):
        return None
    return "DUMMY_VALUE"


def _mock_getenv_set(key: str, default=None):
    if key in ("DATADOG_API_KEY", "DD_API_KEY"):
        return FAKE_DD_KEY
    return os.getenv(key, default)


class TestCLI:
    @pytest.fixture
    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help="sub-commands", required=True)
        DatadogCommand().submenu(subparsers)
        return parser

    @pytest.fixture
    def getenv_empty(self) -> MagicMock:
        return MagicMock(side_effect=_mock_getenv_empty)

    @pytest.fixture
    def getenv_set(self) -> MagicMock:
        return MagicMock(side_effect=_mock_getenv_set)

    @pytest.fixture
    def send_event(self) -> MagicMock:
        return MagicMock()

    def test_parse_title(self, parser: argparse.ArgumentParser):
        examples = [
            [
                "datadog",
                "--title",
                "Uh oh! Kafka cluster `antartica` turned into a fly!",
            ],
            [
                "datadog",
                "--title=Uh oh! Kafka cluster `antartica` turned into a fly!",
            ],
        ]

        for example in examples:
            args = parser.parse_args(example)
            assert (
                args.title
                == "Uh oh! Kafka cluster `antartica` turned into a fly!"
            )
            assert args.message is None
            assert args.source is None
            assert args.tag is None

    def test_parse_overall(self, parser: argparse.ArgumentParser):
        example = [
            "datadog",
            "--title",
            "Actuated synergy manifest: xfn-enablement-layer",
            "--message",
            "Please refer to Bill's 82-slide presentation for details.",
            "--source=synergy-manifest-actuater",
        ]
        args = parser.parse_args(example)
        assert args.title == "Actuated synergy manifest: xfn-enablement-layer"
        assert (
            args.message
            == "Please refer to Bill's 82-slide presentation for details."
        )
        assert args.source == "synergy-manifest-actuater"

    def test_parse_tags(self, parser: argparse.ArgumentParser):
        example = [
            "datadog",
            "-t",
            "foo=bar",
            "--tag",
            "syns=acked",
            "--tag=body=ready",
        ]
        args = parser.parse_args(example)
        assert "foo=bar" in args.tag
        assert "syns=acked" in args.tag
        assert "body=ready" in args.tag

    def test_missing_datadog_key(self, getenv_empty: MagicMock):
        args = Namespace(
            title="This is really important you gotta tell The Dog!!!",
            message=None,
            source=None,
            tag=None,
            dry_run=None,
        )
        command = DatadogCommand()

        with patch("os.getenv", getenv_empty):
            with pytest.raises(ValueError):
                command.execute(args)

    def test_dry_run(self, getenv_set: MagicMock, send_event: MagicMock):
        args = Namespace(
            title="This is really important you gotta tell The Dog!!!",
            message=None,
            source=None,
            tag=None,
            dry_run=True,
        )

        command = DatadogCommand()
        with patch("os.getenv", getenv_set):
            with patch(
                "infra_event_notifier.backends.datadog.send_event", send_event
            ):
                command.execute(args)

                getenv_set.assert_called()
                send_event.assert_not_called()

    def test_send(self, getenv_set: MagicMock, send_event: MagicMock):
        args = Namespace(
            title="This is really important you gotta tell The Dog!!!",
            message=None,
            source=None,
            tag=None,
            dry_run=None,
        )
        command = DatadogCommand()
        with patch("os.getenv", getenv_set):
            with patch(
                "infra_event_notifier.backends.datadog.send_event", send_event
            ):
                command.execute(args)

                getenv_set.assert_called()
                send_event.assert_called_once_with(
                    datadog_api_key=FAKE_DD_KEY,
                    title="This is really important you gotta tell The Dog!!!",
                    text="",
                    tags={
                        "source": "infra-event-notifier",
                        "source_tool": "infra-event-notifier",
                        "source_category": "infra-tools",
                    },
                    alert_type="info",
                )
