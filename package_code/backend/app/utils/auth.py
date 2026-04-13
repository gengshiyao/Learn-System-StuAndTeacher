from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from ..models import User


def get_current_identity():
    return get_jwt_identity()


def get_current_user():
    identity = get_jwt_identity()
    if not identity:
        return None
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        return None
    if not user_id:
        return None
    return User.query.get(user_id)


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt() or {}
            role = claims.get("role")
            if role not in roles:
                from .response import error

                return error("permission denied", code=403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
