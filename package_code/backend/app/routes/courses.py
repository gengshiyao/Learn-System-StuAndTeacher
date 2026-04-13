from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Course
from ..utils.auth import role_required
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error


bp = Blueprint("courses", __name__)


@bp.get("/courses")
@jwt_required(optional=True)
def list_courses():
    limit, offset = get_pagination_args(request)
    courses = Course.query.offset(offset).limit(limit).all()
    return ok([c.to_dict() for c in courses])


@bp.post("/courses")
@role_required("teacher", "admin")
def create_course():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return error("name required")
    course = Course(name=name, description=data.get("description"))
    db.session.add(course)
    db.session.commit()
    return ok(course.to_dict())
