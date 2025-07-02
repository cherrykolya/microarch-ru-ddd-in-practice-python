from sqlalchemy.ext.asyncio import AsyncSession

from core.ports.unit_of_work import UnitOfWork as UnitOfWorkInterface


class UnitOfWork(UnitOfWorkInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
