"""Data models for TryHackMe API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


# ── Users ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class User:
    username: str
    email: str
    avatar: str
    total_points: int
    monthly_points: int
    date_signed_up: datetime
    ext_user_id: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> User:
        return cls(
            username=data["username"],
            email=data["email"],
            avatar=data["avatar"],
            total_points=data.get("totalPoint", 0),
            monthly_points=data.get("monthlyPoints", 0),
            date_signed_up=datetime.fromisoformat(
                data["dateSignedUp"].replace("Z", "+00:00")
            ),
            ext_user_id=data.get("extUserId"),
        )


# ── Rooms ────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Room:
    code: str
    title: str
    description: str
    public: bool

    @classmethod
    def from_api(cls, data: dict) -> Room:
        return cls(
            code=data["code"],
            title=data["title"],
            description=data["description"],
            public=data["public"],
        )


# ── Questions ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Question:
    question_no: int
    question: str
    answer: str
    hint: str
    extra_points: int

    @classmethod
    def from_api(cls, data: dict) -> Question:
        return cls(
            question_no=data["questionNo"],
            question=data["question"],
            answer=data.get("answer", ""),
            hint=data.get("hint", ""),
            extra_points=data.get("extraPoints", 0),
        )


@dataclass(frozen=True)
class Task:
    task_no: int
    questions: list[Question] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> Task:
        return cls(
            task_no=data["taskNo"],
            questions=[Question.from_api(q) for q in data.get("infoList", [])],
        )


# ── Scoreboard ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TaskAttempt:
    question_no: int
    correct: bool
    score: int
    attempts: int
    id: str
    time_correct: datetime | None = None

    @classmethod
    def from_api(cls, data: dict) -> TaskAttempt:
        tc = data.get("timeCorrect")
        return cls(
            question_no=data["questionNo"],
            correct=data["correct"],
            score=data.get("score", 0),
            attempts=data.get("attempts", 0),
            id=data.get("_id", ""),
            time_correct=(
                datetime.fromisoformat(tc.replace("Z", "+00:00")) if tc else None
            ),
        )


@dataclass(frozen=True)
class ScoreboardEntry:
    username: str
    score: int
    level: int
    avatar: str
    rank: int
    tasks: dict[str, list[TaskAttempt]] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict) -> ScoreboardEntry:
        tasks: dict[str, list[TaskAttempt]] = {}
        for task_key, attempts in data.get("tasks", {}).items():
            tasks[task_key] = [TaskAttempt.from_api(a) for a in attempts]
        return cls(
            username=data["username"],
            score=data.get("score", 0),
            level=data.get("level", 0),
            avatar=data.get("avatar", ""),
            rank=data.get("rank", 0),
            tasks=tasks,
        )


# ── Time Report ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TimeReportUser:
    id: str
    username: str
    email: str
    total_seconds: int

    @classmethod
    def from_api(cls, data: dict) -> TimeReportUser:
        return cls(
            id=data["_id"],
            username=data["username"],
            email=data["email"],
            total_seconds=data["totalSeconds"],
        )


@dataclass(frozen=True)
class TimeReport:
    users: list[TimeReportUser]
    min_seconds: int
    max_seconds: int

    @classmethod
    def from_api(cls, data: dict) -> TimeReport:
        return cls(
            users=[TimeReportUser.from_api(u) for u in data.get("users", [])],
            min_seconds=data.get("minSeconds", 0),
            max_seconds=data.get("maxSeconds", 0),
        )
