from datetime import datetime

from .. import db


class KnowledgePoint(db.Model):
    __tablename__ = "knowledge_point"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    est_minutes = db.Column(db.Integer, nullable=False)
    tags = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "name": self.name,
            "difficulty": self.difficulty,
            "est_minutes": self.est_minutes,
            "tags": self.tags,
            "description": self.description,
        }
