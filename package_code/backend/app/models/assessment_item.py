from .. import db


class AssessmentItem(db.Model):
    __tablename__ = "assessment_item"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessment.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text)
    answer = db.Column(db.String(255))
    score = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "question": self.question,
            "options_json": self.options_json,
            "answer": self.answer,
            "score": self.score,
        }
