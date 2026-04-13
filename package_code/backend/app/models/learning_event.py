from datetime import datetime

from .. import db


class LearningEvent(db.Model):
    __tablename__ = "learning_event"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    event_type = db.Column(db.Enum("view", "complete_exercise", "complete_resource"), nullable=False)
    duration_sec = db.Column(db.Integer, nullable=False)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "kp_id": self.kp_id,
            "resource_id": self.resource_id,
            "event_type": self.event_type,
            "duration_sec": self.duration_sec,
            "ts": self.ts.isoformat(),
        }
