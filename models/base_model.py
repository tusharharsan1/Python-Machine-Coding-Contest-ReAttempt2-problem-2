class BaseModel:
    """Every model has an id. 0 means "not saved yet"."""

    def __init__(self, id: int = 0):
        self.id = id
