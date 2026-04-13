from datetime import datetime

from .. import db


class LearningPath(db.Model):
    __tablename__ = "learning_path"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    strategy_snapshot = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "version": self.version,
            "strategy_snapshot": self.strategy_snapshot,
            "created_at": self.created_at.isoformat(),
        }
