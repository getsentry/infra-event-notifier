import argparse
from abc import ABC, abstractmethod
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
        help=(
            "Don't perform any action, just print what would have happened."
        ),
        **add_arg_kwargs,
    )


class BaseCommand(ABC):

    @classmethod
    @abstractmethod
    def name(cls) -> str: ...

    @classmethod
    @abstractmethod
    def description(cls) -> str: ...

    def submenu(self, subparsers: Subparsers) -> argparse.ArgumentParser:
        parser = subparsers.add_parser(
            self.name(), description=self.description()
        )
        parser.set_defaults(func=self.execute)
        return parser

    @abstractmethod
    def execute(self, args: argparse.Namespace) -> None: ...
