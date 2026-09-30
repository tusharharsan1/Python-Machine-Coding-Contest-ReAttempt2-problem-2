from abc import ABC, abstractmethod
from typing import Optional

from models.customer_session import CustomerSession


class CustomerSessionRepository(ABC):
    @abstractmethod
    def save(self, customer_session: CustomerSession) -> CustomerSession:
        pass

    @abstractmethod
    def find_active_customer_session_by_user_id(self, user_id: int) -> Optional[CustomerSession]:
        pass
