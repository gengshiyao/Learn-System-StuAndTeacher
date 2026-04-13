from flask import Blueprint, request

from .. import db
from ..models import KnowledgePoint, LearningEvent, Resource
from ..utils.auth import role_required, get_current_user
from ..utils.response import ok, error
from ..services.mastery_service import update_mastery_for_user_kp


bp = Blueprint("learning_events", __name__)


@bp.post("/learning_events")
@role_required("student")
def create_learning_event():
    data = request.get_json() or {}
    kp_id = data.get("kp_id")
    event_type = data.get("event_type")
    duration_sec = data.get("duration_sec")
    resource_id = data.get("resource_id")
    if kp_id is None or event_type is None or duration_sec is None:
        return error("kp_id, event_type, duration_sec required")
    if not KnowledgePoint.query.get(kp_id):
        return error("kp not found")
    if resource_id and not Resource.query.get(resource_id):
        return error("resource not found")
    user = get_current_user()
    event = LearningEvent(
        user_id=user.id,
        kp_id=kp_id,
        resource_id=resource_id,
        event_type=event_type,
        duration_sec=int(duration_sec),
    )
    db.session.add(event)
    db.session.commit()
    update_mastery_for_user_kp(user.id, kp_id)
    return ok(event.to_dict())
