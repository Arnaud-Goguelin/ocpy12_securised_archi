from typing import TYPE_CHECKING

from crm_epic_events.models import Customer
from crm_epic_events.services.company.service import CompanyService
from crm_epic_events.utils import db_transaction


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

        # Auto-create company if not found — stays in the same transaction
        company = CompanyService.get_by_vat(data.company_vat, db)
        if not company:
            company = CompanyService.create(current_user, data, db)

        with db_transaction(db, "Creating customer"):
            return Customer.create(
                salesperson_id=current_user.id,
                company_vat=company.vat_number,
                email=data.email,
                first_name=data.first_name,
                last_name=data.last_name,
                phone=data.phone,
                db=db,
            )

    @staticmethod
    def update(
        target_customer: "Customer",
        data: "CustomerUpdateInput",
        db: "Session",
    ) -> "Customer":
        with db_transaction(db, "Updating customer"):
            return target_customer.update(data, db)

    @staticmethod
    def delete(target_customer: "Customer", db: "Session") -> None:
        company_vat = target_customer.company_vat
        with db_transaction(db, "Deleting customer"):
            target_customer.delete(db)
            remaining = Customer.get_all_by_company_vat(company_vat, db)
            if not remaining:
                target_customer.company.delete_by_vat(company_vat, db)
