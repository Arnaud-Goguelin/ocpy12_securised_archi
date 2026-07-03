import uuid

from typing import TYPE_CHECKING

from customer.schemas import CustomerCreateInput

from crm_epic_events.errors import UserNotAllowedError
from crm_epic_events.models import Company
from crm_epic_events.utils import Roles, db_transaction


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from crm_epic_events.models import User
    from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput


class CompanyService:
    @staticmethod
    def get_all(db: "Session") -> list["Company"]:
        return Company.get_all(db)

    @staticmethod
    def get_by_customers_salesperson(current_user_id: uuid.UUID, db: "Session") -> list["Company"]:
        return Company.get_by_customers_salesperson(current_user_id, db)

    @staticmethod
    def get_by_vat(vat_number: str, db: "Session") -> "Company | None":
        return Company.get_by_vat(vat_number, db)

    @staticmethod
    def create(current_user: "User", data: "CompanyCreateInput | CustomerCreateInput", db: "Session") -> "Company":
        """MANAGER and SALES can create a company."""
        if current_user.role not in (Roles.MANAGER, Roles.SALES):
            raise UserNotAllowedError()

        existing = Company.get_by_vat(data.vat_number, db)
        if existing:
            raise ValueError(f"Company with VAT '{data.vat_number}' already exists.")

        with db_transaction(db, "Creating company"):
            return Company.create(data.vat_number, data.name, db)

    @staticmethod
    def update(
        current_user: "User",
        target_company: "Company",
        data: "CompanyUpdateInput",
        db: "Session",
    ) -> "Company":
        """MANAGER and SALES can update a company."""
        if current_user.role not in (Roles.MANAGER, Roles.SALES):
            raise UserNotAllowedError()

        with db_transaction(db, "Updating company"):
            return target_company.update(data, db)

    @staticmethod
    def delete(current_user: "User", target_company: "Company", db: "Session") -> None:
        """Only MANAGER can delete a company."""
        if current_user.role != Roles.MANAGER:
            raise UserNotAllowedError()

        with db_transaction(db, "Deleting company"):
            target_company.delete(db)
