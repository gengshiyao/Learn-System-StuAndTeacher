import csv
import io

from flask import Blueprint, request, Response

from ..models import (
    Assessment,
    AssessmentRecord,
    KnowledgePoint,
    LearningEvent,
    LearningPath,
    LearningPathItem,
    Mastery,
)
from ..utils.auth import role_required
from ..utils.response import error


bp = Blueprint("export", __name__)


def _csv_response(filename, rows, headers):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    resp = Response(output.getvalue(), mimetype="text/csv")
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return resp


@bp.get("/export/events")
@role_required("admin")
def export_events():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    events = (
        LearningEvent.query.join(KnowledgePoint, LearningEvent.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id)
        .all()
    )
    rows = [
        [e.user_id, e.kp_id, e.event_type, e.duration_sec, e.ts.isoformat()]
        for e in events
    ]
    return _csv_response(
        "learning_events.csv", rows, ["user_id", "kp_id", "event_type", "duration_sec", "ts"]
    )


@bp.get("/export/records")
@role_required("admin")
def export_records():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    records = (
        AssessmentRecord.query.join(Assessment, AssessmentRecord.assessment_id == Assessment.id)
        .join(KnowledgePoint, Assessment.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id)
        .all()
    )
    rows = [
        [r.user_id, r.assessment_id, r.score, r.submit_time.isoformat()]
        for r in records
    ]
    return _csv_response(
        "assessment_records.csv", rows, ["user_id", "assessment_id", "score", "submit_time"]
    )


@bp.get("/export/mastery")
@role_required("admin")
def export_mastery():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    rows = (
        Mastery.query.join(KnowledgePoint, Mastery.kp_id == KnowledgePoint.id)
        .filter(KnowledgePoint.course_id == course_id)
        .all()
    )
    data = [
        [m.user_id, m.kp_id, float(m.mastery_value), m.updated_at.isoformat()] for m in rows
    ]
    return _csv_response(
        "mastery.csv", data, ["user_id", "kp_id", "mastery_value", "updated_at"]
    )


@bp.get("/export/paths")
@role_required("admin")
def export_paths():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    paths = LearningPath.query.filter_by(course_id=course_id).all()
    path_ids = [p.id for p in paths]
    if not path_ids:
        return _csv_response(
            "paths.csv",
            [],
            ["user_id", "course_id", "version", "kp_id", "seq", "required_flag"],
        )
    items = LearningPathItem.query.filter(LearningPathItem.path_id.in_(path_ids)).all()
    path_map = {p.id: p for p in paths}
    rows = []
    for item in items:
        path = path_map.get(item.path_id)
        if not path:
            continue
        rows.append([path.user_id, path.course_id, path.version, item.kp_id, item.seq, item.required_flag])
    return _csv_response(
        "paths.csv",
        rows,
        ["user_id", "course_id", "version", "kp_id", "seq", "required_flag"],
    )
