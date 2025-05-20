from src.database import db


class Description(db.Model):
    __tablename__ = "description"
    description_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_id = db.Column(db.Integer, db.ForeignKey("log.log_id"))
    description = db.Column(db.String(), nullable=False)

    def to_dict(self):
        return {
            "description_id": self.description_id,
            "log_id": self.log_id,
            "description": self.description
        }