import os
import random
from datetime import datetime, timedelta, date
from flask import jsonify
from flask_jwt_extended import create_access_token
from faker import Faker
from src.database import db
from src.models.user import User
from src.models.log import Log
from src.models.mood import Mood
from src.models.sleep import Sleep
from src.models.feel import Feel
from src.models.description import Description
from src.bcrypt import bcrypt

DEMO_START_DATE = date(2024, 1, 1)

MOOD_NAMES  = {-2: "Very Sad", -1: "Sad", 0: "Neutral", 1: "Happy", 2: "Very Happy"}
SLEEP_NAMES = {0: "0-2 hours", 1: "3-4 hours", 2: "5-6 hours", 3: "7-8 hours", 4: "9+ hours"}

MOOD_FEELS = {
    2:  ["Joyful", "Grateful", "Excited", "Optimistic", "Confident", "Hopeful"],
    1:  ["Content", "Hopeful", "Calm", "Motivated", "Peaceful", "Grateful"],
    0:  ["Calm", "Content", "Restless", "Tired", "Hopeful"],
    -1: ["Down", "Lonely", "Disappointed", "Tired", "Anxious", "Irritable"],
    -2: ["Down", "Overwhelmed", "Anxious", "Stressed", "Lonely", "Irritable"],
}

MOOD_SLEEP = {
    2:  [3, 3, 4],
    1:  [2, 3, 3],
    0:  [1, 2, 3],
    -1: [0, 1, 2],
    -2: [0, 0, 1],
}

MOOD_DESCRIPTIONS = {
    2: [
        "Had a fantastic day! Everything went smoothly.",
        "Feeling on top of the world today.",
        "Great time with friends — lots of laughs and good energy.",
        "Productive day and feeling really accomplished.",
        "One of those days where everything just clicks.",
    ],
    1: [
        "Pretty good day overall. Managed to get things done.",
        "Feeling positive today — had a nice walk outside.",
        "Nice and steady day. Content with how things went.",
        "Had a good workout, feeling energized.",
        "Solid day. Small wins add up.",
    ],
    0: [
        "Just an average day. Nothing special.",
        "Got through the day. Feeling okay.",
        "Neither good nor bad, just existing.",
        "Routine day, nothing much to note.",
        "A bit flat today but that's okay.",
    ],
    -1: [
        "Tough day. Feeling a bit low.",
        "Struggling a bit today. Hard to stay motivated.",
        "Not feeling great. Hope tomorrow is better.",
        "Had some difficult moments today.",
        "Tired and a little off. Need rest.",
    ],
    -2: [
        "Really rough day. Feeling overwhelmed.",
        "Everything feels heavy today.",
        "Hard to get out of bed. Needed some alone time.",
        "Feeling completely drained.",
        "One of those hard days. Just getting through it.",
    ],
}

fake = Faker()


def _generate_log_dates(rng):
    end = date.today() - timedelta(days=1)
    log_dates = []
    current = DEMO_START_DATE + timedelta(days=rng.randint(0, 14))

    phase_config = {
        "inactive": {"log_chance": 0.0,  "duration": (5, 10)},
        "low":      {"log_chance": 0.2,  "duration": (5, 14)},
        "medium":   {"log_chance": 0.45, "duration": (5, 14)},
        "high":     {"log_chance": 0.75, "duration": (3, 10)},
    }

    while current <= end:
        phase = rng.choices(
            ["inactive", "low", "medium", "high"],
            weights=[15, 35, 35, 15]
        )[0]
        cfg = phase_config[phase]
        duration = rng.randint(*cfg["duration"])

        for _ in range(duration):
            if current > end:
                break
            if cfg["log_chance"] > 0 and rng.random() < cfg["log_chance"]:
                log_dates.append(datetime.combine(current, datetime.min.time()))
            current += timedelta(days=1)

    # ensure at least 20 logs per month (proportional for partial months)
    existing_days = {d.date() for d in log_dates}
    month_start = DEMO_START_DATE.replace(day=1)
    while month_start <= end:
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        month_end = min(next_month - timedelta(days=1), end)

        days_in_range = (month_end - month_start).days + 1
        minimum = min(20, days_in_range)
        month_logs = [d for d in existing_days if month_start <= d <= month_end]
        deficit = minimum - len(month_logs)

        if deficit > 0:
            available = [
                month_start + timedelta(days=i)
                for i in range(days_in_range)
                if month_start + timedelta(days=i) not in existing_days
            ]
            for d in rng.sample(available, min(deficit, len(available))):
                existing_days.add(d)
                log_dates.append(datetime.combine(d, datetime.min.time()))

        month_start = next_month

    log_dates.sort()
    return log_dates


def create_demo_account():
    rng = random.Random()
    email = fake.unique.email()
    password = fake.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
        user_email=email,
        user_password=hashed_pw,
        user_name=fake.first_name(),
        is_admin=False,
        is_demo=True,
    )
    db.session.add(user)
    db.session.flush()

    log_data = []
    for day in _generate_log_dates(rng):
        mood_scale = rng.choices([-2, -1, 0, 1, 2], weights=[5, 15, 25, 35, 20])[0]
        log_data.append({
            "created_at": day.replace(hour=rng.choice([7, 8, 9, 19, 20, 21, 22]), minute=rng.randint(0, 59), second=0, microsecond=0),
            "mood_scale": mood_scale,
            "sleep_scale": rng.choice(MOOD_SLEEP[mood_scale]),
            "feels": rng.sample(MOOD_FEELS[mood_scale], rng.randint(2, min(4, len(MOOD_FEELS[mood_scale])))),
            "description": rng.choice(MOOD_DESCRIPTIONS[mood_scale]),
        })

    logs = [Log(user_id=user.user_id, created_at=d["created_at"]) for d in log_data]
    db.session.add_all(logs)
    db.session.flush()

    for log, data in zip(logs, log_data):
        mood_scale = data["mood_scale"]
        db.session.add(Mood(log_id=log.log_id, mood_scale=mood_scale, mood_name=MOOD_NAMES[mood_scale]))
        db.session.add(Sleep(log_id=log.log_id, sleep_time_scale=data["sleep_scale"], sleep_time_name=SLEEP_NAMES[data["sleep_scale"]]))
        db.session.add(Description(log_id=log.log_id, description=data["description"]))
        for feel_name in data["feels"]:
            db.session.add(Feel(log_id=log.log_id, feel_name=feel_name))

    db.session.commit()

    access_token = create_access_token(identity=str(user.user_id))
    return jsonify({
        "message": "Demo login successful",
        "access_token": access_token,
        "user_name": user.user_name,
        "user_email": user.user_email,
    }), 200


def delete_demo_account(user):
    logs = Log.query.filter_by(user_id=user.user_id).all()
    for log in logs:
        Feel.query.filter_by(log_id=log.log_id).delete()
        Mood.query.filter_by(log_id=log.log_id).delete()
        Sleep.query.filter_by(log_id=log.log_id).delete()
        Description.query.filter_by(log_id=log.log_id).delete()
    Log.query.filter_by(user_id=user.user_id).delete()
    db.session.delete(user)
    db.session.commit()
