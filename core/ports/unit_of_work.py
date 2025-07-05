from abc import ABC, abstractmethod

from core.ports.courier_repository_interface import CourierRepositoryInterface
from core.ports.order_repository_interface import OrderRepositoryInterface


class UnitOfWork(ABC):
    """Абстрактный базовый класс для паттерна Unit of Work."""

    courier_repository: CourierRepositoryInterface
    order_repository: OrderRepositoryInterface

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Начало транзакции."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Завершение транзакции."""
        pass

    @abstractmethod
    async def commit(self):
        """Фиксация изменений."""
        pass

    @abstractmethod
    async def rollback(self):
        """Откат изменений."""
        pass
