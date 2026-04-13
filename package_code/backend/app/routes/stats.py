from datetime import datetime, timedelta

from flask import Blueprint, request

from .. import db
from ..models import Assessment, AssessmentRecord, KnowledgePoint, LearningEvent, Mastery
from ..services.mastery_service import get_strategy_params
from ..utils.auth import role_required
from ..utils.response import ok, error


bp = Blueprint("stats", __name__)


@bp.get("/stats")
@role_required("teacher", "admin")
def get_stats():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")

    total_events = (
        LearningEvent.query.join(KnowledgePoint, LearningEvent.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id)
        .count()
    )

    avg_score = (
        db.session.query(db.func.avg(AssessmentRecord.score))
        .join(Assessment, AssessmentRecord.assessment_id == Assessment.id)
        .join(KnowledgePoint, Assessment.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id)
        .scalar()
        or 0
    )

    params = get_strategy_params(course_id)
    threshold = params["mastery_threshold"]

    total_kps = KnowledgePoint.query.filter_by(course_id=course_id).count()
    mastered = (
        Mastery.query.join(KnowledgePoint, Mastery.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id, Mastery.mastery_value >= threshold)
        .count()
    )

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = (
        db.session.query(LearningEvent.user_id)
        .join(KnowledgePoint, LearningEvent.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id, LearningEvent.ts >= seven_days_ago)
        .distinct()
        .count()
    )

    rate = 0 if total_kps == 0 else mastered / total_kps
    return ok(
        {
            "event_count": total_events,
            "avg_score": float(avg_score),
            "mastery_rate": rate,
            "active_users_7d": active_users,
        }
    )
