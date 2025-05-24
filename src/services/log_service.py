from flask_jwt_extended import get_jwt_identity

from src.database import db
from src.models.log import Log
from src.models.user import User
from src.models.feel import Feel
from src.models.mood import Mood
from src.models.sleep import Sleep
from src.models.description import Description
from flask import jsonify


def get_current_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(user_id=current_user).first()
    return user


def get_all_logs():
    logged_user = get_current_user()
    if not logged_user:
        return jsonify({"description": "not user found"})
    if not logged_user.is_administrator():
        return jsonify({"description": "Unauthorized"}), 401
    logs = Log.query.all()
    logs_dict = [log.to_dict() for log in logs]
    return (logs_dict, 200)


def create_log(feels, mood, sleep, description):
    logged_user = get_current_user()

    if not logged_user:
        return jsonify({"description": "not user found"}, 401)

    new_log = Log(
        user_id=logged_user.user_id)
    db.session.add(new_log)
    db.session.commit()

    new_description = Description(
        log_id=new_log.log_id,
        description=description
    )

    db.session.add(new_description)
    db.session.commit()

    new_mood = Mood(
        log_id=new_log.log_id,
        mood_name=mood
    )
    db.session.add(new_mood)
    db.session.commit()

    new_sleep = Sleep(
        log_id=new_log.log_id,
        sleep_time=sleep
    )
    db.session.add(new_sleep)
    db.session.commit()

    for feel in feels:
        new_feel = Feel(
            log_id=new_log.log_id,
            feel_name=feel
        )
        db.session.add(new_feel)
        db.session.commit()

    return jsonify({"new_log": new_log.to_dict(), "new_description": new_description.to_dict()}, 200)


def get_single_log(log_id):
    logged_user = get_current_user()
    searched_log = Log.query.get(log_id)
    user_id = searched_log.user_id
    searched_user = User.query.get(user_id)
    if logged_user != searched_user:
        if not logged_user.is_administrator():
            return jsonify({"description": "Unauthorized"}), 401

    return (searched_log.to_dict(), 200)



def change_single_log(data, log_id):
    logged_user = get_current_user()
    changed_log = Log.query.get(log_id)
    new_log_information = {}


    if not logged_user:
        return jsonify({"description": "not user found"}, 404)
    if not changed_log:
        return jsonify({"description": "not log found"}, 404)

    new_log_information["log_id"] = log_id
    user_id = changed_log.user_id
    searched_user = User.query.get(user_id)

    if logged_user != searched_user:
        if not logged_user.is_administrator():
            return jsonify({"description": "Unauthorized"}), 401

    if "description" in data.keys():
        current_description = Description.query.filter_by(log_id=log_id).first()
        current_description.description = data["description"]
        db.session.commit()
        new_log_information["description"] = current_description.to_dict()

    if "mood" in data.keys():
        current_mood = Mood.query.filter_by(log_id=log_id).first()
        current_mood.mood_name = data["mood"]
        db.session.commit()
        new_log_information["mood"] = current_mood.to_dict()

    if "sleep" in data.keys():
        current_sleep = Sleep.query.filter_by(log_id=log_id).first()
        current_sleep.sleep_time = data["sleep"]
        db.session.commit()
        new_log_information["sleep"] = current_mood.to_dict()

    if "feel" in data.keys():
        if data["feel"]:
            Feel.query.filter_by(log_id=log_id).delete()
            db.session.commit()
            feels = data["feel"]
            for feel in feels:
                new_feel = Feel(
                    log_id=log_id,
                    feel_name = feel
                )
                db.session.add(new_feel)
                db.session.commit()
                new_log_information["feel"] = feels

    return (new_log_information, 200)

def delete_single_log(log_id):
    logged_user = get_current_user()
    deleted_log = Log.query.get(log_id)

    if not logged_user:
        return jsonify({"description": "not user found"}, 404)
    if not deleted_log:
        return jsonify({"description": "not log found"}, 404)

    user_id = deleted_log.user_id
    searched_user = User.query.get(user_id)

    if logged_user != searched_user:
        if not logged_user.is_administrator():
            return jsonify({"description": "Unauthorized"}), 401

    db.session.delete(deleted_log)
    db.session.commit()

    return jsonify({"description": f"log deleted"}), 200
