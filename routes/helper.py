import uuid

import redis
from flask import request

from models.user import User


def current_user():
    if 'session_id' in request.cookies:
        session_id = request.cookies['session_id']
    else:
        return User.guest()
    uid = get_session(session_id)
    u: User = User.one(id=uid)
    return u


def add_session(session_id, user_id):
    k = session_id
    v = user_id
    cache.set(k, v)
    return k


def get_session(session_id):
    k = session_id
    if cache.exists(k):
        user_id = int(cache.get(k).decode(encoding='utf-8'))
        return user_id


def new_csrf_token():
    u: User = current_user()
    token = str(uuid.uuid4())
    k = 'csrf_token_{}'.format(token)
    v = u.id
    cache.set(k, v)
    return k


def new_reset_password_token(user_id):
    token = str(uuid.uuid4())
    k = 'reset_password_token_{}'.format(token)
    v = user_id
    cache.set(k, v)
    return k


cache = redis.StrictRedis()
