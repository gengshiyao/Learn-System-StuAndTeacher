from datetime import datetime

from .. import db


class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)
    type = db.Column(db.Enum("quiz"), nullable=False, default="quiz")
    total_score = db.Column(db.Integer, nullable=False, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "kp_id": self.kp_id,
            "type": self.type,
            "total_score": self.total_score,
        }
