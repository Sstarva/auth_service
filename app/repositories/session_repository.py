from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import UserSession
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[UserSession]):
    """Репозиторий для управления сессиями пользователей и refresh-токенами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=UserSession, session=session)

    async def get_by_jti(self, jti: str) -> UserSession | None:
        """Поиск сессии по уникальному JTI токена."""
        stmt = select(UserSession).where(UserSession.refresh_token_jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_jti(self, jti: str) -> UserSession | None:
        """Поиск не отозванной сессии с проверкой срока жизни."""
        stmt = select(UserSession).where(
            UserSession.refresh_token_jti == jti,
            UserSession.is_revoked.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_sessions_by_user_id(self, user_id: UUID) -> list[UserSession]:
        """Получить все активные устройства/сессии пользователя."""
        stmt = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_revoked.is_(False),
            )
            .order_by(UserSession.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_session(
        self,
        user_id: UUID,
        refresh_token_jti: str,
        expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
        device_name: str | None = None,
    ) -> UserSession:
        """Создание новой пользовательской сессии."""
        new_session = UserSession(
            user_id=user_id,
            refresh_token_jti=refresh_token_jti,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            device_name=device_name,
            is_revoked=False,
        )
        return await self.add(new_session)

    async def revoke_by_jti(self, jti: str) -> bool:
        """Отзыв сессии по JTI (например, при обычном logout или ротации токена)."""
        stmt = (
            update(UserSession)
            .where(UserSession.refresh_token_jti == jti, UserSession.is_revoked.is_(False))
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def revoke_all_user_sessions(self, user_id: UUID, except_jti: str | None = None) -> int:
        """
        Отзыв всех сессий пользователя (например, при смене пароля или взломе).
        Опционально можно оставить текущую сессию активной (except_jti).
        """
        stmt = update(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_revoked.is_(False),
        )
        if except_jti:
            stmt = stmt.where(UserSession.refresh_token_jti != except_jti)

        stmt = stmt.values(is_revoked=True)
        result = await self.session.execute(stmt)
        return result.rowcount