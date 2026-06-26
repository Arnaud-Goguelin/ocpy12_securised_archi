from .constants import GenericMessages
from .printers import print_info


def exit_app():
    print_info(GenericMessages.EXIT)
    exit(0)
