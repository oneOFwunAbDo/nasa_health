"""
Local user storage for the Space Health app.

Everything is saved in users.json next to this file:
  first name, last name, username, password (salted + hashed, never plain text),
  face encodings (numbers describing the face, NOT photos), station, language.

The admin page will read from this same file later.
"""

import datetime
import hashlib
import hmac
import json
import secrets
from pathlib import Path

DATA_FILE = Path(__file__).with_name("users.json")


def _load():
    if not DATA_FILE.exists():
        return {"users": {}}
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _save(data):
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()


def username_taken(username):
    return username.lower() in _load()["users"]


def get_user(username):
    return _load()["users"].get(username.lower())


def create_user(first_name, last_name, username, password,
                face_encodings, station, language):
    data = _load()
    key = username.lower()
    if key in data["users"]:
        raise ValueError("username already taken")

    salt = secrets.token_bytes(16)
    data["users"][key] = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "password_salt": salt.hex(),
        "password_hash": _hash_password(password, salt),
        "face_encodings": face_encodings,   # list of 128-number lists
        "station": station,
        "language": language,
        "tasks": {},  # "YYYY-MM-DD" -> tasks completed that day; empty at sign-up
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
    """Change saved fields for one user, e.g. station or language from settings."""
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