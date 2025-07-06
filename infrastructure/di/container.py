from typing import AsyncContextManager, Callable

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from core.application.use_cases.commands.assign_orders import AssignOrdersUseCase
from core.application.use_cases.commands.create_courier import CreateCourierUseCase
from core.application.use_cases.commands.create_order import CreateOrderUseCase
from core.application.use_cases.commands.move_couriers import MoveCouriersUseCase
from core.application.use_cases.queries.get_all_busy_couriers import GetAllBusyCouriersUseCase
from core.application.use_cases.queries.get_all_couriers import GetAllCouriersUseCase
from core.application.use_cases.queries.get_not_completed_orders import GetNotCompletedOrdersUseCase
from core.domain.services.dispatch_service import Dispatcher
from infrastructure.adapters.postgres.session import get_db_session
from infrastructure.adapters.postgres.uow import UnitOfWork as PostgresUnitOfWork
from infrastructure.config.settings import Settings


class Container(containers.DeclarativeContainer):
    """IoC контейнер приложения."""

    config = providers.Singleton(Settings)

    # Database
    db_session_factory: providers.Resource[Callable[[], AsyncContextManager[AsyncSession]]] = providers.Resource(
        get_db_session
    )

    # Unit of Work
    unit_of_work = providers.Factory(
        PostgresUnitOfWork,
        session_factory=db_session_factory,
    )

    # Domain Services
    dispatcher = providers.Factory(
        Dispatcher,
    )

    # Use Cases
    assign_orders_use_case = providers.Factory(
        AssignOrdersUseCase,
        uow=unit_of_work,
        dispatcher=dispatcher,
    )

    create_order_use_case = providers.Factory(
        CreateOrderUseCase,
        uow=unit_of_work,
    )

    move_couriers_use_case = providers.Factory(
        MoveCouriersUseCase,
        uow=unit_of_work,
    )

    get_not_completed_orders_use_case = providers.Factory(
        GetNotCompletedOrdersUseCase,
        uow=unit_of_work,
    )

    get_all_busy_couriers_use_case = providers.Factory(
        GetAllBusyCouriersUseCase,
        uow=unit_of_work,
    )

    get_all_couriers_use_case = providers.Factory(
        GetAllCouriersUseCase,
        uow=unit_of_work,
    )

    create_courier_use_case = providers.Factory(
        CreateCourierUseCase,
        uow=unit_of_work,
    )
