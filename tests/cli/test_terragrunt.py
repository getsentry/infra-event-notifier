import argparse
import pathlib
import pytest
from argparse import Namespace
from unittest.mock import MagicMock, patch

from infra_event_notifier.cli.terragrunt import (
    TerragruntCommand,
    SentryKubeConfig,
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
        conf_path = tmp_path / "configuration.yaml"
        conf_path.write_text(
            """
silo_regions:
  saas:
    bastion:
      spawner_endpoint: https://localhost:12345
      site: some_saas
    k8s:
      root: k8s
      cluster_def_root: clusters/us
      materialized_manifests: materialized_manifests/us
    sentry_region: us
    service_monitors: {
      getsentry: [ 123456789 ]
    }
                        """
        )
        return conf_path

    @pytest.fixture
    def getenv_unset_key(self, config_path: pathlib.Path) -> MagicMock:
        def mock_getenv_unset_key(key: str, default=None) -> str | None:
            if key in ("DATADOG_API_KEY", "DD_API_KEY"):
                return default
            if key == "SENTRY_KUBE_CONFIG_FILE":
                return str(config_path)
            return "DUMMY_VALUE"

        return MagicMock(side_effect=mock_getenv_unset_key)

    @pytest.fixture
    def getenv_set_key(self, config_path: pathlib.Path) -> MagicMock:
        def mock_getenv_set_key(key: str, default=None) -> str | None:
            print(f"I am mocked: {key}")
            if key in ("DATADOG_API_KEY", "DD_API_KEY"):
                return FAKE_DD_KEY
            if key == "SENTRY_KUBE_CONFIG_FILE":
                return str(config_path)
            return "DUMMY_VALUE"

        return MagicMock(side_effect=mock_getenv_set_key)

    @pytest.fixture
    def getenv_unset_sentry_kube(self, config_path: pathlib.Path) -> MagicMock:
        def mock_getenv_set_key(key: str, default=None) -> str | None:
            print(f"I am mocked: {key}")
            if key in ("DATADOG_API_KEY", "DD_API_KEY"):
                return FAKE_DD_KEY
            if key == "SENTRY_KUBE_CONFIG_FILE":
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
            config = SentryKubeConfig()
            assert config.silo_regions["saas"].sentry_region == "us"

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
