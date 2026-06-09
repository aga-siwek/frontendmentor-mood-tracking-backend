#!/usr/bin/env python3
"""
Seed script: creates 5 demo users with irregular mood logs spanning 2025-2026.
Run: python seed_db.py
"""

import sys
import os
import random
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from faker import Faker
from app import app
from src.database import db
from src.models.user import User
from src.models.log import Log
from src.models.mood import Mood
from src.models.sleep import Sleep
from src.models.feel import Feel
from src.models.description import Description
from src.bcrypt import bcrypt

NUM_USERS = 5
# One user per start year — shuffled so order is random each run
USER_START_YEARS = [2020, 2024, 2025, 2025, 2026]
random.shuffle(USER_START_YEARS)

MOOD_NAMES  = {-2: "Very Sad", -1: "Sad", 0: "Neutral", 1: "Happy", 2: "Very Happy"}
SLEEP_NAMES = {0: "0-2 hours", 1: "3-4 hours", 2: "5-6 hours", 3: "7-8 hours", 4: "9+ hours"}

ALL_FEELS = [
    "Joyful", "Down", "Anxious", "Calm", "Excited", "Lonely", "Grateful",
    "Overwhelmed", "Motivated", "Irritable", "Peaceful", "Tired", "Hopeful",
    "Confident", "Stressed", "Content", "Disappointed", "Optimistic", "Restless",
]

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
        "So much positive energy today, I love it.",
    ],
    1: [
        "Pretty good day overall. Managed to get things done.",
        "Feeling positive today — had a nice walk outside.",
        "Nice and steady day. Content with how things went.",
        "Had a good workout, feeling energized.",
        "Solid day. Small wins add up.",
        "Things are going well. Grateful for that.",
    ],
    0: [
        "Just an average day. Nothing special.",
        "Got through the day. Feeling okay.",
        "Neither good nor bad, just existing.",
        "Routine day, nothing much to note.",
        "A bit flat today but that's okay.",
        "Meh kind of day. Tomorrow might be better.",
    ],
    -1: [
        "Tough day. Feeling a bit low.",
        "Struggling a bit today. Hard to stay motivated.",
        "Not feeling great. Hope tomorrow is better.",
        "Had some difficult moments today.",
        "Tired and a little off. Need rest.",
        "Everything felt like an effort today.",
    ],
    -2: [
        "Really rough day. Feeling overwhelmed.",
        "Everything feels heavy today.",
        "Hard to get out of bed. Needed some alone time.",
        "Feeling completely drained.",
        "One of those hard days. Just getting through it.",
        "Couldn't shake the dark mood today.",
    ],
}

fake = Faker()


def clear_all_tables():
    Feel.query.delete()
    Mood.query.delete()
    Sleep.query.delete()
    Description.query.delete()
    Log.query.delete()
    User.query.delete()
    db.session.commit()
    print("All tables cleared.")


def generate_irregular_dates(rng, start_date):
    """Generates irregular log dates from start_date to yesterday.

    Simulates real usage: active phases (5-20 days of logging)
    separated by inactive gaps (10-50 days of nothing).
    """
    end = date.today() - timedelta(days=1)
    log_dates = []

    current = start_date + timedelta(days=rng.randint(0, 30))

    while current <= end:
        # Active phase: log most days for a stretch
        active_length = rng.randint(5, 20)
        for _ in range(active_length):
            if current > end:
                break
            if rng.random() > 0.2:  # 80% chance of logging on any given active day
                log_dates.append(datetime.combine(current, datetime.min.time()))
            current += timedelta(days=1)

        # Inactive gap: stop logging for a while
        current += timedelta(days=rng.randint(10, 50))

    return log_dates


def seed_user(index, start_year):
    rng = random.Random()

    name = fake.name()
    email = fake.unique.email()
    password = fake.password(length=16, special_chars=False, digits=True, upper_case=True, lower_case=True)

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(user_email=email, user_password=hashed_pw, user_name=name, is_admin=False)
    db.session.add(user)
    db.session.flush()

    start_month = 1 if start_year == 2026 else rng.randint(1, 10)
    start_date = date(start_year, start_month, 1)
    log_days = generate_irregular_dates(rng, start_date)

    for day in log_days:
        mood_scale = rng.choices([-2, -1, 0, 1, 2], weights=[5, 15, 25, 35, 20])[0]
        sleep_scale = rng.choice(MOOD_SLEEP[mood_scale])

        feel_pool = MOOD_FEELS[mood_scale]
        feels = rng.sample(feel_pool, rng.randint(2, min(4, len(feel_pool))))

        description = rng.choice(MOOD_DESCRIPTIONS[mood_scale])

        hour = rng.choice([7, 8, 9, 19, 20, 21, 22])
        log_time = day.replace(hour=hour, minute=rng.randint(0, 59), second=0, microsecond=0)

        new_log = Log(user_id=user.user_id, created_at=log_time)
        db.session.add(new_log)
        db.session.flush()

        db.session.add(Mood(log_id=new_log.log_id, mood_scale=mood_scale, mood_name=MOOD_NAMES[mood_scale]))
        db.session.add(Sleep(log_id=new_log.log_id, sleep_time_scale=sleep_scale, sleep_time_name=SLEEP_NAMES[sleep_scale]))
        db.session.add(Description(log_id=new_log.log_id, description=description))
        for feel_name in feels:
            db.session.add(Feel(log_id=new_log.log_id, feel_name=feel_name))

    db.session.commit()
    print(f"  [{index:02d}] {name} <{email}> / {password} — {len(log_days)} logs (from {start_date})")
    return len(log_days)


def seed():
    with app.app_context():
        clear_all_tables()
        print(f"Seeding {NUM_USERS} users...\n")
        total_logs = sum(seed_user(i + 1, year) for i, year in enumerate(USER_START_YEARS))
        print(f"\nDone! {NUM_USERS} users, {total_logs} logs total.")


if __name__ == "__main__":
    seed()
