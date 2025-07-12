from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository
from infrastructure.adapters.postgres.uow import UnitOfWork


class MockGeoService:
    """Мок-сервис для работы с геолокацией."""

    async def get_location(self, address: str) -> Location:
        """Возвращает случайную локацию для любого адреса."""
        return Location.create_random()


class TestUnitOfWork(UnitOfWork):
    """Тестовый UoW, который использует одну сессию для всех операций."""

    def __init__(self, session: AsyncSession, event_publisher):
        self._session = session
        self._order_repository: OrderRepository | None = None
        self._courier_repository: CourierRepository | None = None
        self.event_publisher = event_publisher
        self._repositories: list = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
            return
        await self.commit()
