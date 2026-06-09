import os
from flask import Blueprint
from src.services import demo_service
from src.limiter import limiter

demo_app = Blueprint("demo", __name__)


@demo_app.route("/demo/login", methods=["POST"])
@limiter.limit("100 per hour" if os.environ.get("FLASK_ENV") == "development" else "15 per hour")
def demo_login():
    return demo_service.create_demo_account()
