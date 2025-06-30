import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.engine import Transaction
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.services.dispatch_service import Dispatcher
from core.domain.shared_kernel.location import Location


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
    loop = asyncio.get_event_loop_policy().new_event_loop()
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
async def engine(postgres_container: PostgresContainer, apply_migrations):
    """Create engine connected to test database with applied migrations."""
    engine = create_async_engine(
        postgres_container.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://"),
        echo=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session_with_commit(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session that commits changes."""
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
