from typing import Optional

from models.base_model import BaseModel
from models.customer_session_status import CustomerSessionStatus
from models.user import User


class CustomerSession(BaseModel):
    """Tracks the orders of one customer, from their first order until they ask for the bill."""

    def __init__(self, id: int = 0, user: Optional[User] = None,
                 customer_session_status: CustomerSessionStatus = CustomerSessionStatus.ACTIVE):
        super().__init__(id)
        self.user = user
        self.customer_session_status = customer_session_status

    def is_active(self) -> bool:
        return self.customer_session_status == CustomerSessionStatus.ACTIVE
