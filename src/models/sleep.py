from src.database import db

class Sleep(db.Model):
    __tablename__ = "sleep"
    sleep_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_id = db.Column(db.Integer, db.ForeignKey("log.log_id"))
    sleep_time = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
          "sleep_id": self.sleep_id,
            "log_id": self.log_id,
            "sleep_time": self.sleep_time
        }
