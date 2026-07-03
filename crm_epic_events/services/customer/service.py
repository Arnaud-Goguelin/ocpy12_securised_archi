# crm_epic_events/services/customer/service.py
from typing import TYPE_CHECKING

from crm_epic_events.models import Customer
from crm_epic_events.utils import Roles, db_transaction
from crm_epic_events.errors import UserIsNotOwnerError, UserNotAllowedError

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from crm_epic_events.models import User
    from crm_epic_events.services.customer.schemas import CustomerCreateInput, CustomerUpdateInput


class CustomerService:

    @staticmethod
    def get_all(db: "Session") -> list["Customer"]:
        return Customer.get_all(db)

    @staticmethod
    def get_all_by_salesperson(salesperson: "User", db: "Session") -> list["Customer"]:
        return Customer.get_all_by_salesperson(salesperson.id, db)

    @staticmethod
    def create(current_user: "User", data: "CustomerCreateInput", db: "Session") -> "Customer":
        """
        Only SALES members can create a customer.
        The customer is automatically assigned to the creating salesperson.
        """
        if current_user.role != Roles.SALES:
            raise UserNotAllowedError()

        with db_transaction(db, "Creating customer"):
            return Customer.create(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                phone=data.phone,
                company_name=data.company_name,
                salesperson_id=current_user.id,
                db=db,
            )

    @staticmethod
    def update(
        current_user: "User",
        target_customer: "Customer",
        data: "CustomerUpdateInput",
        db: "Session",
    ) -> "Customer":
        """
        MANAGER can update any customer.
        SALES can only update their own customers.
        """
        is_manager = current_user.role == Roles.MANAGER
        is_owner = target_customer.salesperson_id == current_user.id

        if not is_manager and not is_owner:
            raise UserIsNotOwnerError()

        with db_transaction(db, "Updating customer"):
            return target_customer.update(data, db)

    @staticmethod
    def delete(current_user: "User", target_customer: "Customer", db: "Session") -> None:
        """Only MANAGER can delete a customer."""
        if current_user.role != Roles.MANAGER:
            raise UserNotAllowedError()

        with db_transaction(db, "Deleting customer"):
            target_customer.delete(db)
