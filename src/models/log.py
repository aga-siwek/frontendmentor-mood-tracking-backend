from src.database import db
from datetime import datetime


class Log(db.Model):
    __tablename__ = "log"
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "created_at": self.created_at
        }

