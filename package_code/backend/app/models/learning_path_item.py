from .. import db


class LearningPathItem(db.Model):
    __tablename__ = "learning_path_item"

    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey("learning_path.id"), nullable=False)
    seq = db.Column(db.Integer, nullable=False)
    kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)
    required_flag = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "path_id": self.path_id,
            "seq": self.seq,
            "kp_id": self.kp_id,
            "required_flag": self.required_flag,
        }
