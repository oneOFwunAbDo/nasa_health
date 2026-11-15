"""
Local user storage for the Space Health app.

Everything is saved in users.json next to this file:
  first name, last name, username, password (salted + hashed, never plain text),
  face encodings (numbers describing the face, NOT photos), station, language,
  mission progress and the reminders / animation settings.

Writes are atomic: data goes to a temporary file first and is then swapped in
with os.replace(), so a crash mid-save can never leave a half-written users.json.

The admin page will read from this same file later.
"""

import datetime
import hashlib
import hmac
import json
import os
import secrets
import tempfile
from pathlib import Path

DATA_FILE = Path(__file__).with_name("users.json")


# ------------------------------------------------------------------ file access
def _load():
    if not DATA_FILE.exists():
        return {"users": {}}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _save(data):
    """Atomic save: write a temp file in the same folder, flush it, then os.replace()."""
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(
        dir=DATA_FILE.parent, prefix=DATA_FILE.stem + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, DATA_FILE)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


# ------------------------------------------------------------------ mission dates
def mission_date(start, day):
    """The calendar date that mission day `day` falls on (day 1 = `start`)."""
    return start + datetime.timedelta(days=day - 1)


def elapsed_mission_day(start, today=None):
    """Which mission day it is right now, counting real days since `start`."""
    today = today or datetime.date.today()
    return max(1, (today - start).days + 1)


# ------------------------------------------------------------------ schema / migration
def _legacy_mission_start(user):
    """
    Start date for profiles saved before `mission_start` existed. Uses the sign-up
    date, moved earlier if needed so the saved mission day is not in the future.
    """
    today = datetime.date.today()
    try:
        start = datetime.datetime.fromisoformat(user["created"]).date()
    except (KeyError, ValueError, TypeError):
        start = today

    furthest = user.get("current_mission_day")
    furthest = furthest if isinstance(furthest, int) and furthest >= 1 else 1
    for key, states in (user.get("mission_tasks") or {}).items():
        if isinstance(states, list) and any(states) and str(key).isdigit():
            furthest = max(furthest, int(key))
    return min(start, today - datetime.timedelta(days=furthest - 1))


def _apply_defaults(user):
    """Fill in keys missing from older profiles. Returns True if anything changed."""
    changed = False
    for key, value in (("tasks", {}), ("mission_tasks", {}),
                       ("reminders", True), ("animate", True)):
        if key not in user:
            user[key] = value
            changed = True

    day = user.get("current_mission_day")
    if not isinstance(day, int) or day < 1:
        user["current_mission_day"] = 1
        changed = True

    if "mission_start" not in user:
        user["mission_start"] = _legacy_mission_start(user).isoformat()
        changed = True
    return changed


# ------------------------------------------------------------------ passwords
def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()


# ------------------------------------------------------------------ public API
def username_taken(username):
    return username.lower() in _load()["users"]


def get_user(username):
    """Return one user's record. Older profiles are upgraded (and saved) on first read."""
    data = _load()
    user = data["users"].get(username.lower())
    if user is not None and _apply_defaults(user):
        _save(data)
    return user


def create_user(first_name, last_name, username, password,
                face_encodings, station, language):
    data = _load()
    key = username.lower()
    if key in data["users"]:
        raise ValueError("username already taken")

    salt = secrets.token_bytes(16)
    today = datetime.date.today()
    data["users"][key] = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password_salt": salt.hex(),
        "password_hash": _hash_password(password, salt),
        "face_encodings": face_encodings,   # list of 128-number lists
        "station": station,
        "language": language,
        "tasks": {},                        # "YYYY-MM-DD" -> tasks completed that day
        "mission_start": today.isoformat(), # date that mission day 1 falls on
        "current_mission_day": 1,
        "mission_tasks": {},                # "1" -> [True, False, ...] per mission day
        "reminders": True,
        "animate": True,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    _save(data)


def check_password(username, password):
    user = get_user(username)
    if user is None:
        return False
    salt = bytes.fromhex(user["password_salt"])
    return hmac.compare_digest(_hash_password(password, salt), user["password_hash"])


def update_user(username, **fields):
    """Change saved fields for one user, e.g. station, language or settings."""
    data = _load()
    key = username.lower()
    if key in data["users"]:
        data["users"][key].update(fields)
        _save(data)


def all_face_encodings():
    """Yields (username, encoding) for every stored face sample."""
    for key, user in _load()["users"].items():
        for encoding in user["face_encodings"]:
            yield key, encoding
