class CustomUserError(Exception):
    def __init__(self, message: str = "User error.", status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class UserAlreadyExistsError(CustomUserError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "A user with this email already exists.")
        super().__init__(**kwargs)


class PasswordNotSecuredError(CustomUserError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "Password is not secure.")
        super().__init__(**kwargs)
