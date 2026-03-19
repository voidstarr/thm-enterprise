"""thm-enterprise: Pythonic client for the TryHackMe Enterprise API."""

from .client import TryHackMe
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    TryHackMeError,
)
from .models import (
    Question,
    Room,
    ScoreboardEntry,
    Task,
    TaskAttempt,
    TimeReport,
    TimeReportUser,
    User,
)

__all__ = [
    "TryHackMe",
    # exceptions
    "TryHackMeError",
    "AuthenticationError",
    "BadRequestError",
    "NotFoundError",
    # models
    "User",
    "Room",
    "Question",
    "Task",
    "TaskAttempt",
    "ScoreboardEntry",
    "TimeReport",
    "TimeReportUser",
]
