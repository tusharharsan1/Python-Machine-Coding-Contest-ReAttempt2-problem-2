from typing import Optional

from dtos.response_status import ResponseStatus
from models.bill import Bill


class GenerateBillResponseDto:
    """The response: the bill and whether it worked."""

    def __init__(self):
        self.response_status: Optional[ResponseStatus] = None
        self.bill: Optional[Bill] = None
