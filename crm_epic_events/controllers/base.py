from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from crm_epic_events.errors import UserIsNotOwnerError
from crm_epic_events.permissions import Roles
from crm_epic_events.utils.constants import MenuItem


if TYPE_CHECKING:
    from crm_epic_events.models.user import User


class BaseController:
    """Shared base for all controllers, providing menu filtering and ownership enforcement."""

    db: "Session"
    user: "User | None"
    menu_items: list[MenuItem]

    @property
    def visible_menu_items(self) -> list[MenuItem]:
        """Returns only the menu items the current user's role is allowed to see."""

        if not self.user:
            return []
        return [item for item in self.menu_items if self.user.role in item.roles_allowed]

    def check_ownership(self, owner: "User | None") -> None:
        """
        Enforces that the current user owns the target resource. MANAGER bypasses this check.

        Raises:
            UserIsNotOwnerError: If the current user is not the owner of the target resource.
        """

        if self.user.role == Roles.MANAGER:
            return
        if not owner or owner.id != self.user.id:
            raise UserIsNotOwnerError()
