import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Базовые атрибуты пользователя."""

    email: EmailStr
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Уникальный логин (латиница, цифры, _, -)",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        clean = value.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", clean):
            raise ValueError(
                "Username может содержать только латинские буквы, цифры, дефис и подчеркивание"
            )
        return clean

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserCreate(UserBase):
    """Схема создания пользователя (регистрация)."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль пользователя",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(c.isdigit() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not any(c.isalpha() for c in value):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return value


class UserUpdate(BaseModel):
    """Схема обновления данных профиля."""

    username: str | None = Field(default=None, min_length=3, max_length=30)
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def validate_opt_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        clean = value.strip()
        if not re.match(r"^[a-zA-Z0-9_-]+$", clean):
            raise ValueError("Username содержит недопустимые символы")
        return clean


class UserRead(UserBase):
    """Схема отдачи данных пользователя клиенту."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    last_login_at: datetime | None = None