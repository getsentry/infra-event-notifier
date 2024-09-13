import argparse
import os
import pytest
from argparse import Namespace
from unittest.mock import MagicMock, patch

from infra_event_notifier.cli.datadog import DatadogCommand


def _mock_getenv(key: str, default=None):
    if key in ("DATADOG_API_KEY", "DD_API_KEY"):
        return None
    return os.getenv(key, default)


class TestCLI:
    @pytest.fixture
    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help="sub-commands", required=True)
        DatadogCommand().submenu(subparsers)
        return parser

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

    @patch("os.getenv", MagicMock(side_effect=_mock_getenv))
    def test_missing_datadog_key(self):
        args = Namespace(
            title="This is really important you gotta tell The Dog!!!",
            message=None,
            source=None,
            tag=None,
        )
        command = DatadogCommand()

        with pytest.raises(ValueError):
            command.execute(args)
