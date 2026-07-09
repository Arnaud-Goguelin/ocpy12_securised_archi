import uuid

from decimal import Decimal

from pydantic import BaseModel, model_validator


class ContractCreateInput(BaseModel):
    """
    Input schema for creating a new contract.

    Validates that `remaining_amount` does not exceed `total_amount`.
    The salesperson is inherited from the linked customer, not chosen freely.
    Used in: ``ContractService.create()``.
    """

    salesperson_id: uuid.UUID
    customer_id: uuid.UUID
    total_amount: Decimal
    remaining_amount: Decimal
    status: bool = False

    @model_validator(mode="after")
    def remaining_not_greater_than_total(self) -> "ContractCreateInput":
        if (
            self.total_amount is not None
            and self.remaining_amount is not None
            and self.remaining_amount > self.total_amount
        ):
            raise ValueError("remaining_amount cannot be greater than total_amount.")
        return self


class ContractUpdateInput(BaseModel):
    """
    Input schema for partially updating an existing contract.

    All fields are optional; only provided fields are applied.
    Cross-field validation ensures `remaining_amount` never exceeds `total_amount` when both are provided.
    Used in: ``ContractService.update()``.
    """

    total_amount: Decimal | None = None
    remaining_amount: Decimal | None = None
    status: bool | None = None

    @model_validator(mode="after")
    def remaining_not_greater_than_total(self) -> "ContractUpdateInput":
        if (
            self.total_amount is not None
            and self.remaining_amount is not None
            and self.remaining_amount > self.total_amount
        ):
            raise ValueError("remaining_amount cannot be greater than total_amount.")
        return self
