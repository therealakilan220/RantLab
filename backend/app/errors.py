class ApiError(Exception):
    """Raise anywhere; main.py turns it into the standard error body from docs/api-contract.md."""

    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
