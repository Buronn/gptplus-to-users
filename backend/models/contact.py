from utils.db import db
from sqlalchemy import Enum as SQLAlchemyEnum

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
    title = db.Column(db.String, nullable=True, default="Untitled")
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.String, db.ForeignKey('preguntas.id'))
    role = db.Column(SQLAlchemyEnum('system', 'user', 'assistant', name='role_enum'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    pregunta = db.relationship('Preguntas', backref=db.backref('messages', lazy=True))

class Tokens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.String, db.ForeignKey('preguntas.id'))
    token = db.Column(db.Integer, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    pregunta = db.relationship('Preguntas', backref=db.backref('tokens', lazy=True))