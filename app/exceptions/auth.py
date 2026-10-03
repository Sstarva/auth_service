from app.exceptions.base import DomainException


class UserAlreadyExistError(DomainException):
    def __init__(self, message: str = "Пользователь с таким email или username уже существует"):
        super().__init__(message=message, code="USER_ALREADY_EXIST")

class InvalidCredentialsError(DomainException):
    def __init__(self, message: str = "Неверный email или пароль"):
        super().__init__(message=message, code="INVALID_CREDENTIALS")


class TokenInvalidError(DomainException):
    def __init__(self, message: str = "Токен недействителен или поврежден"):
        super().__init__(message=message, code="TOKEN_INVALID")


class TokenRevokedError(DomainException):
    def __init__(self, message: str = "Токен был отозван"):
        super().__init__(message=message, code="TOKEN_REVOKED")