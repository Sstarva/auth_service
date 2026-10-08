from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для управления сущностью пользователя (User)."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=User, session=session)

    async def get_by_email(self, email: str) -> User | None:
        """Поиск пользователя по точному совпадению email (в нижнем регистре)."""
        stmt = select(User).where(User.email == email.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Поиск пользователя по username."""
        stmt = select(User).where(User.username == username.strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, identifier: str) -> User | None:
        """Универсальный поиск для логина (по логину или email)."""
        clean_identifier = identifier.strip()
        stmt = select(User).where(
            or_(
                User.email == clean_identifier.lower(),
                User.username == clean_identifier,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email_or_username(self, email: str, username: str) -> tuple[bool, bool]:
        """
        Проверка занятости email и username одним запросом при регистрации.
        Возвращает кортеж: (email_exists, username_exists).
        """
        stmt = select(User.email, User.username).where(
            or_(
                User.email == email.strip().lower(),
                User.username == username.strip(),
            )
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        email_exists = any(r[0] == email.strip().lower() for r in rows)
        username_exists = any(r[1] == username.strip() for r in rows)
        return email_exists, username_exists

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        username: str,
        **extra_fields: Any,
    ) -> User:
        """Фабричный метод создания и сохранения пользователя в транзакции."""
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            username=username.strip(),
            **extra_fields,
        )
        return await self.add(user)

    async def update_last_login(self, user_id: UUID) -> None:
        """Обновление времени последнего входа."""
        from sqlalchemy import func
        await self.update(user_id, last_login_at=func.now())