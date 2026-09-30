from typing import Dict, Optional

from models.customer_session import CustomerSession
from repositories.customer_session_repository import CustomerSessionRepository


class InMemoryCustomerSessionRepository(CustomerSessionRepository):
    """Stores CustomerSession objects in a dictionary (in memory, no database needed).

    The tests create it with no arguments: InMemoryCustomerSessionRepository(). Keep it that way.
    """

    _id_counter = 0  # shared by all the repositories, so an id is never used twice

    def __init__(self):
        self.customer_session_map: Dict[int, CustomerSession] = {}

    def save(self, customer_session: CustomerSession) -> CustomerSession:
        # If the session does not have an id yet, give it one.
        if customer_session.id == 0:
            InMemoryCustomerSessionRepository._id_counter += 1
            customer_session.id = InMemoryCustomerSessionRepository._id_counter
        self.customer_session_map[customer_session.id] = customer_session
        return customer_session

    def find_active_customer_session_by_user_id(self, user_id: int) -> Optional[CustomerSession]:
        """Returns the active session of this user, or None if there is no such session."""
        for customer_session in self.customer_session_map.values():
            if customer_session.user.id == user_id and customer_session.is_active():
                return customer_session
        return None
