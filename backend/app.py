from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pytz
import json
import chat.functions as chat
from sqlalchemy.ext.declarative import DeclarativeMeta
import os, jwt, bcrypt, datetime
from functools import wraps
import logging 
from werkzeug.exceptions import Unauthorized
import time

logging.basicConfig(level=logging.DEBUG , format='%(asctime)s - %(levelname)s - %(message)s')
chile_tz = pytz.timezone('America/Santiago')
def get_user_id():
    token = request.headers.get('X-Auth-Token')
    if not token:
        logging.info("Missing authorization header")
        raise Unauthorized('Missing authorization header')
    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
        usuario_id = payload.get('id')
        if usuario_id is None:
            raise Unauthorized('Invalid authorization token')
        return usuario_id
    except jwt.exceptions.DecodeError:
        raise Unauthorized('Invalid authorization token')

def monitoring(response):
    fecha = datetime.datetime.utcnow()
    try:
        usuario_id = get_user_id()
    except Unauthorized:
        usuario_id = -1
    accion = request.endpoint if request.endpoint else 'None'
    metodo = request.method if request.method else 'None'
    if metodo == 'OPTIONS':
        return response
    status = str(response.status_code) if response.status_code else 400
    size = len(response.data) if response.data else 0

    # Guardar la solicitud en la base de datos
    solicitud = Requests(date=fecha, user_id=usuario_id, action=accion, method=metodo, status=status, size=size)
    db.session.add(solicitud)
    db.session.commit()

    return response

def token_admin():
    payload = {
        "resource": {"dashboard": 4},
        "params": {
            
        },
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
        }
    token = jwt.encode(payload, os.environ["METABASE_SECRET_KEY"], algorithm="HS256")
    iframeUrl = os.environ["METABASE_SITE_URL"] + "/embed/dashboard/" + token + "#theme=night&bordered=true&titled=true"

    return iframeUrl

def store_conversation_id(conversation_id, current_id):
    try:
        conversation = Preguntas.query.filter_by(id=conversation_id).first()
        if conversation:
            return
        conversation = Preguntas(id=conversation_id, user_id=current_id, deleted=False)
        db.session.add(conversation)
        db.session.commit()
    except Exception as e:
        logging.error(e)

def login_check(data):
    if not data:
        logging.debug("No data received")
        return jsonify({"error": "No data received"}), 400
    if not data.get('username') or not data.get('password'):
        logging.debug("Missing data")
        return jsonify({"error": "Missing data"}), 400
    username = Users.query.filter_by(username=data.get('username')).first()
    if not username:
        logging.debug("User not found")
        return jsonify({"error": "User not found"}), 404
    logging.debug("User found")
    if bcrypt.checkpw(data.get('password').encode('utf-8'),username.password.encode('utf-8')):
        token = jwt.encode({
            'id': username.id, 
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=int(os.environ['EXPIRE_TIME']))},
                os.environ['SECRET_KEY'])  
        return jsonify({"token": token, "username":username.username}), 200
    else:
        return jsonify({"error": "Incorrect Password"}), 400

def register_check(data):
    if not data:
        return jsonify({"error": "No data received"}), 400
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing data"}), 400
    username = Users.query.filter_by(username=data.get('username')).first()
    if username:
        return jsonify({"error": "User already exists"}), 400
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(data.get('password').encode('utf-8'), salt)
    new_user = Users(username=data.get('username'), password=hashed_password.decode('utf-8'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

def get_users_list():
    users = Users.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['questions'] = Preguntas.query.filter_by(user_id=user.id).count()
        if user.id == -1 or user.id == 1:
            continue
        output.append(user_data)
    # Ordenar por cantidad de preguntas
    output.sort(key=lambda x: x['questions'], reverse=True)
    return jsonify({'users': output}), 200

def delete_user_check(id):
    
    if not id:
        return jsonify({"error": "No data received"}), 400
    user = Users.query.filter_by(id=id).first()

    
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.id == 1:
        return jsonify({"error": "You can't delete the admin user"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

def black_list_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        blocked_token = None
        if 'x-auth-token' in request.headers:
            blocked_token = request.headers['x-auth-token']
        if not blocked_token:
            return jsonify({'message': 'You are not loged in'}), 401
        try:
            blocked = LogoutToken(
                token=blocked_token,
                date=datetime.datetime.utcnow()
            )
            db.session.add(blocked)
            db.session.commit()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Could not sign out', 'error': str(e)}), 401
    return decorated

def user_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'X-Auth-Token' in request.headers:
            token = request.headers['X-Auth-Token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        if token in db.session.query(LogoutToken.token).all():
            return jsonify({'message': 'Token is blocked'}), 401
        try:
            data = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
            current_user = Users.query.filter_by(id=data['id']).first()
        except Exception as e:
            return jsonify({'message': 'Invalid Token', 'error': str(e)}), 401

        return f(*args,  **kwargs)

    return decorator

def admin_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'X-Auth-Token' in request.headers:
            token = request.headers['X-Auth-Token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        if token in db.session.query(LogoutToken.token).all():
            return jsonify({'message': 'Token is blocked'}), 401
        try:
            data = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
            current_user = Users.query.filter_by(id=data['id']).first()
            if current_user.username != os.environ['ADMIN_ACCOUNT']:
                return jsonify({'message': 'Admin rights required'}), 401
        except Exception as e:
            return jsonify({'message': 'Invalid Token', 'error': str(e)}), 401

        return f(*args,  **kwargs)

    return decorator

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://ai.fburon.cl", "https://qai.fburon.cl"]}})
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
database = os.getenv('POSTGRES_DB')
app.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql+psycopg2://{user}:{password}@{host}/{database}'
# initialize the app with the extension
db.init_app(app)

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


with app.app_context():
    db.create_all()
    if not Users.query.filter_by(username=os.environ['ADMIN_ACCOUNT']).first():
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(os.environ['ADMIN_PASSWORD'].encode('utf-8'), salt)
        db.session.add(Users(username=os.environ['ADMIN_ACCOUNT'],
                               password=hashed_password.decode('utf-8'),))
    if not Users.query.filter_by(username="not user").first():
        db.session.add(Users(id=-1,username="not user",
                               password=1,))        
    db.session.commit()

@app.route('/')
def hello_world():
    return "<h1>This is a REST API</h1>"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    answer = login_check(data)
    return answer

@app.route('/logout', methods=['POST'])
@black_list_token
def logout():
    return {'message': 'Logout successful'}

@app.route('/register', methods=['POST'])
@admin_token
def register():
    data = request.get_json()
    answer = register_check(data)
    return answer


@app.route('/change-password', methods=['PUT'])
@user_token
def change_password():
    data = request.get_json()
    user = Users.query.filter_by(id=get_user_id()).first()
    password = data['password']

    if not password:
        return jsonify({"error": "Missing data"}), 400
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Wrong password"}), 400
    
    new_password = data['new_password']
    if not new_password:
        return jsonify({"error": "Missing data"}), 400
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    user.password = hashed_password.decode('utf-8')
    db.session.commit()

    return {'message': 'Password changed successfully'}, 200

@app.route('/users', methods=['GET'])
@admin_token
def get_users():
    data = get_users_list()
    return data

@app.route('/delete-user', methods=['POST'])
@admin_token
def delete_user():
    if not request.json:
        return jsonify({"error": "Missing data"}), 400
    else:
        id = request.json['id']
        if not id:
            return jsonify({"error": "Missing data"}), 400
        else:
            answer = delete_user_check(id)
            return answer

@app.route('/check-login', methods=['GET'])
@user_token
def check():
    return {'message': 'Check successful'}, 200

@app.route('/conversations', methods=['GET'])
@user_token
def get_conversations():
    data=chat.gpt_conversations()
    # Filter conversations by user
    user_id = get_user_id()
    if user_id != 1:
        conversation = []
        for conv in data['items']:
            user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
            if conv['id'] in [c.id for c in user_conversations]:
                conversation.append(conv)
        data['items'] = conversation
    return data, 200
@app.after_request
def monitor_messages(response):
    return monitoring(response)

@app.route('/messages/<conversation_id>', methods=['GET'])
@user_token
def get_messages(conversation_id):
    user_id = get_user_id()
    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
        if conversation_id not in [c.id for c in user_conversations]:
            return jsonify({"error": "Not allowed"}), 403
    if not conversation_id:
        return jsonify({"error": "Missing data"}), 400
    else:
        data=chat.gpt_conversation(conversation_id)
        return data, 200

@app.route('/messages', methods=['POST'])
@user_token
def send_message():
    user_id = get_user_id()
    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
        if request.json['conversation_id'] not in [c.id for c in user_conversations]:
            return jsonify({"error": "Not allowed"}), 403
    if not request.json:
        return jsonify({"error": "Missing data"}), 400
    else:
        conversation_id = request.json['conversation_id']
        parent_message_id = request.json['parent_message_id']
        message = request.json['message']
        def send_data(line):
            response = make_response(line + b'\n')
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['X-Accel-Buffering'] = 'no'
            return response
        chat.gpt_response(conversation_id, parent_message_id, message, send_data)
        return jsonify({"message":"Procesamiento completo."}), 200

@app.route('/metabase', methods=['GET'])
@admin_token
def get_metabase():
    data = token_admin()
    return jsonify({"url":data}), 200

@app.route('/change-title', methods=['PUT'])
@user_token
def change_title():
    user_id = get_user_id()
    if user_id != 1:
        user_conversations = Preguntas.query.filter_by(user_id=user_id).all()
        if request.json['conversation_id'] not in [c.id for c in user_conversations]:
            return jsonify({"error": "Not allowed"}), 403
    if not request.json:
        return jsonify({"error": "Missing data"}), 400
    else:
        conversation_id = request.json['conversation_id']
        title = request.json['title']
        chat.gpt_change_title(conversation_id, title)
    return {'message': 'Change title successful'}, 200

@app.route('/conversations', methods=['POST'])
@user_token
def new_conversation():
    try:
        current_id = get_user_id()
        if not request.json:
            return jsonify({"error": "Missing data"}), 400
        else:
            message = request.json['message']
            def send_data(line):
                response = make_response(line + b'\n')
                response.headers['Content-Type'] = 'text/plain'
                response.headers['Cache-Control'] = 'no-cache'
                response.headers['X-Accel-Buffering'] = 'no'
                return response
            chat.gpt_new_conversation(message, send_data, store_conversation_id, current_id)
            return jsonify({"message":"Procesamiento completo."}), 200
    except Exception as e:
        logging.exception(e)
        return jsonify({"error": "Error processing request"}), 500

@app.route('/conversations/<conversation_id>', methods=['DELETE'])
@user_token
def delete_conversation(conversation_id):
    if not conversation_id:
        return jsonify({"error": "Missing data"}), 400
    else:
        chat.gpt_delete_conversation(conversation_id)
        conversation = Preguntas.query.filter_by(id=conversation_id).first()
        db.session.delete(conversation)
        db.session.commit()

    return {'message': 'Delete conversation successful'}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=False, port=5000)