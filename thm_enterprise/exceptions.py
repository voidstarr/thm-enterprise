"""TryHackMe API exceptions."""


class TryHackMeError(Exception):
    """Base exception for TryHackMe API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(TryHackMeError):
    """Raised when the API key is invalid or missing (403)."""


class BadRequestError(TryHackMeError):
    """Raised on 400 Bad Request responses."""


class NotFoundError(TryHackMeError):
    """Raised on 404 Not Found responses."""
