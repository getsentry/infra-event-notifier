import argparse
import functools
import sys
import os
import pprint
import getpass
from dataclasses import dataclass
from typing import Mapping, Any

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from yaml import SafeLoader, load
from infra_event_notifier.cli.command import (
    BaseCommand,
    Subparsers,
    add_dryrun,
)
from infra_event_notifier.backends import datadog

TERRAGRUNT_EVENT_SOURCE = "terragrunt"


class SentryKubeConfig:
    """
    In order to properly log Terragrunt events, we need some config from
    sentry-kube. But we don't want to install sentry-kube and its 1 million
    dependencies. This represents a simplified model of that config. For full
    details, see repo getsentry/sentry-infra-tools path
    libsentrykube/config.py.
    """

    def __init__(self) -> None:
        config_file_name = os.getenv(
            "SENTRY_KUBE_CONFIG_FILE", "cli_config/configuration.yaml"
        )

        with open(config_file_name) as file:
            configuration = load(file, Loader=SafeLoader)
            assert (
                "silo_regions" in configuration
            ), "silo_regions entry not present in the config"
            silo_regions = {
                name: SiloRegion.from_conf(conf)
                for name, conf in configuration["silo_regions"].items()
            }

        self.silo_regions: Mapping[str, SiloRegion] = silo_regions


@dataclass(frozen=True)
class SiloRegion:
    sentry_region: str

    @classmethod
    def from_conf(cls, silo_regions_conf: Mapping[str, Any]) -> Self:
        return cls(
            sentry_region=silo_regions_conf.get("sentry_region", "unknown")
        )


class TerragruntCommand(BaseCommand):

    @functools.cache
    def _load_ops_config(self): ...

    @classmethod
    @override
    def name(cls) -> str:
        return "terragrunt"

    @classmethod
    @override
    def description(cls) -> str:
        return "Parses arguments provided by Terragrunt hook"

    @override
    def submenu(self, subparsers: Subparsers) -> argparse.ArgumentParser:
        parser = super().submenu(subparsers)
        parser.add_argument("--cli-args", type=str)
        add_dryrun(parser, True)

        return parser

    @override
    def execute(self, args: argparse.Namespace) -> None:
        self._execute_impl(args)

    # Separation for unit testing. This preserves the execute() function
    # signature while enabling dependency injection for testing.
    def _execute_impl(
        self, args: argparse.Namespace, cwd=os.getcwd(), user=getpass.getuser()
    ) -> None:
        cli_args = args.cli_args

        # Find our slice under terragrunt/terraform
        if "terraform/" in cwd:
            tgroot = "terraform"
            tgslice = cwd.split("terraform/")[1]
            region = "saas"
        elif "terragrunt/" in cwd:
            tgroot = "terragrunt"
            tgslice = cwd.split("terragrunt/")[1].split("/.terragrunt-cache/")[
                0
            ]
            region = tgslice.split("/")[-1]
        else:
            print(repr(cwd))
            raise RuntimeError(
                "Unable to determine what slice you're running in."
            )

        sentry_region = SentryKubeConfig().silo_regions[region].sentry_region

        tags = {
            "source": TERRAGRUNT_EVENT_SOURCE,
            "source_tool": TERRAGRUNT_EVENT_SOURCE,
            "source_category": datadog.DEFAULT_EVENT_SOURCE_CATEGORY,
            "sentry_user": user,
            "sentry_region": sentry_region,
            "terragrunt_root": tgroot,
            "terragrunt_slice": tgslice,
            "terragrunt_cli_args": cli_args,
        }

        send_kwargs: dict[str, Any] = {
            "title": (
                f"terragrunt: Ran '{cli_args}' for slice '{tgslice}' "
                f"in region '{sentry_region}'"
            ),
            "text": datadog.markdown_text(
                f"User **{user}** ran terragrunt '{cli_args}' for slice: "
                f"**{tgslice}**"
            ),
            "tags": tags,
            "alert_type": "info",
        }
        api_key = datadog.api_key_from_env()

        if args.dry_run:
            print("Would admit the following event:")
            pprint.pp(send_kwargs)
        else:
            try:
                datadog.send_event(datadog_api_key=api_key, **send_kwargs)
            except Exception as e:
                print("!! Could not report an event to DataDog:")
                print(e)
