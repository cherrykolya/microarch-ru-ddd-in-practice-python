from abc import ABC, abstractmethod

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order


class DispatcherInterface(ABC):
    @abstractmethod
    def dispatch(self, couriers: list[Courier], order: Order) -> None:
        pass
