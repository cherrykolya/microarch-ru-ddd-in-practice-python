from typing import AsyncContextManager, Callable, Optional, cast

from sqlalchemy.ext.asyncio import AsyncSession

from core.ports.unit_of_work import UnitOfWork as UnitOfWorkInterface
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository


class UnitOfWork(UnitOfWorkInterface):
    def __init__(self, session_factory: Callable[[], AsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self):
        try:
            async with self.session_factory() as session:
                self._session = session
                return self
        except Exception:
            if hasattr(self, "_session") and self._session is not None:
                await self._session.close()
            raise

    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if hasattr(self, "_session") and self._session is not None:
                await self._session.close()
                self._session = None

    async def commit(self):
        if not self._session:
            raise RuntimeError("Session not initialized")
        await self._session.commit()

    async def rollback(self):
        if not self._session:
            raise RuntimeError("Session not initialized")
        await self._session.rollback()

    @property
    def courier_repository(self) -> CourierRepository:
        if not self._session:
            raise RuntimeError("Session not initialized")
        return CourierRepository(session=cast(AsyncSession, self._session))

    @property
    def order_repository(self) -> OrderRepository:
        if not self._session:
            raise RuntimeError("Session not initialized")
        return OrderRepository(session=cast(AsyncSession, self._session))

    @property
    def session(self) -> AsyncSession:
        """Получение текущей сессии."""
        if not self._session:
            raise RuntimeError("Session not initialized")
        return cast(AsyncSession, self._session)
