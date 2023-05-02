from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from models.contact import Users, Preguntas, Requests, LogoutToken
from utils.db import db
from werkzeug.exceptions import Unauthorized
import logging 
import os, jwt, bcrypt, datetime
import time
from functools import wraps
import chat.functions as chat

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
