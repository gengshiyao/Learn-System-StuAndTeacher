from datetime import datetime

from .. import db


class TeacherStrategy(db.Model):
    __tablename__ = "teacher_strategy"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    params_json = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "course_id": self.course_id,
            "params_json": self.params_json,
            "updated_at": self.updated_at.isoformat(),
        }
