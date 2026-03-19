# thm-enterprise

Python client for the [TryHackMe Enterprise API](https://help.tryhackme.com/en/project/thmapi/articles/6498330-enterprise-api).

Requires a **Business** or **Classroom** plan API key.

## Installation

```bash
pip install thm-enterprise
```

## Quick Start

```python
from thm_enterprise import TryHackMe

thm = TryHackMe(api_key="your-api-key")

# List all users on your seats / api-users
for user in thm.get_users():
    print(user.username, user.email, user.total_points)

# Get room scoreboard (scores + per-question attempts)
for entry in thm.get_scoreboard("dvwa"):
    print(entry.username, entry.score)

# Check available rooms
rooms = thm.get_rooms()

# Get questions for a room
tasks = thm.get_room_questions("dvwa")
for task in tasks:
    for q in task.questions:
        print(f"Task {task.task_no} Q{q.question_no}: {q.question}")
```

## API Coverage

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_registration_url(token)` | `GET /external/api/register` | Build a registration URL for an API-user |
| `authenticate_user(ext_user_id, room_code)` | `POST /external/api/authenticate` | Authenticate/register a user and get a redirect URL |
| `add_seat(email)` | `PUT /api/v2/external/seats/users` | Add a user to a company seat |
| `remove_seat(email)` | `DELETE /api/v2/external/seats/users` | Remove a user from a company seat |
| `get_users()` | `GET /external/api/users` | List all seated and API users |
| `get_user_by_email(email)` | — | Convenience lookup by email |
| `get_rooms()` | `GET /external/api/rooms` | List all accessible rooms |
| `room_exists(room_code)` | `GET /external/api/roomExists` | Check if a room exists |
| `get_room_questions(room_code)` | `GET /external/api/questions` | Get tasks and questions for a room |
| `remove_user_from_room(ext_user_id, room_code)` | `POST /external/api/leaveRoom` | Remove a user from a room |
| `get_scoreboard(room_code)` | `GET /api/v2/external/scoreboard` | Get scores and attempts for a room |
| `get_time_report(emails, from_date, to_date)` | `POST /api/v2/external/reports/time` | Get time spent per user between two dates |

## Error Handling

All API errors raise typed exceptions:

```python
from thm_enterprise import TryHackMe, AuthenticationError, BadRequestError, NotFoundError

thm = TryHackMe(api_key="your-api-key")

try:
    thm.get_scoreboard("nonexistent-room")
except AuthenticationError:
    print("Invalid or expired API key")
except NotFoundError:
    print("Room not found")
except BadRequestError as e:
    print(f"Bad request: {e.message}")
```

## License

[MIT](LICENSE)
