from typing import Dict, Optional

from models.base_model import BaseModel
from models.menu_item import MenuItem


class Bill(BaseModel):
    def __init__(self, id: int = 0, ordered_items: Optional[Dict[MenuItem, int]] = None,
                 total_amount: float = 0.0, gst: float = 0.0, service_charge: float = 0.0):
        super().__init__(id)
        # {menu item: total quantity}
        self.ordered_items: Dict[MenuItem, int] = ordered_items if ordered_items is not None else {}
        self.total_amount = total_amount  # includes the food cost, GST and the service charge
        self.gst = gst
        self.service_charge = service_charge
