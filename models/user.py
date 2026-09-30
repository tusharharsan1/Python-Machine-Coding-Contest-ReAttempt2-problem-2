from typing import Optional

from models.base_model import BaseModel
from models.user_type import UserType


class User(BaseModel):
    def __init__(self, id: int = 0, name: str = "", password: str = "", phone: str = "",
                 user_type: Optional[UserType] = UserType.CUSTOMER):
        super().__init__(id)
        self.name = name
        self.password = password
        self.phone = phone
        self.user_type = user_type
