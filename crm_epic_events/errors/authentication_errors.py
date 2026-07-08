class CustomAuthenticationError(Exception):
    def __init__(self, message: str = "Authentication error.", status_code: int = 401):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class CustomInvalidCredentialsError(CustomAuthenticationError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "Invalid credentials")
        super().__init__(**kwargs)


class CustomInvalidTokenError(CustomAuthenticationError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "Invalid token")
        super().__init__(**kwargs)


class UserNotAuthenticatedError(CustomAuthenticationError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "You must be logged in to perform this action.")
        super().__init__(**kwargs)
