from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from faststream.kafka.fastapi import KafkaRouter

from core.application.use_cases.commands.create_order import CreateOrderCommand, CreateOrderUseCase
from infrastructure.config.settings import get_settings
from infrastructure.di.container import Container

from .schemas import BasketConfirmedEvent

settings = get_settings()


# Инициализация брокера
router = KafkaRouter(settings.kafka.BROKERS.split(","), include_in_schema=False)


@router.subscriber(
    settings.kafka.BASKET_CONFIRMED_TOPIC,
    group_id=settings.kafka.BASKET_CONFIRMED_GROUP_ID,
)
@inject
async def process_basket_confirmed(
    msg: BasketConfirmedEvent,
    use_case: CreateOrderUseCase = Depends(Provide[Container.create_order_use_case]),
) -> None:
    """
    Обработчик события подтверждения корзины.
    """

    await use_case.handle(
        CreateOrderCommand(
            basket_id=msg.basket_id,
            street=msg.address.street,
            volume=msg.volume,
        )
    )
