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
        """Returns all the orders of this customer session (an empty list if there are none)."""
        orders_of_session = []
        for order in self.orders_map.values():
            if order.customer_session.id == customer_session_id:
                orders_of_session.append(order)
        return orders_of_session
