from typing import Dict, Optional

from models.base_model import BaseModel
from models.customer_session import CustomerSession
from models.menu_item import MenuItem


class Order(BaseModel):
    def __init__(self, id: int = 0, customer_session: Optional[CustomerSession] = None,
                 ordered_items: Optional[Dict[MenuItem, int]] = None):
        super().__init__(id)
        self.customer_session = customer_session
        # {menu item: quantity}, for example {dosa: 2, coffee: 1}
        self.ordered_items: Dict[MenuItem, int] = ordered_items if ordered_items is not None else {}
