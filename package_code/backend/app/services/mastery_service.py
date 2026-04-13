import json

from sqlalchemy import func

from .. import db
from ..models import (
    Assessment,
    AssessmentRecord,
    KnowledgePoint,
    LearningEvent,
    Mastery,
    TeacherStrategy,
)


DEFAULT_PARAMS = {
    "mastery_threshold": 0.7,
    "alpha_quiz": 0.50,
    "beta_exercise": 0.30,
    "gamma_time": 0.20,
    "time_cap_min": 60,
    "decay_enabled": False,
}


def get_strategy_params(course_id):
    strategy = TeacherStrategy.query.filter_by(course_id=course_id).first()
    if not strategy:
        return DEFAULT_PARAMS.copy()
    try:
        data = json.loads(strategy.params_json)
    except json.JSONDecodeError:
        return DEFAULT_PARAMS.copy()
    merged = DEFAULT_PARAMS.copy()
    merged.update({k: data.get(k, v) for k, v in merged.items()})
    return merged


def update_mastery_for_user_kp(user_id, kp_id):
    kp = KnowledgePoint.query.get(kp_id)
    if not kp:
        return None
    params = get_strategy_params(kp.course_id)

    total_seconds = (
        db.session.query(func.coalesce(func.sum(LearningEvent.duration_sec), 0))
        .filter_by(user_id=user_id, kp_id=kp_id)
        .scalar()
    )
    total_seconds = float(total_seconds or 0)
    total_minutes = total_seconds / 60.0
    time_norm = min(total_minutes, params["time_cap_min"]) / params["time_cap_min"]

    has_exercise = (
        db.session.query(LearningEvent.id)
        .filter_by(user_id=user_id, kp_id=kp_id, event_type="complete_exercise")
        .first()
        is not None
    )
    exercise_norm = 1 if has_exercise else 0

    latest_record = (
        db.session.query(AssessmentRecord)
        .join(Assessment, AssessmentRecord.assessment_id == Assessment.id)
        .filter(AssessmentRecord.user_id == user_id, Assessment.kp_id == kp_id)
        .order_by(AssessmentRecord.submit_time.desc())
        .first()
    )
    quiz_score_norm = 0
    if latest_record:
        quiz_score_norm = max(0, min(latest_record.score, 100)) / 100.0

    mastery_new = (
        0.2
        + params["alpha_quiz"] * quiz_score_norm
        + params["beta_exercise"] * exercise_norm
        + params["gamma_time"] * time_norm
    )
    mastery_new = max(0, min(mastery_new, 1))

    record = Mastery.query.filter_by(user_id=user_id, kp_id=kp_id).first()
    if not record:
        record = Mastery(user_id=user_id, kp_id=kp_id, mastery_value=mastery_new)
        db.session.add(record)
    else:
        record.mastery_value = mastery_new

    db.session.commit()
    return record
