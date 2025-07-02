import pytest
from dependency_injector.providers import Resource
from sqlalchemy.ext.asyncio import AsyncSession

from core.application.use_cases.commands.assign_orders import AssignOrdersCommand
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_assign_orders(db_session_with_commit: AsyncSession):
    # Создаем контейнер
    container = Container()

    # Переопределяем провайдер сессии, чтобы использовать сессию из фикстуры
    container.db_session.override(Resource(lambda: db_session_with_commit))

    container.init_resources()

    # Получаем use case из контейнера
    assign_orders = await container.assign_orders_use_case()

    # Используем use case
    await assign_orders.handle(AssignOrdersCommand())
