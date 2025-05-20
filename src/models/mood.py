from src.database import db


class Mood(db.Model):
    __tablename__ = "mood"
    mood_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_id = db.Column(db.Integer, db.ForeignKey("log.log_id"))
    mood_name = db.Column(db.String(128), nullable=False)

    def to_dict(self):
        return {
            "mood_id": self.mood_id,
            "log_id": self.log_id,
            "mood_name": self.mood_name
        }
