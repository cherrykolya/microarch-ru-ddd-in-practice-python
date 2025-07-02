from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from core.application.use_cases.commands.assign_orders import AssignOrdersUseCase
from core.application.use_cases.commands.create_order import CreateOrderUseCase
from core.application.use_cases.commands.move_couriers import MoveCouriersUseCase
from core.application.use_cases.queries.get_all_busy_couriers import GetAllBusyCouriersUseCase
from core.application.use_cases.queries.get_not_completed_orders import GetNotCompletedOrdersUseCase
from core.domain.services.dispatch_service import Dispatcher
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository
from infrastructure.adapters.postgres.session import async_session
from infrastructure.adapters.postgres.uow import UnitOfWork as PostgresUnitOfWork
from infrastructure.config.settings import Settings


class Container(containers.DeclarativeContainer):
    """IoC контейнер приложения."""

    config = providers.Singleton(Settings)

    # Database
    db_session: providers.Resource[AsyncSession] = providers.Resource(async_session)

    # Repositories
    courier_repository = providers.Factory(
        CourierRepository,
        session=db_session,
    )

    order_repository = providers.Factory(
        OrderRepository,
        session=db_session,
    )

    # Unit of Work
    unit_of_work = providers.Factory(
        PostgresUnitOfWork,
        session=db_session,
    )

    # Domain Services
    dispatcher = providers.Factory(
        Dispatcher,
    )

    # Use Cases
    assign_orders_use_case = providers.Factory(
        AssignOrdersUseCase,
        uow=unit_of_work,
        order_repository=order_repository,
        courier_repository=courier_repository,
        dispatcher=dispatcher,
    )

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        uow=unit_of_work,
        order_repository=order_repository,
    )

    move_couriers_use_case = providers.Factory(
        MoveCouriersUseCase,
        uow=unit_of_work,
        courier_repository=courier_repository,
        order_repository=order_repository,
    )

    get_not_completed_orders_use_case = providers.Factory(
        GetNotCompletedOrdersUseCase,
        session=db_session,
    )

    get_all_busy_couriers_use_case = providers.Factory(
        GetAllBusyCouriersUseCase,
        session=db_session,
    )
