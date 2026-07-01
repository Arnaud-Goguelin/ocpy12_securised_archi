from typing import TYPE_CHECKING

from colorama import Fore, Style

from .constants import GenericMessages
from .countdown import countdown


if TYPE_CHECKING:
    from pydantic import ValidationError


def colored(text: str, color: str) -> str:
    """Wraps text with a colorama color and resets after."""
    return f"{color}{text}{Style.RESET_ALL}"


def print_title(title: str) -> None:
    separator = colored("=" * len(title), Fore.GREEN)
    print(f"\n{separator}\n{title}\n{separator}\n")


def print_option(key: str, label: str) -> None:
    print(f"  {colored(key, Fore.LIGHTYELLOW_EX)}. {label}")


def print_info(text: str) -> None:
    print(colored(text, Fore.CYAN))


def print_error(text: str) -> None:
    print(colored(text, Fore.RED))


def print_validation_errors(validation_error: "ValidationError") -> None:
    """Prints only the human-readable messages from a Pydantic ValidationError."""
    for error in validation_error.errors():
        field = error["loc"][0] if error["loc"] else "input"
        message = error["msg"].replace("Value error, ", "")
        print_error(f"  {field}: {message}")


def print_unexpected_error(error: str, generic_messages: GenericMessages) -> None:
    print(colored("An error occurred:", Fore.RED))
    print(error)
    countdown(generic_messages)


def print_success(text: str) -> None:
    print(colored(text, Fore.GREEN))


def prompt(label: str) -> str:
    return input(f"{colored(label, Fore.LIGHTYELLOW_EX)}: ")
