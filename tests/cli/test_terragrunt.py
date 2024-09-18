import argparse
import pathlib
import pytest
from argparse import Namespace
from unittest.mock import MagicMock, patch

from infra_event_notifier.cli.terragrunt import (
    TerragruntCommand,
    RegionsConfig,
)

FAKE_DD_KEY = "I_AM_A_DATADOG_KEY"


class TestCLI:
    @pytest.fixture
    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(help="sub-commands", required=True)
        TerragruntCommand().submenu(subparsers)
        return parser

    @pytest.fixture
    def send_event(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def config_path(self, tmp_path: pathlib.Path) -> pathlib.Path:
        conf_path = tmp_path / "regions.json"
        conf_path.write_text(
            """
{
  "terragrunt_to_sentry_region": {
    "de": "de",
    "saas": "us",
    "us": "us"
  }
}
                        """
        )
        return conf_path

    @pytest.fixture
    def getenv_unset_key(self, config_path: pathlib.Path) -> MagicMock:
        def mock_getenv_unset_key(key: str, default=None) -> str | None:
            if key in ("DATADOG_API_KEY", "DD_API_KEY"):
                return default
            if key == "SENTRY_TERRAGRUNT_REGIONS_CONFIG":
                return str(config_path)
            return "DUMMY_VALUE"

        return MagicMock(side_effect=mock_getenv_unset_key)

    @pytest.fixture
    def getenv_set_key(self, config_path: pathlib.Path) -> MagicMock:
        def mock_getenv_set_key(key: str, default=None) -> str | None:
            if key in ("DATADOG_API_KEY", "DD_API_KEY"):
                return FAKE_DD_KEY
            if key == "SENTRY_TERRAGRUNT_REGIONS_CONFIG":
                return str(config_path)
            return "DUMMY_VALUE"

        return MagicMock(side_effect=mock_getenv_set_key)

    @pytest.fixture
    def getenv_unset_sentry_kube(self, config_path: pathlib.Path) -> MagicMock:
        def mock_getenv_set_key(key: str, default=None) -> str | None:
            if key in ("DATADOG_API_KEY", "DD_API_KEY"):
                return FAKE_DD_KEY
            if key == "SENTRY_TERRAGRUNT_REGIONS_CONFIG":
                return None
            return "DUMMY_VALUE"

        return MagicMock(side_effect=mock_getenv_set_key)

    def test_parse(self, parser: argparse.ArgumentParser):
        examples = [
            ["terragrunt", "--cli-args", "apply all"],
            ["terragrunt", "--cli-args=apply all"],
        ]

        for example in examples:
            args = parser.parse_args(example)
            assert args.cli_args == "apply all"

    def test_missing_datadog_key(self, getenv_unset_key: MagicMock):
        args = Namespace(cli_args="destroy-all", dry_run=None)
        command = TerragruntCommand()

        with patch("os.getenv", getenv_unset_key):
            with pytest.raises(ValueError):
                command._execute_impl(
                    args, cwd="terraform/gib-potato", user="bob"
                )

    def test_dry_run(self, getenv_set_key: MagicMock, send_event: MagicMock):
        args = Namespace(cli_args="apply all", dry_run=True)

        command = TerragruntCommand()
        with patch("os.getenv", getenv_set_key):
            with patch(
                "infra_event_notifier.backends.datadog.send_event", send_event
            ):
                command._execute_impl(
                    args, cwd="terraform/gib-potato", user="bob"
                )

                getenv_set_key.assert_called()
                send_event.assert_not_called()

    def test_load_config(self, getenv_set_key):
        with patch("os.getenv", getenv_set_key):
            config = RegionsConfig()
            assert config.terragrunt_to_sentry_region["saas"] == "us"
            assert config.terragrunt_to_sentry_region["us"] == "us"
            assert config.terragrunt_to_sentry_region["de"] == "de"

    def test_missing_config_throws(
        self, getenv_unset_sentry_kube: MagicMock, send_event: MagicMock
    ):
        args = Namespace(cli_args="run-all plan", dry_run=None)
        command = TerragruntCommand()
        with patch("os.getenv", getenv_unset_sentry_kube):
            with patch(
                "infra_event_notifier.backends.datadog.send_event", send_event
            ):
                with pytest.raises(ValueError):
                    command._execute_impl(
                        args, cwd="terraform/gib-potato", user="bob"
                    )

    def test_send(self, getenv_set_key: MagicMock, send_event: MagicMock):
        args = Namespace(cli_args="run-all plan", dry_run=None)
        command = TerragruntCommand()
        with patch("os.getenv", getenv_set_key):
            with patch(
                "infra_event_notifier.backends.datadog.send_event", send_event
            ):
                command._execute_impl(
                    args, cwd="terraform/gib-potato", user="bob"
                )

                getenv_set_key.assert_called()
                send_event.assert_called_once_with(
                    datadog_api_key=FAKE_DD_KEY,
                    title=(
                        "terragrunt: Ran 'run-all plan' for slice "
                        "'gib-potato' in region 'us'"
                    ),
                    text=(
                        "%%%\nUser **bob** ran terragrunt 'run-all plan' for "
                        "slice: **gib-potato**\n%%%"
                    ),
                    tags={
                        "source": "terragrunt",
                        "source_tool": "terragrunt",
                        "source_category": "infra-tools",
                        "sentry_user": "bob",
                        "sentry_region": "us",
                        "terragrunt_root": "terraform",
                        "terragrunt_slice": "gib-potato",
                        "terragrunt_cli_args": "run-all plan",
                    },
                    alert_type="info",
                )
