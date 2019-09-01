from functools import wraps

from flask import request, abort
from routes.helper import cache, current_user
from utils import log
import flask as f


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        if cache.exists(token):
            user_id = int(cache.get(token).decode(encoding='utf-8'))
            u = current_user()
            if user_id == u.id:
                cache.delete(token)
                return f(*args, **kwargs)
        else:
            abort(401)
    return wrapper


def login_required(route_function):
    @wraps(route_function)
    def function():
        log('login_required', route_function)
        u = current_user()
        if u.is_guest():
            log('login_required is_guest', u)
            return f.redirect('/login/view')
        else:
            return route_function()
    return function
