import json

from collections import defaultdict

from .. import db
from ..models import KnowledgePoint, KpPrereq, LearningPath, LearningPathItem, Mastery
from .mastery_service import get_strategy_params


class PathGenerationError(Exception):
    pass


def generate_learning_path(user_id, course_id, time_budget_per_week_minutes=300):
    kps = KnowledgePoint.query.filter_by(course_id=course_id).all()
    if not kps:
        raise PathGenerationError("course has no knowledge points")

    mastery_records = Mastery.query.filter_by(user_id=user_id).all()
    mastery_map = {m.kp_id: float(m.mastery_value) for m in mastery_records}

    params = get_strategy_params(course_id)
    threshold = params["mastery_threshold"]

    weak = {kp.id for kp in kps if mastery_map.get(kp.id, 0.2) < threshold}
    if not weak:
        sorted_kps = sorted(kps, key=lambda kp: (kp.difficulty, kp.est_minutes, kp.id))
        chosen = sorted_kps[:10]
        sequence = [kp.id for kp in chosen]
        required_flags = {kp.id: 1 for kp in chosen}
        return _persist_path(
            user_id, course_id, sequence, required_flags, params, time_budget_per_week_minutes
        )

    prereqs = KpPrereq.query.join(
        KnowledgePoint, KpPrereq.kp_id == KnowledgePoint.id
    ).filter(KnowledgePoint.course_id == course_id)
    prereq_map = defaultdict(list)
    for pr in prereqs:
        prereq_map[pr.kp_id].append(pr.prereq_kp_id)

    closure = set()

    def dfs(kp_id):
        if kp_id in closure:
            return
        closure.add(kp_id)
        for pre in prereq_map.get(kp_id, []):
            dfs(pre)

    for kp_id in weak:
        dfs(kp_id)

    closure_kps = {kp.id: kp for kp in kps if kp.id in closure}

    edges = []
    indegree = {kp_id: 0 for kp_id in closure_kps}
    graph = defaultdict(list)
    for pr in prereqs:
        if pr.kp_id in closure_kps and pr.prereq_kp_id in closure_kps:
            graph[pr.prereq_kp_id].append(pr.kp_id)
            indegree[pr.kp_id] += 1
            edges.append((pr.prereq_kp_id, pr.kp_id))

    sequence = []
    remaining = set(closure_kps.keys())
    while remaining:
        zeros = [kp_id for kp_id in remaining if indegree[kp_id] == 0]
        if not zeros:
            raise PathGenerationError("先修关系存在环，请教师端修复")
        zeros.sort(
            key=lambda kp_id: (
                closure_kps[kp_id].difficulty,
                mastery_map.get(kp_id, 0.2),
                closure_kps[kp_id].est_minutes,
            )
        )
        for kp_id in zeros:
            sequence.append(kp_id)
            remaining.remove(kp_id)
            for nxt in graph.get(kp_id, []):
                indegree[nxt] -= 1

    required_flags = {kp_id: 1 if kp_id in weak else 0 for kp_id in sequence}
    return _persist_path(
        user_id, course_id, sequence, required_flags, params, time_budget_per_week_minutes
    )


def _persist_path(user_id, course_id, sequence, required_flags, params, time_budget_per_week_minutes):
    last_path = (
        LearningPath.query.filter_by(user_id=user_id, course_id=course_id)
        .order_by(LearningPath.version.desc())
        .first()
    )
    version = 1 if not last_path else last_path.version + 1

    path = LearningPath(
        user_id=user_id,
        course_id=course_id,
        version=version,
        strategy_snapshot=json.dumps(params),
    )
    db.session.add(path)
    db.session.flush()

    items = []
    for idx, kp_id in enumerate(sequence, start=1):
        item = LearningPathItem(
            path_id=path.id, seq=idx, kp_id=kp_id, required_flag=required_flags[kp_id]
        )
        db.session.add(item)
        items.append(item)

    db.session.commit()

    weeks = _split_weeks(sequence, course_id, time_budget_per_week_minutes)
    return path, items, weeks


def _split_weeks(sequence, course_id, time_budget_per_week_minutes=300):
    kps = KnowledgePoint.query.filter(
        KnowledgePoint.course_id == course_id, KnowledgePoint.id.in_(sequence)
    ).all()
    kp_map = {kp.id: kp for kp in kps}
    weeks = []
    current = []
    total = 0
    week_index = 1
    for kp_id in sequence:
        est = kp_map.get(kp_id).est_minutes if kp_map.get(kp_id) else 0
        if current and total + est > time_budget_per_week_minutes:
            weeks.append({"week": week_index, "kp_ids": current})
            week_index += 1
            current = []
            total = 0
        current.append(kp_id)
        total += est
    if current:
        weeks.append({"week": week_index, "kp_ids": current})
    return weeks
