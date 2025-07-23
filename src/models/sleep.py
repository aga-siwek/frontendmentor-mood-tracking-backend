from src.database import db

class Sleep(db.Model):
    __tablename__ = "sleep"
    sleep_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_id = db.Column(db.Integer, db.ForeignKey("log.log_id"))
    sleep_time_scale = db.Column(db.Integer, nullable=False)
    sleep_time_name = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
          "sleep_id": self.sleep_id,
            "log_id": self.log_id,
            "sleep_time_scale": self.sleep_time_scale,
            "sleep_time_name": self.sleep_time_name
        }
