import functools

from collections.abc import Callable
from typing import TYPE_CHECKING

from crm_epic_events.errors import UserNotAllowedError


if TYPE_CHECKING:
    from crm_epic_events.utils.constants import Roles


def require_roles(*allowed_roles: "Roles") -> Callable:
    """
    Decorator that restricts access to a controller method based on the current user's role.

    The decorated method must belong to a class with a `self.user` attribute (User model instance).
    If the user's role is not in `allowed_roles`, a custom error UserNotAllowedError is raised.

    Usage:
        @require_roles(Roles.MANAGER, Roles.SALES)
        def handle_create_customer(self):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.user is None or self.user.role not in allowed_roles:
                raise UserNotAllowedError()
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
