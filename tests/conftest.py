import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from dependency_injector import providers
from sqlalchemy import event
from sqlalchemy.engine import Transaction
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.services.dispatch_service import Dispatcher
from core.domain.shared_kernel.location import Location
from core.ports.unit_of_work import UnitOfWork
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository
from infrastructure.di.container import Container


class TestUnitOfWork(UnitOfWork):
    """Тестовый UoW, который использует одну сессию для всех операций."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._courier_repository = CourierRepository(session)
        self._order_repository = OrderRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.commit()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    @property
    def courier_repository(self) -> CourierRepository:
        return self._courier_repository

    @property
    def order_repository(self) -> OrderRepository:
        return self._order_repository

    @property
    def session(self):
        return self._session


class TestContainer(Container):
    """Тестовый контейнер с переопределенными зависимостями."""

    config = providers.Configuration()

    # Сессия БД
    db_session = providers.Dependency(AsyncSession)

    # Unit of Work
    unit_of_work = providers.Factory(
        TestUnitOfWork,
        session=db_session,
    )

    # Сервисы
    dispatcher = providers.Factory(Dispatcher)

    # Use cases
    assign_orders_use_case = providers.Factory(
        "core.application.use_cases.commands.assign_orders.AssignOrdersUseCase",
        uow=unit_of_work,
        dispatcher=dispatcher,
    )

    move_couriers_use_case = providers.Factory(
        "core.application.use_cases.commands.move_couriers.MoveCouriersUseCase",
        uow=unit_of_work,
    )

    get_all_busy_couriers_use_case = providers.Factory(
        "core.application.use_cases.queries.get_all_busy_couriers.GetAllBusyCouriersUseCase",
        uow=unit_of_work,
    )

    get_not_completed_orders_use_case = providers.Factory(
        "core.application.use_cases.queries.get_not_completed_orders.GetNotCompletedOrdersUseCase",
        uow=unit_of_work,
    )


@pytest.fixture
def default_location() -> Location:
    """Базовая локация для тестов."""
    return Location.create(1, 1)


@pytest.fixture
def default_courier_speed() -> int:
    """Базовая скорость курьера для тестов."""
    return 2


@pytest.fixture
def default_order_volume() -> int:
    """Базовый объем заказа для тестов."""
    return 5


@pytest.fixture
def courier(default_location, default_courier_speed) -> Courier:
    """Базовый курьер для тестов."""
    return Courier.create(name="Test Courier", speed=default_courier_speed, location=default_location)


@pytest.fixture
def order(default_location, default_order_volume) -> Order:
    """Базовый заказ для тестов."""
    return Order.create(order_id=uuid4(), location=default_location, volume=default_order_volume)


@pytest.fixture
def dispatcher() -> Dispatcher:
    """Диспетчер для тестов."""
    return Dispatcher()


@pytest.fixture
def couriers(courier_locations) -> list[Courier]:
    return [Courier.create(name=f"Courier {i}", speed=2, location=loc) for i, loc in enumerate(courier_locations, 1)]


@pytest.fixture
def courier_locations() -> list[Location]:
    return [
        Location.create(1, 1),  # closest
        Location.create(10, 10),  # furthest
        Location.create(5, 5),  # middle
    ]


@pytest.fixture
def order_location() -> Location:
    """Локация заказа для тестов диспетчера."""
    return Location.create(2, 2)


@pytest.fixture(autouse=False)
def dispatch_order(order_location: Location, default_order_volume: int) -> Order:
    """Заказ для тестов диспетчера с особой локацией."""
    return Order.create(order_id=uuid4(), location=order_location, volume=default_order_volume)


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


# @pytest.fixture
# async def get_db_session_factory(engine: AsyncEngine) -> Callable[[], AsyncContextManager[AsyncSession]]:
#     """Create a database session factory."""
#     return async_sessionmaker(engine, expire_on_commit=False, future=True, autoflush=False)
