import argparse
import os
import pprint
import sys
from typing import Any, TypeAlias

from infra_event_notifier.backends import datadog

Subparsers: TypeAlias = "argparse._SubParsersAction[argparse.ArgumentParser]"

DEFAULT_EVENT_SOURCE = "infra-event-notifier"


def add_dryrun(parser: argparse.ArgumentParser, submenu: bool) -> None:
    """
    Helper function to register a dry-run flag.

    We need this on submenus as well as the main parser becaausethe user can
    give the flag before or after the subcommand.
    """
    add_arg_kwargs: dict[str, Any] = {}
    if submenu:
        add_arg_kwargs["default"] = argparse.SUPPRESS
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Don't perform any action, just print what would have happened.",
        **add_arg_kwargs,
    )


def submenu_datadog(subparsers: Subparsers) -> None:
    dd_parser = subparsers.add_parser(
        "datadog", description="Log a generic event to Datadog"
    )
    dd_parser.add_argument("--title", type=str)
    dd_parser.add_argument("--message", type=str)
    dd_parser.add_argument("--source", type=str)
    dd_parser.add_argument(
        "--tag", "-t", type=str, help="format: -t tag=value", action="append"
    )
    add_dryrun(dd_parser, True)
    dd_parser.set_defaults(func=parse_datadog)


def submenu_datadog_terragrunt(subparsers: Subparsers) -> None:
    dd_terragrunt_parser = subparsers.add_parser("datadog-terragrunt")
    dd_terragrunt_parser.add_argument("--cli-args", type=str)
    add_dryrun(dd_terragrunt_parser, True)
    dd_terragrunt_parser.set_defaults(func=parse_datadog_terragrunt)


def parse_datadog(args: argparse.Namespace) -> None:
    """
    Parse CLI args for datadog subcommand and send the log.
    """
    title = args.title or ""
    message = args.message or ""
    arg_tags = args.tag or []

    if args.source is None or args.source == "":
        print(
            "WARNING: No source was set, using 'infra-event-notifier'. Please "
            "consider setting a more descriptive source!",
            file=sys.stderr,
        )
    source = args.source or DEFAULT_EVENT_SOURCE

    dd_api_key = os.getenv("DATADOG_API_KEY") or os.getenv("DD_API_KEY")
    if dd_api_key is None or dd_api_key == "":
        raise ValueError(
            "ERROR: You must provide a Datadog API key. Set "
            "environment variable DATADOG_API_KEY or DD_API_KEY."
        )

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

    if args.dry_run:
        print("Would admit the following event:")
        pprint.pp(send_kwargs)
    else:
        try:
            datadog.send_event(datadog_api_key=dd_api_key, **send_kwargs)
        except Exception as e:
            print("!! Could not report an event to DataDog:")
            print(e)


def parse_datadog_terragrunt(args: argparse.Namespace) -> None:
    pass


def main():
    parser = argparse.ArgumentParser(
        prog="infra-event-notifier",
        description="Sends notifications to Datadog. Slack support planned.",
        epilog="For more information, see "
        "https://github.com/getsentry/infra-event-notifier",
    )
    add_dryrun(parser, False)

    subparsers = parser.add_subparsers(help="sub-commands", required=True)
    submenu_datadog(subparsers)
    submenu_datadog_terragrunt(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
