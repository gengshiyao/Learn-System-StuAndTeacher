from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..models import KnowledgePoint, Mastery
from ..utils.auth import get_current_user
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error


bp = Blueprint("mastery", __name__)


@bp.get("/mastery")
@jwt_required()
def list_mastery():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    user_id = request.args.get("user_id", type=int)
    current = get_current_user()
    if current.role == "student":
        user_id = current.id
    elif not user_id:
        return error("user_id required")

    limit, offset = get_pagination_args(request)
    mastery_rows = (
        Mastery.query.join(KnowledgePoint, Mastery.kp_id == KnowledgePoint.id)
        .filter(Mastery.user_id == user_id, KnowledgePoint.course_id == course_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ok([m.to_dict() for m in mastery_rows])
