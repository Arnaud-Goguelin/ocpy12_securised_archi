class CustomPermissionError(Exception):
    def __init__(self, message: str = "Permission error.", status_code: int = 403):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class UserNotAllowedError(CustomPermissionError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "User not allowed to perform this action.")
        super().__init__(**kwargs)


class UserIsNotOwnerError(CustomPermissionError):
    def __init__(self, **kwargs):
        kwargs.setdefault("message", "User is not the owner of this object.")
        super().__init__(**kwargs)
