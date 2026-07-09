import uuid

from typing import TYPE_CHECKING

from crm_epic_events.errors import CompanyAlreadyExistsError
from crm_epic_events.models import Company
from crm_epic_events.services.company.schemas import CompanyCreateInput, CompanyUpdateInput
from crm_epic_events.services.customer.schemas import CustomerCreateInput
from crm_epic_events.utils import db_transaction


if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class CompanyService:
    """
    Handles business logic for company lifecycle management.
    Permissions are managed in the controller.
    """

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
    def create(data: "CompanyCreateInput | CustomerCreateInput", db: "Session") -> "Company":
        """
        Creates a new company from either a direct creation input or a customer creation input.

        When called from ``CustomerService.create()``, uses ``data.company_name`` as the company name.

        Raises:
            CompanyAlreadyExistsError: If a company with the same VAT number already exists.
        """

        existing = Company.get_by_vat(data.vat_number, db)
        if existing:
            raise CompanyAlreadyExistsError()

        with db_transaction(db, "Creating company"):
            return Company.create(
                data.vat_number,
                data.name if isinstance(data, CompanyCreateInput) else data.company_name,
                db,
            )

    @staticmethod
    def update(
        target_company: "Company",
        data: "CompanyUpdateInput",
        db: "Session",
    ) -> "Company":
        with db_transaction(db, "Updating company"):
            return target_company.update(data, db)

    @staticmethod
    def delete(target_company: "Company", db: "Session") -> None:
        with db_transaction(db, "Deleting company"):
            target_company.delete(db)
