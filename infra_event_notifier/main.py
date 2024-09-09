import argparse
from typing import Any, TypeAlias

Subparsers: TypeAlias = "argparse._SubParsersAction[argparse.ArgumentParser]"


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
    pass


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
