import argparse
import functools
import getpass
import json
import os
import pprint
import sys
from typing import Any

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from infra_event_notifier.cli.command import (
    BaseCommand,
    Subparsers,
    add_dryrun,
)
from infra_event_notifier.backends import datadog

TERRAGRUNT_EVENT_SOURCE = "terragrunt"


class RegionsConfig:
    """
    In order to properly log Terragrunt events, we need to map the region from
    the name of the slice to a Sentry region name. We use a config file sotred
    in ops/ for this.
    """

    def __init__(self, config_file: str) -> None:
        with open(config_file) as file:
            configuration = json.load(file)
            assert (
                "terragrunt_to_sentry_region" in configuration.keys()
            ), "terragrunt_to_sentry_region entry not present in the config"
            self.terragrunt_to_sentry_region: dict[str, str] = configuration[
                "terragrunt_to_sentry_region"
            ]


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
        parser.add_argument("--cli-args", type=str, required=True)
        parser.add_argument("--region-map", type=str, required=True)
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
        region_map = args.region_map

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
            raise RuntimeError(
                "Unable to determine what slice you're running in."
            )

        sentry_region = RegionsConfig(region_map).terragrunt_to_sentry_region[
            region
        ]

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
