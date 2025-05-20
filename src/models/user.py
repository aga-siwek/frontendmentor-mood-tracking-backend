from src.database import db

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(190), unique=True, nullable=False)
    user_password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_email": self.user_email,
            "is_admin": self.is_admin,
        }

    def is_administrator(self):
        return self.is_admin == 1

