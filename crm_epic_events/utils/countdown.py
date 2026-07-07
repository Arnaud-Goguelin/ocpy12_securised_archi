import time

from .constants import GenericMessages


def countdown(message: GenericMessages, timer: int = 3):
    """
    Counts down from 3 to 0, displaying a message before each number.
    """
    for i in range(timer, -1, -1):
        print(f"\r{message.value}{i}", end="", flush=True)
        time.sleep(1)
    print("\n")
    return None
