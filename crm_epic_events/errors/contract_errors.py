class CustomContractError(Exception):
    def __init__(self, message: str = "Contract error.", status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class ContractAmountError(CustomContractError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "Remaining amount cannot be greater than total amount.")
        super().__init__(**kwargs)


class ContractNotSignedError(CustomContractError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "Cannot create an event for an unsigned contract.")
        super().__init__(**kwargs)


class ContractNotFoundError(CustomContractError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "Contract not found.")
        super().__init__(**kwargs)
