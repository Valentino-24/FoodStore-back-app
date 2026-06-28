class AppException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotFoundError(AppException):
    def __init__(self, resource: str, identifier: int | str):
        super().__init__(
            message=f"{resource} con id={identifier} no encontrado",
            status_code=404
        )


class BusinessRuleError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)


class AuthorizationError(AppException):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message=message, status_code=403)
