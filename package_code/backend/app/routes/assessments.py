from flask import Blueprint, request

from .. import db
from ..models import Assessment, AssessmentRecord, KnowledgePoint
from ..utils.auth import role_required, get_current_user
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error
from ..services.mastery_service import update_mastery_for_user_kp


bp = Blueprint("assessments", __name__)


@bp.get("/assessments")
def list_assessments():
    kp_id = request.args.get("kp_id", type=int)
    if not kp_id:
        return error("kp_id required")
    limit, offset = get_pagination_args(request)
    items = Assessment.query.filter_by(kp_id=kp_id).offset(offset).limit(limit).all()
    return ok([a.to_dict() for a in items])


@bp.post("/assessments")
@role_required("teacher", "admin")
def create_assessment():
    data = request.get_json() or {}
    kp_id = data.get("kp_id")
    if not kp_id:
        return error("kp_id required")
    if not KnowledgePoint.query.get(kp_id):
        return error("kp not found")
    assessment = Assessment(kp_id=kp_id, type="quiz", total_score=data.get("total_score", 100))
    db.session.add(assessment)
    db.session.commit()
    return ok(assessment.to_dict())


@bp.post("/assessment_records")
@role_required("student")
def create_assessment_record():
    data = request.get_json() or {}
    assessment_id = data.get("assessment_id")
    score = data.get("score")
    if assessment_id is None or score is None:
        return error("assessment_id and score required")
    assessment = Assessment.query.get(assessment_id)
    if not assessment:
        return error("assessment not found")
    user = get_current_user()
    record = AssessmentRecord(user_id=user.id, assessment_id=assessment_id, score=int(score))
    db.session.add(record)
    db.session.commit()
    update_mastery_for_user_kp(user.id, assessment.kp_id)
    return ok(record.to_dict())
