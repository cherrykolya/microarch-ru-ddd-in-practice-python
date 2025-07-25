from typing import AsyncContextManager, Callable

from aiokafka import AIOKafkaProducer
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
from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.adapters.grpc.geo.client import GRPCGeoService
from infrastructure.adapters.kafka.event_publisher import KafkaEventPublisher, get_kafka_producer
from infrastructure.adapters.postgres.outbox.outbox_poller import OutboxPollingPublisher
from infrastructure.adapters.postgres.outbox.outbox_publisher import OutboxPublisher
from infrastructure.adapters.postgres.session import get_db_session
from infrastructure.adapters.postgres.uow import UnitOfWork as PostgresUnitOfWork
from infrastructure.config.settings import Settings, get_settings


class Container(containers.DeclarativeContainer):
    """IoC контейнер приложения."""

    config: providers.Provider[Settings] = providers.Singleton(get_settings)

    # Database
    db_session_factory: providers.Provider[Callable[[], AsyncContextManager[AsyncSession]]] = providers.Resource(
        get_db_session
    )

    # Kafka
    kafka_producer: providers.Singleton[AIOKafkaProducer] = providers.Singleton(get_kafka_producer)

    kafka_event_publisher: providers.Provider[EventPublisherInterface] = providers.Factory(
        KafkaEventPublisher,
        kafka_producer=kafka_producer,
    )

    outbox_publisher: providers.Provider[OutboxPublisher] = providers.Factory(
        OutboxPublisher,
    )

    # Geo Service
    geo_service = providers.Factory(
        GRPCGeoService,
        host=config().geo_service.host,
        port=config().geo_service.port,
    )

    # Unit of Work
    unit_of_work = providers.Factory(
        PostgresUnitOfWork,
        session_factory=db_session_factory,
        event_publisher=outbox_publisher,
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
        geo_service=geo_service,
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

    outbox_poller = providers.Factory(
        OutboxPollingPublisher,
    )
