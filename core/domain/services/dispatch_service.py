from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.services.dispatch_service_interface import DispatcherInterface


class Dispatcher(DispatcherInterface):
    def dispatch(self, couriers: list[Courier], order: Order) -> Courier:
        closest_courier = None
        closest_courier_time_to_location = float("inf")

        for courier in couriers:
            time_to_location = courier.calculate_time_to_location(order.location)
            if time_to_location < closest_courier_time_to_location and courier.can_take_order(order):
                closest_courier = courier
                closest_courier_time_to_location = time_to_location

        if closest_courier is None:
            raise ValueError("No courier can take order")

        closest_courier.take_order(order)

        return closest_courier
