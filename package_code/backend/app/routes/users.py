from flask import Blueprint, request

from .. import db
from ..models import User
from ..utils.auth import role_required
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error


bp = Blueprint("users", __name__)


@bp.get("/users")
@role_required("admin")
def list_users():
    limit, offset = get_pagination_args(request)
    users = User.query.offset(offset).limit(limit).all()
    return ok([u.to_dict() for u in users])


@bp.put("/users/<int:user_id>")
@role_required("admin")
def update_user(user_id):
    data = request.get_json() or {}
    role = data.get("role")
    if role not in ("student", "teacher", "admin"):
        return error("invalid role")
    user = User.query.get(user_id)
    if not user:
        return error("user not found")
    user.role = role
    db.session.commit()
    return ok(user.to_dict())
