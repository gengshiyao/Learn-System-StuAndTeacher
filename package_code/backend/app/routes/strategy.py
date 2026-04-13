import json

from flask import Blueprint, request

from .. import db
from ..models import Course, TeacherStrategy
from ..utils.auth import role_required
from ..utils.response import ok, error


bp = Blueprint("strategy", __name__)


REQUIRED_FIELDS = {
    "mastery_threshold",
    "alpha_quiz",
    "beta_exercise",
    "gamma_time",
    "time_cap_min",
    "decay_enabled",
}


@bp.get("/strategy")
@role_required("teacher", "admin")
def get_strategy():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    strategy = TeacherStrategy.query.filter_by(course_id=course_id).first()
    return ok(strategy.to_dict() if strategy else None)


@bp.put("/strategy")
@role_required("teacher", "admin")
def update_strategy():
    data = request.get_json() or {}
    course_id = data.get("course_id")
    params_json = data.get("params_json")
    if not course_id or params_json is None:
        return error("course_id and params_json required")
    if not Course.query.get(course_id):
        return error("course not found")

    if isinstance(params_json, dict):
        params = params_json
        params_json = json.dumps(params_json)
    else:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError:
            return error("params_json must be valid JSON")

    missing = [key for key in REQUIRED_FIELDS if key not in params]
    if missing:
        return error("missing fields: " + ",".join(missing))

    strategy = TeacherStrategy.query.filter_by(course_id=course_id).first()
    if not strategy:
        strategy = TeacherStrategy(course_id=course_id, params_json=params_json)
        db.session.add(strategy)
    else:
        strategy.params_json = params_json
    db.session.commit()
    return ok(strategy.to_dict())
