class CustomCompanyError(Exception):
    def __init__(self, message: str = "Company error.", status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class CompanyAlreadyExistsError(CustomCompanyError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "A company with this VAT number already exists.")
        super().__init__(**kwargs)
