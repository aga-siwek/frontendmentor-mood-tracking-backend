from src.database import db


class Feel(db.Model):
    __tablename__ = "feel"
    feel_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_id = db.Column(db.Integer, db.ForeignKey("log.log_id"))
    feel_name = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            "feel_id": self.feel_id,
            "log_id": self.log_id,
            "feel_name": self.feel_name
        }