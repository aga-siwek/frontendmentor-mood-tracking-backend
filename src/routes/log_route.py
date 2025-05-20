from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from src.services import log_service

log_app = Blueprint("logs", __name__)

@log_app.route("/logs/", methods=["POST"])
@jwt_required()
def add_log():
    post_data = request.json
    feels = post_data["feel"]
    mood = post_data["mood"]
    sleep = post_data["sleep"]
    description = post_data["description"]
    return log_service.create_log(feels, mood, sleep, description)

@log_app.route("/logs/", methods=["GET"])
@jwt_required()
def list_logs():
    return log_service.get_all_logs()

@log_app.route("/logs/<log_id>", methods=["GET"])
@jwt_required()
def list_single_log(log_id):
    return log_service.get_single_log(log_id)

@log_app.route("/logs/<log_id>", methods=["PUT"])
@jwt_required()
def change_single_log(log_id):
    put_data = request.json
    return log_service.change_single_log(put_data, log_id)

@log_app.route("/logs/<log_id>", methods=["DELETE"])
@jwt_required()
def delete_single_log(log_id):
    return log_service.delete_single_log(log_id)

