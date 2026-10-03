class DomainException(Exception):
    """Базовое доменное исключение сервиса аутентификаций."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)