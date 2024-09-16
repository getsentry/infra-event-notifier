import argparse

from infra_event_notifier.cli.datadog import DatadogCommand
from infra_event_notifier.cli.terragrunt import TerragruntCommand
from infra_event_notifier.cli.command import BaseCommand, add_dryrun


def parse_args(
    argv=None, commands: list[BaseCommand] | None = None
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="infra-event-notifier",
        description="Sends notifications to Datadog. Slack support planned.",
        epilog="For more information, see "
        "https://github.com/getsentry/infra-event-notifier",
    )
    add_dryrun(parser, False)

    subparsers = parser.add_subparsers(help="sub-commands", required=True)

    for command in [DatadogCommand(), TerragruntCommand()]:
        command.submenu(subparsers)

    return parser.parse_args(argv)


def main():
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
