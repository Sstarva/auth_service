from typing import Any, Generic, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый абстрактный репозиторий для CRUD операций над моделями."""

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, id_: UUID | int | str) -> ModelType | None:
        """Получить запись по первичному ключу."""
        return await self.session.get(self.model, id_)

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Получить список записей с пагинацией."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, entity: ModelType) -> ModelType:
        """Добавить сущность в контекст сессии (без commit)."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, id_: UUID | int | str, **values: Any) -> ModelType | None:
        """Обновить поля записи по первичному ключу."""
        stmt = (
            update(self.model)
            .where(self.model.id == id_)
            .values(**values)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, id_: UUID | int | str) -> bool:
        """Удалить запись по первичному ключу."""
        stmt = delete(self.model).where(self.model.id == id_)
        result = await self.session.execute(stmt)
        return result.rowcount > 0