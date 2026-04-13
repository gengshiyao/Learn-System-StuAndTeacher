from flask import Blueprint, request

from ..models import Course, LearningPath, LearningPathItem
from ..services.path_service import generate_learning_path, PathGenerationError
from ..utils.auth import role_required, get_current_user
from ..utils.response import ok, error


bp = Blueprint("paths", __name__)


@bp.post("/paths/generate")
@role_required("student")
def generate_path():
    data = request.get_json() or {}
    course_id = data.get("course_id")
    if not course_id:
        return error("course_id required")
    if not Course.query.get(course_id):
        return error("course not found")
    time_budget = data.get("time_budget_per_week_minutes", 300)
    user = get_current_user()
    try:
        path, items, weeks = generate_learning_path(user.id, course_id, int(time_budget))
    except PathGenerationError as exc:
        return error(str(exc))
    return ok(
        {
            "path_id": path.id,
            "version": path.version,
            "items": [i.to_dict() for i in items],
            "weeks": weeks,
        }
    )


@bp.get("/paths/latest")
@role_required("student")
def latest_path():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    user = get_current_user()
    path = (
        LearningPath.query.filter_by(user_id=user.id, course_id=course_id)
        .order_by(LearningPath.version.desc())
        .first()
    )
    if not path:
        return ok(None)
    items = LearningPathItem.query.filter_by(path_id=path.id).order_by(LearningPathItem.seq).all()
    return ok({"path": path.to_dict(), "items": [i.to_dict() for i in items]})


@bp.get("/paths/<int:path_id>")
@role_required("student")
def get_path(path_id):
    user = get_current_user()
    path = LearningPath.query.get(path_id)
    if not path or path.user_id != user.id:
        return error("path not found")
    items = LearningPathItem.query.filter_by(path_id=path.id).order_by(LearningPathItem.seq).all()
    return ok({"path": path.to_dict(), "items": [i.to_dict() for i in items]})
