from uuid import UUID
from pydantic import BaseModel, Field


class TokenPairResponse(BaseModel):
    """Формат успешного ответа с парой токенов"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Время жизни Access-токена в секундах")


class TokenPayload(BaseModel):
    """Внутренний пейлоад, декодируемый из JWT Access-токена."""

    sub: UUID = Field(description="User ID")
    jti: str = Field(description="Уникальный идентификатор токена")
    exp: int = Field(description="Время истечения токена (Unix timestamp)")
    type: str = "access"