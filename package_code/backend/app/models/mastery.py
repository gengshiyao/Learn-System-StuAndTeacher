from datetime import datetime

from .. import db


class Mastery(db.Model):
    __tablename__ = "mastery"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)
    mastery_value = db.Column(db.Numeric(4, 3), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "kp_id": self.kp_id,
            "mastery_value": float(self.mastery_value),
            "updated_at": self.updated_at.isoformat(),
        }
