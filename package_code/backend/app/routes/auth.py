from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required

from .. import db
from ..models import User
from ..utils.response import ok, error
from ..utils.auth import get_current_user


bp = Blueprint("auth", __name__)


@bp.post("/register")
@jwt_required(optional=True)
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")
    if not username or not password:
        return error("username and password required")
    if User.query.filter_by(username=username).first():
        return error("username already exists")

    user = User(username=username)
    user.set_password(password)

    if role:
        current = None
        try:
            current = get_current_user()
        except Exception:
            current = None
        if current and current.role == "admin":
            user.role = role
        else:
            user.role = "student"

    db.session.add(user)
    db.session.commit()
    return ok({"id": user.id, "username": user.username, "role": user.role})


@bp.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return error("username and password required")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error("invalid credentials", code=401)
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return ok({"token": token, "user": user.to_dict()})


@bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    if not user:
        return error("user not found", code=404)
    return ok(user.to_dict())
