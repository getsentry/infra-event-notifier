import os
import pytest
from unittest.mock import MagicMock, patch

from infra_event_notifier.main import parse_args, parse_datadog


def _mock_getenv(key: str, default=None):
    if key in ("DATADOG_API_KEY", "DD_API_KEY"):
        return None
    return os.getenv(key, default)


class TestCLI:
    def test_parse_dryrun(self):
        examples = [
            ["-n", "datadog"],
            ["--dry-run", "datadog"],
            ["datadog", "-n"],
            ["datadog", "--dry-run"],
        ]
        for example in examples:
            args = parse_args(example)
            assert args.dry_run

    def test_parse_no_dryrun(self):
        example = ["datadog"]
        args = parse_args(example)
        assert not args.dry_run

    def test_parse_title(self):
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
            args = parse_args(example)
            assert (
                args.title
                == "Uh oh! Kafka cluster `antartica` turned into a fly!"
            )

    def test_parse_overall(self):
        example = [
            "datadog",
            "--title",
            "Actuated synergy manifest: xfn-enablement-layer",
            "--message",
            "Please refer to Bill's 82-slide presentation for details.",
            "--source=synergy-manifest-actuater",
        ]
        args = parse_args(example)
        assert args.title == "Actuated synergy manifest: xfn-enablement-layer"
        assert (
            args.message
            == "Please refer to Bill's 82-slide presentation for details."
        )
        assert args.source == "synergy-manifest-actuater"

    def test_parse_tags(self):
        example = [
            "datadog",
            "-t",
            "foo=bar",
            "--tag",
            "syns=acked",
            "--tag=body=ready",
        ]
        args = parse_args(example)
        assert "foo=bar" in args.tag
        assert "syns=acked" in args.tag
        assert "body=ready" in args.tag

    @patch("os.getenv", MagicMock(side_effect=_mock_getenv))
    def test_missing_datadog_key(self):
        example = [
            "datadog",
            "--title",
            "This is really important you gotta tell The Dog!!!",
        ]
        args = parse_args(example)

        with pytest.raises(ValueError):
            parse_datadog(args)
