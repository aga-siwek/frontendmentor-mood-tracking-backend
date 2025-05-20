from flask import Flask
from flask_jwt_extended import JWTManager
from src.database import db
from src.bycrypt import bcrypt
from src.routes.user_route import user_app
from src.routes.log_route import log_app


app = Flask(__name__)
app.register_blueprint(log_app)
app.register_blueprint(user_app)
app.config.from_object("config.Config")
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager()
jwt.init_app(app)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)


