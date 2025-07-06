import uuid
from typing import List, Optional, Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from api.adapters.http.schemas import CourierTest, Error, NewCourierTest, Order
from core.application.use_cases.commands.create_courier import CreateCourierCommand, CreateCourierUseCase
from core.application.use_cases.commands.create_order import CreateOrderCommand, CreateOrderUseCase
from core.application.use_cases.queries.get_all_couriers import GetAllCouriersQuery, GetAllCouriersUseCase
from core.application.use_cases.queries.get_not_completed_orders import (
    GetNotCompletedOrdersQuery,
    GetNotCompletedOrdersUseCase,
)
from infrastructure.di.container import Container

router = APIRouter(prefix="/api/v1")


@router.post(
    "/couriers",
    response_model=None,
    responses={"default": {"model": Error}, "400": {"model": Error}, "409": {"model": Error}},
)
@inject
async def create_courier(
    body: NewCourierTest = Body(), use_case: CreateCourierUseCase = Depends(Provide[Container.create_courier_use_case])
) -> Optional[Error]:
    """
    Добавить курьера
    """
    command = CreateCourierCommand(
        name=body.name,
        speed=body.speed,
    )
    await use_case.handle(command)


@router.get("/couriers", response_model=List[CourierTest], responses={"default": {"model": Error}})
@inject
async def get_couriers(
    use_case: GetAllCouriersUseCase = Depends(Provide[Container.get_all_couriers_use_case]),
) -> Union[List[CourierTest], Error]:
    """
    Получить всех курьеров
    """
    query = GetAllCouriersQuery()
    return await use_case.handle(query)


@router.post("/orders", response_model=None, responses={"default": {"model": Error}})
@inject
async def create_order(
    use_case: CreateOrderUseCase = Depends(Provide[Container.create_order_use_case]),
) -> Optional[Error]:
    """
    Создать заказ
    """
    command = CreateOrderCommand(
        basket_id=uuid.uuid4(),
        street="test",
        volume=1,
    )
    await use_case.handle(command)


@router.get("/orders/active", response_model=List[Order], responses={"default": {"model": Error}})
@inject
async def get_orders(
    use_case: GetNotCompletedOrdersUseCase = Depends(Provide[Container.get_not_completed_orders_use_case]),
) -> Union[List[Order], Error]:
    """
    Получить все незавершенные заказы
    """

    return await use_case.handle(GetNotCompletedOrdersQuery())
