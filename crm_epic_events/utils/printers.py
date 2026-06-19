from colorama import Fore, Style


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


def print_success(text: str) -> None:
    print(colored(text, Fore.GREEN))


def prompt(label: str) -> str:
    return input(f"{colored(label, Fore.LIGHTYELLOW_EX)}: ")
