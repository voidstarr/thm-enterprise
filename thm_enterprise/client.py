"""TryHackMe Enterprise API client."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import requests

from .exceptions import AuthenticationError, BadRequestError, NotFoundError, TryHackMeError
from .models import (
    Room,
    ScoreboardEntry,
    Task,
    TimeReport,
    User,
)

_BASE = "https://tryhackme.com"

_ERROR_MAP: dict[int, type[TryHackMeError]] = {
    400: BadRequestError,
    403: AuthenticationError,
    404: NotFoundError,
}


class TryHackMe:
    """Pythonic wrapper around the TryHackMe Enterprise API.

    Usage::

        from thm import TryHackMe

        thm = TryHackMe(api_key="your-key")

        # list all seated / api users
        users = thm.get_users()

        # room scoreboard (grades)
        scores = thm.get_scoreboard("dvwa")
    """

    def __init__(self, api_key: str, *, timeout: int = 30) -> None:
        self._session = requests.Session()
        self._session.headers["THM-API-KEY"] = api_key
        self._timeout = timeout

    # ── helpers ───────────────────────────────────────────────────────────

    def _url(self, path: str) -> str:
        return f"{_BASE}{path}"

    def _handle_response(self, resp: requests.Response) -> dict:
        """Raise a typed exception on error, otherwise return the JSON body."""
        if resp.ok:
            try:
                return resp.json()
            except requests.JSONDecodeError:
                return {}

        # Try to pull a useful message out of the error body.
        try:
            body = resp.json()
            message = body.get("message", resp.text)
        except requests.JSONDecodeError:
            message = resp.text

        exc_cls = _ERROR_MAP.get(resp.status_code, TryHackMeError)
        raise exc_cls(message, status_code=resp.status_code)

    def _get(self, path: str, **params: str) -> dict:
        resp = self._session.get(self._url(path), params=params, timeout=self._timeout)
        return self._handle_response(resp)

    def _post(self, path: str, json: dict | None = None) -> dict:
        resp = self._session.post(self._url(path), json=json, timeout=self._timeout)
        return self._handle_response(resp)

    def _put(self, path: str, json: dict | None = None) -> dict:
        resp = self._session.put(self._url(path), json=json, timeout=self._timeout)
        return self._handle_response(resp)

    def _delete(self, path: str, json: dict | None = None) -> dict:
        resp = self._session.delete(self._url(path), json=json, timeout=self._timeout)
        return self._handle_response(resp)

    # ── Authentication & Registration ────────────────────────────────────

    def get_registration_url(self, token: str) -> str:
        """Return the registration URL for an API-user token."""
        return f"{_BASE}/external/api/register?token={token}"

    def authenticate_user(self, ext_user_id: str, room_code: str) -> str:
        """Authenticate / register an external user and return the redirect URL.

        * If the user does not exist → adds them and returns a registration link.
        * If the user exists but is unregistered → returns registration link.
        * If the user exists and is registered → returns a room-join link.
        """
        data = self._post(
            "/external/api/authenticate",
            json={"extUserId": ext_user_id, "roomCode": room_code},
        )
        return data["url"]

    # ── Seats ────────────────────────────────────────────────────────────

    def add_seat(self, email: str) -> str:
        """Add a user to a company seat.  Returns the username."""
        data = self._put("/api/v2/external/seats/users", json={"email": email})
        return data["data"]["username"]

    def remove_seat(self, email: str) -> str:
        """Remove a user from a company seat.  Returns the username."""
        data = self._delete("/api/v2/external/seats/users", json={"email": email})
        return data["data"]["username"]

    # ── Users ────────────────────────────────────────────────────────────

    def get_users(self) -> list[User]:
        """Retrieve all seated and API users."""
        data = self._get("/external/api/users")
        return [User.from_api(u) for u in data.get("users", [])]

    def get_user_by_email(self, email: str) -> User | None:
        """Convenience: find a single user by email (case-insensitive)."""
        email_lower = email.lower()
        for user in self.get_users():
            if user.email.lower() == email_lower:
                return user
        return None

    # ── Rooms ────────────────────────────────────────────────────────────

    def get_rooms(self) -> list[Room]:
        """Retrieve all accessible rooms (public + private)."""
        data = self._get("/external/api/rooms")
        return [Room.from_api(r) for r in data.get("roomInfo", [])]

    def room_exists(self, room_code: str) -> bool:
        """Check whether a room exists on the platform."""
        data = self._get("/external/api/roomExists", roomCode=room_code)
        return data.get("roomExists", False)

    def get_room_questions(self, room_code: str) -> list[Task]:
        """Retrieve the tasks and questions for a room."""
        data = self._get("/external/api/questions", roomCode=room_code)
        return [Task.from_api(t) for t in data.get("questions", [])]

    def remove_user_from_room(self, ext_user_id: str, room_code: str) -> None:
        """Mark a user as having left a room."""
        self._post(
            "/external/api/leaveRoom",
            json={"extUserId": ext_user_id, "roomCode": room_code},
        )

    # ── Scoreboard / Grades ──────────────────────────────────────────────

    def get_scoreboard(self, room_code: str) -> list[ScoreboardEntry]:
        """Retrieve the score and attempt data for all users in a room."""
        data = self._get("/api/v2/external/scoreboard", roomCode=room_code)
        return [ScoreboardEntry.from_api(e) for e in data.get("data", [])]

    # ── Time Report ──────────────────────────────────────────────────────

    def get_time_report(
        self,
        emails: list[str],
        from_date: datetime,
        to_date: datetime,
        room_types: list[Literal["walkthrough", "challenge"]] | None = None,
    ) -> TimeReport:
        """Return total time spent per user between two dates."""
        body: dict = {
            "userEmails": emails,
            "from": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "to": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }
        if room_types is not None:
            body["roomTypes"] = room_types
        data = self._post("/api/v2/external/reports/time", json=body)
        return TimeReport.from_api(data.get("data", {}))
