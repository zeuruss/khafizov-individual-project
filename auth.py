import csv
import hashlib
import secrets
from pathlib import Path
from fastapi import Request, Response

USERS_PATH = Path(__file__).with_name('users.csv')
SESSIONS = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    users = {}
    if USERS_PATH.exists():
        with open(USERS_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users[row['username']] = row['password_hash']
    return users


def check_credentials(username: str, password: str) -> bool:
    users = load_users()
    if username in users and users[username] == hash_password(password):
        return True
    return False


def login_user(response: Response, username: str):
    session_id = secrets.token_hex(16)
    SESSIONS[session_id] = username
    response.set_cookie('session_id', session_id)
    return session_id


def get_current_user(request: Request):
    session_id = request.cookies.get('session_id')
    if not session_id:
        return None
    return SESSIONS.get(session_id)


def logout_user(request: Request, response: Response):
    session_id = request.cookies.get('session_id')
    if session_id is not None:
        SESSIONS.pop(session_id, None)
    response.delete_cookie('session_id')