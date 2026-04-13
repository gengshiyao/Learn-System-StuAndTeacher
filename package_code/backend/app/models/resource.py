from datetime import datetime

from .. import db


class Resource(db.Model):
    __tablename__ = "resource"

    id = db.Column(db.Integer, primary_key=True)
    kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)
    type = db.Column(db.Enum("video", "doc", "exercise", "quiz"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    est_minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "kp_id": self.kp_id,
            "type": self.type,
            "title": self.title,
            "url": self.url,
            "difficulty": self.difficulty,
            "est_minutes": self.est_minutes,
        }
