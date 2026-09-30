from typing import Optional

from models.base_model import BaseModel
from models.dietary_requirement import DietaryRequirement
from models.item_type import ItemType


class MenuItem(BaseModel):
    def __init__(self, id: int = 0, name: str = "", price: float = 0.0,
                 dietary_requirement: Optional[DietaryRequirement] = None,
                 item_type: Optional[ItemType] = None, description: str = ""):
        super().__init__(id)
        self.name = name
        self.price = price
        self.dietary_requirement = dietary_requirement
        self.item_type = item_type
        self.description = description
