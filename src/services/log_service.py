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

def add_mood_name(mood_scale):
    if mood_scale == -2:
        return "Very Sad"
    elif mood_scale == -1:
        return "Sad"
    elif mood_scale == 0:
        return "Neutral"
    elif mood_scale == 1:
        return "Happy"
    elif mood_scale == 2:
        return "Very Happy"

def add_sleep_time(sleep_time_scale):
    if sleep_time_scale == 0:
        return "0-2 hours"
    elif sleep_time_scale == 1:
        return "3-4 hours"
    elif sleep_time_scale == 2:
        return "5-6 hours"
    elif sleep_time_scale == 3:
        return "7-8 hours"
    elif sleep_time_scale == 4:
        return "9+ hours"
def get_all_logs():
    logged_user = get_current_user()
    if not logged_user:
        return jsonify({"description": "not user found"})
    if not logged_user.is_administrator():
        return jsonify({"description": "Unauthorized"}), 401
    logs = Log.query.all()
    logs_dict = [log.to_dict() for log in logs]
    return (logs_dict, 200)

def get_all_user_logs(user_id):
    logged_user = get_current_user()
    if not logged_user:
        return jsonify({"description": "not user found"})
    if not logged_user.is_administrator():
        return jsonify({"description": "Unauthorized"}), 401
    user_logs = Log.query.filter_by(user_id=int(user_id))
    logs_dict = [log.to_dict() for log in user_logs]
    for log_dict in logs_dict:
        moods = Mood.query.filter_by(log_id = log_dict["log_id"])
        mood_to_dict = moods[0].to_dict()
        log_dict["mood"] = mood_to_dict

        all_feels = Feel.query.filter_by(log_id = log_dict["log_id"])
        feels_to_dict = [feels.to_dict() for feels in all_feels]
        log_dict["feels"] = feels_to_dict

        times_sleep = Sleep.query.filter_by(log_id = log_dict["log_id"])
        times_to_dict = times_sleep[0].to_dict()
        log_dict["sleep"] = times_to_dict

        descriptions = Description.query.filter_by(log_id = log_dict["log_id"])
        description_to_dict = descriptions.to_dict()
        log_dict["description"] = description_to_dict
    print(logs_dict)
    return (logs_dict, 200)

def get_all_me_logs():
    logged_user = get_current_user()
    if not logged_user:
        return jsonify({"description": "not user found"})
    print(logged_user)
    user_logs = Log.query.filter_by(user_id=logged_user.user_id)
    logs_dict = [log.to_dict() for log in user_logs]
    for log_dict in logs_dict:
        moods = Mood.query.filter_by(log_id=log_dict["log_id"])
        mood_to_dict = moods[0].to_dict()
        log_dict["mood"] = mood_to_dict

        all_feels = Feel.query.filter_by(log_id=log_dict["log_id"])
        feels_to_dict = [feels.to_dict() for feels in all_feels]
        log_dict["feels"] = feels_to_dict

        times_sleep = Sleep.query.filter_by(log_id=log_dict["log_id"])
        times_to_dict = times_sleep[0].to_dict()
        log_dict["sleep"] = times_to_dict

        descriptions = Description.query.filter_by(log_id=log_dict["log_id"])
        description_to_dict = descriptions[0].to_dict()
        log_dict["description"] = description_to_dict
    print(logs_dict)
    return (logs_dict, 200)




def create_log(feels, mood_scale, sleep_time_scale, description):
    logged_user = get_current_user()
    mood_name = add_mood_name(mood_scale)
    sleep_time_name = add_sleep_time(sleep_time_scale)

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
        mood_scale=mood_scale,
        mood_name=mood_name
    )
    db.session.add(new_mood)
    db.session.commit()

    new_sleep = Sleep(
        log_id=new_log.log_id,
        sleep_time_scale=sleep_time_scale,
        sleep_time_name=sleep_time_name
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

    return jsonify({"new_log": new_log.to_dict(), "new_mood": new_mood.to_dict(),"new_feels": feels, "new_sleep":new_sleep.to_dict(), "new_description": new_description.to_dict()}, 200)


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

    if "mood_scale" in data.keys():
        mood_name = add_mood_name(data["mood_scale"])
        current_mood = Mood.query.filter_by(log_id=log_id).first()
        current_mood.mood_scale: object = data["mood_scale"]
        current_mood.mood_name: object = mood_name
        db.session.commit()
        new_log_information["mood"] = current_mood.to_dict()

    if "sleep_time_scale" in data.keys():
        sleep_time_name = add_sleep_time(data["sleep_time_scale"])
        current_sleep = Sleep.query.filter_by(log_id=log_id).first()
        current_sleep.sleep_time_scale = data["sleep_time_scale"]
        current_sleep.sleep_time_name = sleep_time_name

        db.session.commit()
        new_log_information["sleep"] = current_sleep.to_dict()

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
