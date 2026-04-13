from flask import Blueprint, request

from .. import db
from ..models import KnowledgePoint, Resource
from ..utils.auth import role_required
from ..utils.pagination import get_pagination_args
from ..utils.response import ok, error


bp = Blueprint("resources", __name__)


@bp.get("/resources")
def list_resources():
    kp_id = request.args.get("kp_id", type=int)
    if not kp_id:
        return error("kp_id required")
    limit, offset = get_pagination_args(request)
    resources = Resource.query.filter_by(kp_id=kp_id).offset(offset).limit(limit).all()
    return ok([r.to_dict() for r in resources])


@bp.post("/resources")
@role_required("teacher", "admin")
def create_resource():
    data = request.get_json() or {}
    kp_id = data.get("kp_id")
    if not kp_id:
        return error("kp_id required")
    if not KnowledgePoint.query.get(kp_id):
        return error("kp not found")
    required = ["type", "title", "url", "difficulty", "est_minutes"]
    for field in required:
        if data.get(field) is None:
            return error(f"{field} required")
    resource = Resource(
        kp_id=kp_id,
        type=data.get("type"),
        title=data.get("title"),
        url=data.get("url"),
        difficulty=int(data.get("difficulty")),
        est_minutes=int(data.get("est_minutes")),
    )
    db.session.add(resource)
    db.session.commit()
    return ok(resource.to_dict())


@bp.put("/resources/<int:resource_id>")
@role_required("teacher", "admin")
def update_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        return error("resource not found")
    data = request.get_json() or {}
    for field in ["type", "title", "url", "difficulty", "est_minutes"]:
        if field in data:
            setattr(resource, field, data.get(field))
    db.session.commit()
    return ok(resource.to_dict())


@bp.delete("/resources/<int:resource_id>")
@role_required("teacher", "admin")
def delete_resource(resource_id):
    resource = Resource.query.get(resource_id)
    if not resource:
        return error("resource not found")
    db.session.delete(resource)
    db.session.commit()
    return ok(True)
