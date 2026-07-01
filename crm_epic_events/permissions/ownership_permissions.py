import functools

from collections.abc import Callable
from typing import TYPE_CHECKING

from crm_epic_events.errors import UserIsNotOwnerError
from crm_epic_events.utils.constants import Roles


if TYPE_CHECKING:
    from crm_epic_events.models import User


def require_ownership(current_user: "User", owner: "User | None") -> Callable:
    """
    Decorator that checks ownership for a controller method.
    MANAGER bypasses the ownership check entirely.
    If owner or current_user is None, the check is skipped — the controller has the responsibility
    to validate object existence and raise the proper error beforehand.
    If the current user is not the owner, an UserIsNotOwnerError is raised.

    Args:
        current_user: The User instance of the current user.
        owner: The User instance that owns the object (e.g. customer.sales_contact).

    Usage:
        @require_ownership(
            current_user=self.user,
            owner=customer.sales_contact,
        )
        def handle_update_customer(self):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # obviously if owner or current_user are None, we can't check ownership either
            # controller has the responsibility to check this
            # (for current_user, it is normally done in main
            # controller with auth check)
            if not current_user:
                return None
            # MANAGER bypasses ownership check
            if current_user.role != Roles.MANAGER:
                if not owner:
                    return None
                if owner != current_user:
                    raise UserIsNotOwnerError()

            return func(*args, **kwargs)

        return wrapper

    return decorator
