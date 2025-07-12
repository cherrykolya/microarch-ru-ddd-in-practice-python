import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from alembic import command
from alembic.config import Config
from dependency_injector import providers
from sqlalchemy import event
from sqlalchemy.engine import Transaction
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from core.application.use_cases.commands.assign_orders import AssignOrdersUseCase
from core.application.use_cases.commands.create_order import CreateOrderUseCase
from core.application.use_cases.commands.move_couriers import MoveCouriersUseCase
from core.application.use_cases.queries.get_all_busy_couriers import GetAllBusyCouriersUseCase
from core.application.use_cases.queries.get_not_completed_orders import GetNotCompletedOrdersUseCase
from core.domain.services.dispatch_service import Dispatcher
from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.adapters.kafka.event_publisher import KafkaEventPublisher
from infrastructure.di.container import Container
from tests.fixtures.mocks import MockGeoService, TestUnitOfWork

pytest_plugins = [
    # dicts
    "tests.fixtures.base",
]


class TestContainer(Container):
    """Тестовый контейнер с замоканными зависимостями."""

    # Сессия БД
    db_session = providers.Dependency(AsyncSession)

    # Переопределяем kafka_producer и event_publisher для тестов
    kafka_producer = providers.Factory(
        lambda: Mock(
            start=AsyncMock(return_value=None), stop=AsyncMock(return_value=None), send=AsyncMock(return_value=None)
        )
    )

    kafka_event_publisher: providers.Provider[EventPublisherInterface] = providers.Factory(
        KafkaEventPublisher,
        kafka_producer=kafka_producer,
    )

    # Unit of Work
    unit_of_work = providers.Factory(
        TestUnitOfWork,
        session=db_session,
        event_publisher=kafka_event_publisher,
    )

    # Сервисы
    dispatcher = providers.Factory(Dispatcher)
    geo_service = providers.Singleton(MockGeoService)

    # Use cases
    assign_orders_use_case = providers.Factory(
        AssignOrdersUseCase,
        uow=unit_of_work,
        dispatcher=dispatcher,
    )

    move_couriers_use_case = providers.Factory(
        MoveCouriersUseCase,
        uow=unit_of_work,
    )

    get_all_busy_couriers_use_case = providers.Factory(
        GetAllBusyCouriersUseCase,
        uow=unit_of_work,
    )

    get_not_completed_orders_use_case = providers.Factory(
        GetNotCompletedOrdersUseCase,
        uow=unit_of_work,
    )

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        uow=unit_of_work,
        geo_service=geo_service,
    )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
    """Create a PostgreSQL container for testing."""
    with PostgresContainer("postgres:15-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def alembic_config(postgres_container: PostgresContainer) -> Config:
    """Create Alembic config for test database."""
    config = Config("alembic.ini")
    config.set_main_option(
        "sqlalchemy.url",
        postgres_container.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://"),
    )
    return config


@pytest.fixture(scope="session")
def apply_migrations(alembic_config: Config):
    """Apply migrations to test database."""
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture(scope="session")
async def engine(postgres_container: PostgresContainer, apply_migrations) -> AsyncGenerator[AsyncEngine, None]:
    """Создает движок БД для тестов."""
    engine = create_async_engine(
        postgres_container.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://"),
        echo=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session_with_commit(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False, future=True, autoflush=False)
    await connection.begin_nested()

    @event.listens_for(session.sync_session, "after_transaction_end")
    def end_savepoint(session: AsyncSession, transaction: Transaction) -> None:
        """async events are not implemented yet, recreates savepoints to avoid final commits"""
        # https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-756269881
        if connection.closed:
            return
        if not connection.in_nested_transaction():
            connection.sync_connection.begin_nested()

    try:
        yield session
    finally:
        if session.in_transaction():  # pylint: disable=no-member
            await transaction.rollback()

        await connection.close()


@pytest.fixture
def test_container(db_session_with_commit: AsyncSession) -> Generator[Container, None, None]:
    """Создает тестовый контейнер с замоканным UoW."""
    container = TestContainer()
    container.db_session.override(providers.Object(db_session_with_commit))
    container.init_resources()

    yield container
    container.shutdown_resources()
