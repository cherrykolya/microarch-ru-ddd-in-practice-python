from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class Address(BaseModel):
    country: str = Field(alias="Country", description="Страна доставки")
    city: str = Field(alias="City", description="Город доставки")
    street: str = Field(alias="Street", description="Улица доставки")
    house: str = Field(alias="House", description="Номер дома")
    apartment: str = Field(alias="Apartment", description="Номер квартиры")

    class Config:
        populate_by_name = True


class Item(BaseModel):
    id: UUID = Field(alias="Id", description="Уникальный идентификатор позиции в корзине")
    good_id: str = Field(alias="GoodId", description="Уникальный идентификатор товара")
    title: str = Field(alias="Title", description="Название товара")
    price: Decimal = Field(alias="Price", description="Цена товара", gt=0)
    quantity: int = Field(alias="Quantity", description="Количество товара", gt=0)

    class Config:
        populate_by_name = True


class DeliveryPeriod(BaseModel):
    from_: int = Field(alias="From", description="Начало периода доставки (в часах)")
    to: int = Field(alias="To", description="Конец периода доставки (в часах)")

    class Config:
        populate_by_name = True


class BasketConfirmedEvent(BaseModel):
    basket_id: UUID = Field(alias="BasketId", description="Уникальный идентификатор корзины")
    address: Address = Field(alias="Address", description="Адрес доставки")
    items: List[Item] = Field(alias="Items", description="Список товаров в корзине")
    delivery_period: DeliveryPeriod = Field(alias="DeliveryPeriod", description="Период доставки")
    volume: int = Field(alias="Volume", description="Объем заказа", gt=0)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "BasketId": "b79bf0be-b53a-4280-8c66-054066eb6f00",
                "Address": {
                    "Country": "Россия",
                    "City": "Москва",
                    "Street": "Несуществующая",
                    "House": "1",
                    "Apartment": "1",
                },
                "Items": [
                    {
                        "Id": "b1b1ba4b-4a6d-4935-b2c2-c6d93e29997d",
                        "GoodId": "292dc3c5-2bdd-4e0c-bd75-c5e8b07a8792",
                        "Title": "Кофе",
                        "Price": 500.0,
                        "Quantity": 4,
                    }
                ],
                "DeliveryPeriod": {"From": 6, "To": 12},
                "Volume": 4,
            }
        }
