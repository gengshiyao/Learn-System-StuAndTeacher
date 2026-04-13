from .. import db


class KpPrereq(db.Model):
    __tablename__ = "kp_prereq"

    id = db.Column(db.Integer, primary_key=True)
    kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)
    prereq_kp_id = db.Column(db.Integer, db.ForeignKey("knowledge_point.id"), nullable=False)

    def to_dict(self):
        return {"id": self.id, "kp_id": self.kp_id, "prereq_kp_id": self.prereq_kp_id}
