from abc import ABC, abstractmethod
from typing import List

from models.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        pass

    @abstractmethod
    def find_orders_by_customer_session(self, customer_session_id: int) -> List[Order]:
        pass
