# mood-tracking
REST API for simple mood tracking application

## DESCRIPTION
A simple mood tracking app for:
- controlling sleep time,
- check your daily mood,
- add daily feels,
- write information about day,
- everyday reflection feedback

DataBases:
Users
-e-mail
-password
-user id
-image
-role

Logs
- log id
- created date
- user id (foreign key)

Mood
-mood id
-mood
-log id (foreign key)

Feeling
-feeling id
-feel 
-log id (foreign key)

DayDescription
-day-description id
-information
- log id (foreign key)

Sleep
-sleep id
-sleep time
-log id (foreign key)

Tracker
Command:

Mood
POST - add mood -user premmision
GET - show all moods from user (11 days)  - user premmision
GET - show all moods (11 days) - admin premission
GET + ID - show selected task with specific IT (for admin all user, from user only his)
PUT _ ID - change mood (for admin all user, from user only his)
DELETE + ID - delete selected task (for admin all user, from user only his)

User
POST - register new user - user and admin premmision
GET - show all users - admin premission
GET + me - show information about currently user - user premmision
GET + ID - show information about selectrd user - admin premmision
PUT change information - user premmision
DELETE me - delete currently user - user premmision 
DELETE + ID - delete selected user - admin premmision

## How to Set Up Project

create virtual env

`python -m venv .venv`

activate virtual env

```
# windows (cmd)
.\.venv\Scripts\activate.bat

# windows (PowerShell)
.\.venv\Scripts\activate.ps1

# macos, linux
source .venv/bin/activate
```

install project dependencies

`pip install .`

## How to run server

you can start flask application by several different way:

run as python script

`python src/app.py`

run with flask

`python -m flask --app src/app/app.py run --host 0.0.0.0 --port 8080`

run with flask (with debug & autoreload)

`python -m flask --app src/app/app.py --debug run --host 0.0.0.0 --port 8080`
