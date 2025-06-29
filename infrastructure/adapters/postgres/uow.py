from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.courier_repository = CourierRepository(session)
        self.order_repository = OrderRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
