from utils.db import db
import datetime
import pytz
chile_tz = pytz.timezone('America/Santiago')

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=True)
    password = db.Column(db.String, nullable=False)

class LogoutToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

class Requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String, nullable=False)

class Preguntas(db.Model):
    id = db.Column(db.String, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    deleted = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, id, user_id, deleted):
        self.id = id
        self.user_id = user_id
        self.deleted = deleted
        self.date = datetime.datetime.now(pytz.utc).astimezone(chile_tz)

    def __repr__(self):
        return f'<Pregunta {self.id}>'
