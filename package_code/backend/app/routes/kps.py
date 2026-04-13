from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .. import db
from ..models import Course, KnowledgePoint
from ..utils.auth import role_required
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error


bp = Blueprint("kps", __name__)


@bp.get("/kps")
@jwt_required(optional=True)
def list_kps():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    limit, offset = get_pagination_args(request)
    kps = (
        KnowledgePoint.query.filter_by(course_id=course_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ok([kp.to_dict() for kp in kps])


@bp.post("/kps")
@role_required("teacher", "admin")
def create_kp():
    data = request.get_json() or {}
    course_id = data.get("course_id")
    if not course_id:
        return error("course_id required")
    course = Course.query.get(course_id)
    if not course:
        return error("course not found")

    required = ["name", "difficulty", "est_minutes"]
    for field in required:
        if data.get(field) is None:
            return error(f"{field} required")

    kp = KnowledgePoint(
        course_id=course_id,
        name=data.get("name"),
        difficulty=int(data.get("difficulty")),
        est_minutes=int(data.get("est_minutes")),
        tags=data.get("tags"),
        description=data.get("description"),
    )
    db.session.add(kp)
    db.session.commit()
    return ok(kp.to_dict())


@bp.put("/kps/<int:kp_id>")
@role_required("teacher", "admin")
def update_kp(kp_id):
    kp = KnowledgePoint.query.get(kp_id)
    if not kp:
        return error("kp not found")
    data = request.get_json() or {}
    for field in ["name", "difficulty", "est_minutes", "tags", "description"]:
        if field in data:
            setattr(kp, field, data.get(field))
    db.session.commit()
    return ok(kp.to_dict())


@bp.delete("/kps/<int:kp_id>")
@role_required("teacher", "admin")
def delete_kp(kp_id):
    kp = KnowledgePoint.query.get(kp_id)
    if not kp:
        return error("kp not found")
    db.session.delete(kp)
    db.session.commit()
    return ok(True)
