import argparse
import sys
import pprint
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

DEFAULT_EVENT_SOURCE = "infra-event-notifier"


class DatadogCommand(BaseCommand):
    @classmethod
    @override
    def name(cls) -> str:
        return "datadog"

    @classmethod
    @override
    def description(cls) -> str:
        return "Log a generic event to Datadog"

    @override
    def submenu(self, subparsers: Subparsers) -> argparse.ArgumentParser:
        parser = super().submenu(subparsers)
        parser.add_argument("--title", type=str)
        parser.add_argument("--message", type=str)
        parser.add_argument("--source", type=str)
        parser.add_argument(
            "--tag",
            "-t",
            type=str,
            help="format: -t tag=value",
            action="append",
        )
        add_dryrun(parser, True)

        return parser

    @override
    def execute(self, args: argparse.Namespace) -> None:
        """
        Parse CLI args for datadog subcommand and send the log.
        """
        title = args.title or ""
        message = args.message or ""
        arg_tags = args.tag or []

        if args.source is None or args.source == "":
            print(
                f"WARNING: No source was set, using '{DEFAULT_EVENT_SOURCE}'. "
                "Please consider setting a more descriptive source!",
                file=sys.stderr,
            )
        source = args.source or DEFAULT_EVENT_SOURCE

        tags = {
            "source": source,
            "source_tool": source,
            "source_category": datadog.DEFAULT_EVENT_SOURCE_CATEGORY,
        }
        try:
            custom_tags = dict([tag.split("=") for tag in arg_tags])
            tags.update(custom_tags)
        except Exception as e:
            raise ValueError(
                "Tag format incorrect use -t tag=value ex:( -t user=$USER ) "
                f"\nERROR: \n {e}"
            )

        send_kwargs: dict[str, Any] = {
            "title": title,
            "text": message,
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
