import enum
import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class OutboxStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Агрегат, породивший событие (например, "user")
    aggregate_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    # Идентификатор агрегата (user_id в виде строки или UUID)
    aggregate_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    # Тип события для потребителей (например, "user.registered", "user.password_reset")
    event_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Текущее состояние отправки
    status: Mapped[OutboxStatus] = mapped_column(
        Enum(OutboxStatus, name="outbox_status_enum", native_enum=True),
        default=OutboxStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Количество попыток доставки
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Описание ошибки, если отправка завершилась сбоем
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Таймстампы
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_outbox_messages_status_created_at", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<OutboxMessage id={self.id} event={self.event_type} "
            f"aggregate_id={self.aggregate_id} status={self.status.value}>"
        )