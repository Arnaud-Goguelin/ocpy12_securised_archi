import time

from .constants import GenericMessages


def countdown(message: GenericMessages):
    """
    Counts down from 3 to 0, displaying a message before each number.
    """
    for i in range(3, -1, -1):
        print(f"\r{message.value}{i}", end="", flush=True)
        time.sleep(1)
    print("\n")
    return None
