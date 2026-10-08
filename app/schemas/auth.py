from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Запрос на вход по логину или email."""
    identifier: str = Field(
        ...,
        description="Email или username пользователя",
        examples=["player_one@starva.io", "player_one"],
    )
    password: str = Field(..., description="Пароль пользователя")
    device_name: str | None = Field(
        default=None,
        description="Имя устройства клиента (например, 'Chrome on Windows', 'iPhone 15')",
    )


class RefreshTokenRequest(BaseModel):
    """Запрос на ротацию пары токенов."""
    refresh_token: str = Field(..., description="Текущий refresh-токен")


class LogoutRequest(BaseModel):
    """Запрос на выход из конкретной сессии."""
    refresh_token: str | None = Field(
        default=None,
        description="Refresh-токен для отзыва (если не передан в cookies/заголовке)",
    )


class ChangePasswordRequest(BaseModel):
    """Запрос на смену пароля."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    revoke_other_sessions: bool = Field(
        default=True,
        description="Завершить ли все остальные активные сессии на других устройствах",
    )


class SessionRead(BaseModel):
    """Схема отображения активной сессии устройства."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    device_name: str | None
    ip_address: str | None
    created_at: datetime
    expires_at: datetime