from flask import Flask

from routes.auth import auth
from routes.querys import querys
from routes.users import users
from routes.views import views

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI
from utils.db import db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://ai.fburon.cl", "https://qai.fburon.cl"]}})

# settings
app.secret_key = 'mysecret'
print(DATABASE_CONNECTION_URI)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_CONNECTION_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# no cache
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(querys)
app.register_blueprint(users)
app.register_blueprint(views)
