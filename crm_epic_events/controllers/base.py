from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from crm_epic_events.errors import UserIsNotOwnerError
from crm_epic_events.permissions import Roles
from crm_epic_events.utils.constants import MenuItem


if TYPE_CHECKING:
    from crm_epic_events.models.user import User


class BaseController:
    db: "Session"
    user: "User | None"
    menu_items: list[MenuItem]

    @property
    def visible_menu_items(self) -> list[MenuItem]:
        if not self.user:
            return []
        return [item for item in self.menu_items if self.user.role in item.roles_allowed]

    def check_ownership(self, owner: "User | None") -> None:
        """Raises UserIsNotOwnerError if current user is not owner. MANAGER bypasses."""
        if self.user.role == Roles.MANAGER:
            return
        if not owner or owner.id != self.user.id:
            raise UserIsNotOwnerError()
