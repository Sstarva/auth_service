from datetime import datetime, timezone
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import OutboxMessage, OutboxStatus
from app.repositories.base import BaseRepository


class OutboxRepository(BaseRepository[OutboxMessage]):
    """Репозиторий для паттерна Transactional Outbox."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(model=OutboxMessage, session=session)

    async def create_event(
        self,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str | UUID,
        payload: dict[str, Any],
    ) -> OutboxMessage:
        """
        Создать событие в контексте текущей транзакции.
        Метод использует add(), поэтому сохраняется атомарно вместе с основной сущностью.
        """
        message = OutboxMessage(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=payload,
            status=OutboxStatus.PENDING,
            retry_count=0,
        )
        return await self.add(message)

    async def get_pending_messages(self, limit: int = 50) -> Sequence[OutboxMessage]:
        """
        Выборка неотправленных сообщений для фонового воркера.
        Использует 'SKIP LOCKED', чтобы несколько релеев не конфликтовали за одни записи.
        """
        stmt = (
            select(OutboxMessage)
            .where(OutboxMessage.status == OutboxStatus.PENDING)
            .order_by(OutboxMessage.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_as_processed(self, message_id: UUID) -> None:
        """Пометить сообщение как успешно доставленное в брокер сообщений."""
        stmt = (
            update(OutboxMessage)
            .where(OutboxMessage.id == message_id)
            .values(
                status=OutboxStatus.PROCESSED,
                processed_at=datetime.now(timezone.utc),
                error_message=None,
            )
        )
        await self.session.execute(stmt)

    async def mark_as_failed(
        self,
        message_id: UUID,
        error_message: str,
        max_retries: int = 3,
    ) -> None:
        """Зафиксировать ошибку отправки или перевести в FAILED при превышении лимита."""
        message = await self.get_by_id(message_id)
        if not message:
            return

        new_retry_count = message.retry_count + 1
        new_status = OutboxStatus.FAILED if new_retry_count >= max_retries else OutboxStatus.PENDING

        stmt = (
            update(OutboxMessage)
            .where(OutboxMessage.id == message_id)
            .values(
                retry_count=new_retry_count,
                status=new_status,
                error_message=error_message,
            )
        )
        await self.session.execute(stmt)