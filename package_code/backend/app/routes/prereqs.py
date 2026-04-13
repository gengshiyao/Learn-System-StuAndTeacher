from collections import defaultdict, deque

from flask import Blueprint, request

from .. import db
from ..models import KnowledgePoint, KpPrereq
from ..utils.auth import role_required
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error


bp = Blueprint("prereqs", __name__)


def _has_path(start, target, adjacency):
    queue = deque([start])
    visited = set()
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        if node in visited:
            continue
        visited.add(node)
        for nxt in adjacency.get(node, []):
            if nxt not in visited:
                queue.append(nxt)
    return False


@bp.get("/prereqs")
def list_prereqs():
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return error("course_id required")
    limit, offset = get_pagination_args(request)
    prereqs = (
        KpPrereq.query.join(
            KnowledgePoint, KpPrereq.kp_id == KnowledgePoint.id
        )
        .filter(KnowledgePoint.course_id == course_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return ok([p.to_dict() for p in prereqs])


@bp.post("/prereqs")
@role_required("teacher", "admin")
def create_prereq():
    data = request.get_json() or {}
    kp_id = data.get("kp_id")
    prereq_kp_id = data.get("prereq_kp_id")
    if not kp_id or not prereq_kp_id:
        return error("kp_id and prereq_kp_id required")
    if kp_id == prereq_kp_id:
        return error("kp_id cannot equal prereq_kp_id")

    kp = KnowledgePoint.query.get(kp_id)
    prereq = KnowledgePoint.query.get(prereq_kp_id)
    if not kp or not prereq:
        return error("kp not found")
    if kp.course_id != prereq.course_id:
        return error("kp must be in same course")

    existing = KpPrereq.query.filter_by(kp_id=kp_id, prereq_kp_id=prereq_kp_id).first()
    if existing:
        return ok(existing.to_dict())

    all_edges = KpPrereq.query.join(
        KnowledgePoint, KpPrereq.kp_id == KnowledgePoint.id
    ).filter(KnowledgePoint.course_id == kp.course_id)

    adjacency = defaultdict(list)
    for edge in all_edges:
        adjacency[edge.prereq_kp_id].append(edge.kp_id)

    if _has_path(kp_id, prereq_kp_id, adjacency):
        return error("先修关系存在环，请教师端修复")

    prereq_edge = KpPrereq(kp_id=kp_id, prereq_kp_id=prereq_kp_id)
    db.session.add(prereq_edge)
    db.session.commit()
    return ok(prereq_edge.to_dict())


@bp.delete("/prereqs/<int:prereq_id>")
@role_required("teacher", "admin")
def delete_prereq(prereq_id):
    prereq = KpPrereq.query.get(prereq_id)
    if not prereq:
        return error("prereq not found")
    db.session.delete(prereq)
    db.session.commit()
    return ok(True)
