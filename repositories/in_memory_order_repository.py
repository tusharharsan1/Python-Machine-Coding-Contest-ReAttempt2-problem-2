from typing import Dict, List

from models.order import Order
from repositories.order_repository import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    """Stores Order objects in a dictionary (in memory, no database needed).

    The tests create it with no arguments: InMemoryOrderRepository(). Keep it that way.
    """

    _id_counter = 0  # shared by all the repositories, so an id is never used twice

    def __init__(self):
        self.orders_map: Dict[int, Order] = {}

    def save(self, order: Order) -> Order:
        # If the order does not have an id yet, give it one.
        if order.id == 0:
            InMemoryOrderRepository._id_counter += 1
            order.id = InMemoryOrderRepository._id_counter
        self.orders_map[order.id] = order
        return order

    def find_orders_by_customer_session(self, customer_session_id: int) -> List[Order]:
        # TODO: Return a list with all the orders whose customer_session.id == customer_session_id.
        #   Loop over self.orders_map.values() and collect the matching orders.
        #   If there is no such order, return an empty list.
        return []  # delete this line when you are done
