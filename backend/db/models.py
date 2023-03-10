import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(256), nullable=False)
    def __repr__(self):
        return '<Users %r>' % self.name

class LogoutToken(db.Model):
    __tablename__ = 'logout_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(256), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return '<LogoutToken %r>' % self.token

def to_dict(obj):
    if isinstance(obj.__class__, DeclarativeMeta):
        # an SQLAlchemy class
        fields = {}
        for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
            data = obj.__getattribute__(field)
            try:
                json.dumps(data)  # this will fail on non-encodable values, like other classes
                if data is not None:
                    fields[field] = data
            except TypeError:
                pass
        # a json-encodable dict
        return fields