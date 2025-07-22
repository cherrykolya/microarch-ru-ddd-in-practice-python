from typing import AsyncContextManager, Callable, Optional, cast

from sqlalchemy.ext.asyncio import AsyncSession

from core.ports.event_publisher_interface import EventPublisherInterface
from core.ports.unit_of_work import UnitOfWork as UnitOfWorkInterface
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository


class UnitOfWork(UnitOfWorkInterface):
    def __init__(
        self, session_factory: Callable[[], AsyncContextManager[AsyncSession]], event_publisher: EventPublisherInterface
    ):
        self.session_factory = session_factory
        self.event_publisher = event_publisher
        self._session: Optional[AsyncSession] = None
        self._order_repository: Optional[OrderRepository] = None
        self._courier_repository: Optional[CourierRepository] = None
        self._repositories: list = []

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

        domain_events = []
        for repo in self._repositories:
            domain_events.extend(repo.get_events())

        if self.event_publisher.requires_commit_after_publish:
            await self.event_publisher.publish(domain_events, session=self._session)
            await self._session.commit()
        else:
            await self._session.commit()
            await self.event_publisher.publish(domain_events)

    async def rollback(self):
        if not self._session:
            raise RuntimeError("Session not initialized")
        await self._session.rollback()

    @property
    def courier_repository(self) -> CourierRepository:
        if not self._session:
            raise RuntimeError("Session not initialized")

        if not self._courier_repository:
            self._courier_repository = CourierRepository(session=cast(AsyncSession, self._session))
            self.register_repository(self._courier_repository)

        return self._courier_repository

    @property
    def order_repository(self) -> OrderRepository:
        if not self._session:
            raise RuntimeError("Session not initialized")

        if not self._order_repository:
            self._order_repository = OrderRepository(session=cast(AsyncSession, self._session))
            self.register_repository(self._order_repository)

        return self._order_repository

    @property
    def session(self) -> AsyncSession:
        """Получение текущей сессии."""
        if not self._session:
            raise RuntimeError("Session not initialized")
        return cast(AsyncSession, self._session)
