class GenerateBillRequestDto:
    """The request: the id of the customer who wants the bill."""

    def __init__(self, user_id: int):
        self.user_id = user_id
